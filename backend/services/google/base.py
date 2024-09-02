from google.oauth2.service_account import Credentials

class Google:
    def __init__(self):
        self.creds = self.authenticate_google()

    def authenticate_google(self):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]     
        creds = Credentials.from_service_account_file('./credentials/service_account.json', scopes=scopes)
        
        return creds
