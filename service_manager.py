from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os.path

class ServiceManager:
    def __init__(self, credentials_file_path, token_file_path):
        self.__started_services_listing = [] #list of tuples containing (service name, version)
        self.__services = [] #list of services instances, the Resource objects
        self.__scopes = ['https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/spreadsheets']
        self.__my_credentials_json_file = credentials_file_path
        self.__token_file = token_file_path

    def authenticate(self):
        creds = None
        # if there is already a token (credentials) saved inside json, recall it
        if os.path.exists(self.__token_file):
            creds = Credentials.from_authorized_user_file(self.__token_file, self.__scopes)
        # is there is no valid credentials, start authorization flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # first, we create a flow object (contains methods to integrate OAuth with Google Authentication)
                flow = InstalledAppFlow.from_client_secrets_file(self.__my_credentials_json_file, self.__scopes)
                # next, using, authentication information from json file, we request a token, that is what Google API request for usage
                creds = flow.run_local_server(port=8080)
                # Save the credentials for the next run
                with open(self.__token_file, "w") as token:
                    token.write(creds.to_json())
        return creds

    def start_services(self):
        creds = self.authenticate()

        #drive_service = build('drive', 'v3', credentials=creds)

        sheets_service = build('sheets', 'v4', credentials=creds)

        # if drive_service:
        #     self.add_started_service('drive', 'v3', drive_service)
        if sheets_service:
            self.add_started_service('sheets', 'v4', sheets_service)

    def add_started_service(self, service_name, version, instance):
        key = (service_name, version)
        if key not in self.__started_services_listing:
            self.__started_services_listing.append(key)
            self.__services.append(instance)

    def get_service(self, service_name, version): #returns the service built (the Service object) from build() function
        if self.service_started(service_name, version):
            # get key from list of services
            key = None
            enumerated = enumerate(self.list_all_started_services())
            for k,v in enumerated:
                if v == (service_name, version):
                    key = k
            # return from the list of service instances the object allocated at correspondent key
            return self.__services[key]

    def service_started(self, service_name, version) -> bool:  #consult if service is in the list of started services
        key = (service_name, version)
        if key in self.__started_services_listing:
            return True
        else:
            return False

    def list_all_started_services(self):
        return self.__started_services_listing

    def get_scopes(self):
        return self.__scopes

    def set_scopes(self, scopes):
        self.__scopes = scopes

    def get_my_credentials_json_file(self):
        return self.__my_credentials_json_file

    def set_my_credentials_json_file(self, file_path):
        self.__my_credentials_json_file = file_path

    def get_token_file(self):
        return self.__token_file

    def set_token_file(self, file_path):
        self.__token_file = file_path