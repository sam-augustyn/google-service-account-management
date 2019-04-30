#!/usr/bin/env python3

from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64

def authenticate(apiName, apiVersion, apiScope):
    ''' Authenticate the user and returns a service object
    @apiName should be the name of the google api
    found here: https://developers.google.com/api-client-library/python/apis/
    @apiVerison should be the version of the api
    @apiScope should be the scope of the google api, this script uses OAuth2 Service Accounts
    found here: https://developers.google.com/identity/protocols/googlescopes '''

    #specify service account file (contains service account information)
    SERVICE_ACCOUNT_FILE = '../manager.json'
    #create a credentials object with the service account file and the specificed scope
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=apiScope)
    #build the service object
    service = build(apiName, apiVersion, credentials=credentials)
    #return the service object
    return service

''' ---GET METHODS--- '''
def getAllAccounts(service, projectName):
    ''' This gets all the service accounts associated with a projects
    It returns a dictionary of all the accounts
    @service, authenticated service object
    @projectName should be the name of the project '''

    #return all the accounts and their information in a dictionary
    return service.projects().serviceAccounts().list(name=projectName).execute()

def getServiceAccount(service, projectName, userName):
    ''' Gets details about a service account and returns info about the service account
    @service is the authenticated service account
    @projectName should be the name of the project
    @userName should be the name of the service account'''

    #return the service account information
    return service.projects().serviceAccounts().get(name=getFullEmail(projectName, userName)).execute()

def getServiceKeys(service, projectName, userName):
    ''' Returns a dictionary of all the service keys for a service account on a project
    @service is the service object
    @projectName is the name of the project
    @userName is the name of the user'''

    #return dictionary witha all of the keys
    return service.projects().serviceAccounts().keys().list(name=getFullEmail(projectName, userName)).execute()

def getServiceEmail(projectName, userName):
    ''' Generates the service email with the specified service account
    @projectName should be the name of the project
    @userName should be the name of the service account '''

    #return a string with the email of the service account
    return userName + "@" + projectName + ".iam.gserviceaccount.com"

def getProjectName(projectName):
    ''' Generate the project name
    @projectName should be the name of the project '''

    #return a string that is the project name
    return "projects/" + projectName

def getFullEmail(projectName, userName):
    ''' Generates the full email used for api calls
    @projectName should be the name of the project
    @userName should be the name of the service account '''

    #return the string with the full email used for api calls
    return getProjectName(projectName) + '/serviceAccounts/' + getServiceEmail(projectName, userName)

''' ---CREATE METHODS--- '''
def createServiceAccount(service, projectName, userName):
    ''' This method creates a service account in the specified project with the specified name
    and returns the service account that was created
    @service, authenitcated service object
    @projectName should be the name of the project
    @userName should be the name of the new service account '''

    #request body for the create account method
    request_body = {"serviceAccount": {"displayName": userName,},"accountId": userName}
    #return the newly created service account
    return service.projects().serviceAccounts().create(name=generateProjectName(projectName), body=request_body).execute()

def createServiceKey(service, serviceAccount):
    ''' Generate a private key for a service account and writes json in the current working directory
    @service, authenticated service object
    @serviceAccount should the service account info generated from the above methods '''

    #call the api to generate the service account key
    response = service.projects().serviceAccounts().keys().create(name=serviceAccount['name'],
    body={"privateKeyType":"TYPE_GOOGLE_CREDENTIALS_FILE", "keyAlgorithm":"KEY_ALG_RSA_2048"}).execute()
    #open a file named <serviceAccount>.json in binary mode
    outfile = open(f"{serviceAccount['displayName']}.json", 'wb')
    #decode the response and write it to a file
    outfile.write(base64.b64decode(response['privateKeyData']))
    #close the file
    outfile.close()

''' ---DELETION METHODS---'''
def removeServiceAccount(service, projectName, userName):
    ''' Removes the specified service account
    @service is the authenticated service account
    @projectName should be the name of the project
    @userName should be the name of the service account '''

    #call the api to delete the specified service account
    service.projects().serviceAccounts().delete(name=getFullEmail(projectName, userName)).execute()

def removeServiceKey(service, key):
    ''' Removes a specified key'''
    service.projects().serviceAccounts().keys().delete(name=key)

def main():
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
    apiName = 'iam'
    apiVersion = 'v1'
    projectName = 'samaugustynbackup'

    service = authenticate(apiName, apiVersion, SCOPES)

    #removeServiceKey(service, getServiceKeys(service, projectName, 'manager').get('keys')[1]['name'])

if __name__ == "__main__": main()
