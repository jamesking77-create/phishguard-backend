import imapclient
import smtplib

def initialize_email_client(email, password):
    # Extract the domain from the email address
    domain = email.split('@')[1]

    # Determine the IMAP server based on the domain
    imap_servers = {
        'gmail.com': 'imap.gmail.com',
        'outlook.com': 'imap-mail.outlook.com',
        'hotmail.com': 'imap-mail.outlook.com',
        'yahoo.com': 'imap.mail.yahoo.com'
    }

    if domain == 'dummyserver.com':
        # Dummy SMTP server for testing
        class DummyIMAPClient:
            def login(self, email, password):
                print(f"Logged in with email: {email} and password: {password}")

            def logout(self):
                print("Logged out")

        return DummyIMAPClient()

    server_address = imap_servers.get(domain)
    if not server_address:
        # Attempt to guess the IMAP server for other domains
        server_address = f'imap.{domain}'

    try:
        server = imapclient.IMAPClient(server_address, ssl=True)
        server.login(email, password)
        return server
    except imapclient.exceptions.LoginError as e:
        raise imapclient.exceptions.LoginError(f"Failed to login to {server_address} with email: {email}. Error: {str(e)}")
