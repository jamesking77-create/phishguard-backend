from flask import request, jsonify, current_app as app
from .email_clients import initialize_email_client
from .ml_model import load_ml_model
from .utils import check_inbox
import threading
import imapclient

email_client = None
ml_model = load_ml_model('models/phishing_detection_model.pkl', 'models/vectorizer.pkl')
threshold = 3

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global email_client
    data = request.json
    email = data['email']
    password = data['password']

    if email and password:
        try:
            email_client = initialize_email_client(email, password)
            threading.Thread(target=check_inbox, args=(email_client, ml_model, threshold)).start()
            return jsonify(success=True)
        except imapclient.exceptions.LoginError as e:
            return jsonify(success=False, error=str(e)), 401
    else:
        return jsonify(success=False, error="Email and password are required"), 400

@app.route('/scan_content', methods=['POST'])
def scan_content():
    data = request.json
    content = data['content']

    # Analyze the content using the ML model
    prediction = ml_model.predict([content])
    result = 'phishing' if prediction[0] == 'phishing' else 'not_phishing'
    
    return jsonify(result=result)
