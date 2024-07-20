from flask import Flask, jsonify, session, request, redirect, url_for
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

# Disable OAuthlib's HTTPS verification when running locally.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
    return 'You are authenticated!'

@app.route('/authorize')
def authorize():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials
    session['credentials'] = pickle.dumps(creds)

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('credentials', None)
    return redirect(url_for('index'))

@app.route('/scan-emails', methods=['GET'])
def scan_emails():
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    creds = pickle.loads(session['credentials'])
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', q="is:unread").execute()
    messages = results.get('messages', [])

    malicious_emails = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        snippet = msg['snippet'].lower()
        headers = {header['name']: header['value'] for header in msg['payload']['headers']}
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown Sender')

        # Criteria for detecting malicious emails
        if (
            "update your account" in snippet or
            "immediate action required" in snippet or
            "your account will be suspended" in snippet or
            "click on the following link" in snippet or
            "malicious-link" in snippet or
            "request for personal or financial information" in snippet or
            "offer too good to be true" in snippet or
            "suspicious attachment" in snippet or
            "unknown sender" in snippet or
            "poor grammar and spelling" in snippet
        ):
            malicious_emails.append({
                'id': msg['id'],
                'snippet': msg['snippet'],
                'subject': subject,
                'sender': sender,
                'actions': {
                    'view': f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}",
                    'delete': f"http://localhost:5000/delete-email?id={msg['id']}",
                    'ignore': 'ignore'
                }
            })
           

    return jsonify({'malicious_emails': malicious_emails})

@app.route('/delete-email', methods=['POST'])
def delete_email():
    if 'credentials' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    email_id = request.args.get('id')
    creds = pickle.loads(session['credentials'])
    service = build('gmail', 'v1', credentials=creds)
    
    service.users().messages().delete(userId='me', id=email_id).execute()
    return jsonify({'status': 'Email deleted'})

if __name__ == '__main__':
    app.run(debug=True)
