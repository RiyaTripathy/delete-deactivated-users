# import python modules

import csv
import configparser
import requests
import urllib3
import pandas as pd


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read the config file to retrieve url, token and filename
config = configparser.ConfigParser()
config.read('okta-config.txt')
url = config.get('General', 'url')
token = config.get('General', 'token')

#function to delete the deactivated users


def deleteDeactivatedUsers (userid,login):

    res = requests.delete(url + '/api/v1/users/'+userid,headers={'Accept': 'application/json', 'Content-Type': 'application/json','Authorization': 'SSWS ' + token},verify=False)

    # Check the status code of the response for success and failure
    if res.status_code == 204:
        # Add the login of the deleted user to a file for record
        with open('UserDeleted.txt', 'a') as f:
            f.write(login + '\n')
    # Add the userid and error summary of the users not deleted to a csv file for record
    else:
        with open('UserNotDeleted.csv', mode='a') as f:
            response=res.json()
            error = str(response['errorCauses'])
            writer = csv.writer(f, delimiter=',')
            writer.writerow([login, error[19:-3]])
    return res.status_code

# Funtion to get the list of deactivated users in Okta


def getDeactivatedUsers():
    # Get all deactivated user list from Okta
    deactivatedUsersUrl= url + '/api/v1/users?filter=status eq "DEPROVISIONED"'
    res = requests.get(deactivatedUsersUrl,headers={'Accept': 'application/json', 'Content-Type': 'application/json',
                                         'Authorization': 'SSWS ' + token},verify=False)
    result=res.json()
    length=len(result)

    if res.status_code == 200:

        # Write to a file if no deactivated users found
        if length==0:
             with open('NoUserFound.txt', 'a') as f:
                f.write('No deactivated users found')

    # Retrieve the id to pass it to the Delete user API method if deactivated users found
        else:
            for attributes in result:
                userid=attributes['id']
                login=attributes['profile']['login']

            # Call user delete function
                deleteDeactivatedUsers(userid, login)

    # Log the error to a file if unable to retrieve the deactivated users
    else:
        with open('UserNotFetched.txt', mode='a') as f:
            error=str(result['errorSummary'])
            writer = csv.writer(f, delimiter=',')
            writer.writerow([error])

    return res.status_code

#Call the method that gets the deactivated user list


getDeactivatedUsers()
