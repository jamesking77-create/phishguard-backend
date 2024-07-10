import imapclient
from imapclient.exceptions import LoginError

def initialize_email_client(email, password):
    server = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    try:
        server.login(email, password)
        return server
    except LoginError as e:
        raise Exception(f"Login failed: {str(e)}")