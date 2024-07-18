import time
from imapclient import IMAPClient

def check_inbox(email_client, ml_model, threshold):
    
    while True:
        email_client.select_folder('INBOX')
        messages = email_client.search(['UNSEEN'])
        for msg_id in messages:
            msg = email_client.fetch(msg_id, ['BODY[]'])
            # Extract the email body and analyze it with the ML model
            body = msg[msg_id][b'BODY[]'].decode('utf-8')
            prediction = ml_model.predict([body])
            if prediction == 'phishing':
                email_client.move([msg_id], 'INBOX.Phishing')
        time.sleep(threshold * 60)  # Check every 'threshold' minutes
