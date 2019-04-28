from google.oauth2 import service_account
from googleapiclient.discovery import build
import json, re, base64

def authenticate(apiName, apiVersion, apiScope):
    ''' Authenticate the user and returns a service object
    @apiName should be the name of the google api
    found here: https://developers.google.com/api-client-library/python/apis/
    @apiVerison should be the version of the api
    @apiScope should be the scope of the google api, this script uses OAuth2 Service Accounts
    found here: https://developers.google.com/identity/protocols/googlescopes '''

    #specify service account file (contains service account information)
    SERVICE_ACCOUNT_FILE = 'manager.json'
    #create a credentials object with the service account file and the specificed scope
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=apiScope)
    #build the service object
    service = build(apiName, apiVersion, credentials=credentials)
    #return the service object
    return service

def createServiceAccount(service, projectName, userName):
    request_body = {"serviceAccount": {"displayName": userName,},"accountId": userName}
    return service.projects().serviceAccounts().create(name=projectName, body=request_body).execute()

def getAllAccounts(service, projectName):
    return service.projects().serviceAccounts().list(name=projectName).execute()

def getServiceAccount(service, projectName, userName):
    return service.projects().serviceAccounts().get(name=generateFullEmail(projectName, userName)).execute()

def generateServiceKey(service, serviceAccount):
    response = service.projects().serviceAccounts().keys().create(name=serviceAccount['name'],
    body={"privateKeyType":"TYPE_GOOGLE_CREDENTIALS_FILE", "keyAlgorithm":"KEY_ALG_RSA_2048"}).execute()
    outfile = open(f"{serviceAccount['displayName']}.json", 'wb')
    outfile.write(base64.b64decode(response['privateKeyData']))
    outfile.close()

def listServiceKey(service, userName, name, projectName):
    return service.projects().serviceAccounts().keys().list(name=name +
    '/serviceAccounts/' + userName + '@' + projectName + ".iam.gserviceaccount.com").execute()

def removeServiceAccount(service, projectName, userName):
    service.projects().serviceAccounts().delete(name=generateFullEmail(projectName, userName)).execute()

def generateServiceEmail(projectName, userName):
    return userName + "@" + projectName + ".iam.gserviceaccount.com"

def generateProjectName(projectName):
    return "projects/" + projectName

def generateFullEmail(projectName, userName):
    return generateProjectName(projectName) + '/serviceAccounts/' + generateServiceEmail(projectName, userName)

def main():
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
    apiName = 'iam'
    apiVersion = 'v1'
    projectName = 'samaugustynbackup'

    service = authenticate(apiName, apiVersion, SCOPES)
    removeServiceAccount(service, 'samaugustynbackup', 'drive1')
    #generateServiceKey(service, createServiceAccount(service, projectName, 'drive1'))
    #print(getServiceAccount(service, 'samaugustynbackup', 'drive1'))


if __name__ == "__main__": main()
