import requests


portalUrl = "https://{yoursite}.maps.arcgis.com"
username = 'username'
password = "password"


def generateToken(username, password, portalUrl):
    # Retrieves a token to be used with API requests.
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    parameters = {'username': username,  # Set the parameters for the token request
                  'password': password,
                  'client': 'referer',
                  'referer': portalUrl,
                  'expiration': 200,
                  'f': 'json'}
    url = portalUrl + '/sharing/rest/generateToken?'
    response = requests.post(url, data=parameters, headers=headers)  #Send a POST request to the token endpoint and get the response

    try:
        jsonResponse = response.json()
        
        if 'token' in jsonResponse:
            return jsonResponse['token']  # Parse the JSON response to extract the token
        elif 'error' in jsonResponse:
            print (jsonResponse['error']['message'])
            for detail in jsonResponse['error']['details']:
                print (detail)
    except ValueError:
        print('An unspecified error occurred.')
        print(ValueError)


        
token = generateToken(username, password, portalUrl)
print(token)