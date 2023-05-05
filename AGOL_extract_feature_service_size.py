#extract size value for all feature services under owner's username and exports to a csv file

from arcgis.gis import GIS
import json
import requests
import csv

#connect to arcgisonline
portalUrl = "https://{mysite}}.maps.arcgis.com"
username = 'username'
password = "password"
gis = GIS(portalUrl, username, password)

#get_users
source_users = gis.users.search('!esri_ & !admin')

qe = "owner: " + gis.users.me.username
user_content_count = gis.content.advanced_search(
    query=qe, max_items=-1, return_count=True)

#query feature service user_contect to extract the feature services
qe = f"owner: {gis.users.me.username} type:Feature Service"
max_items = user_content_count
user_content_as_dict = gis.content.advanced_search(query=qe, max_items=max_items, as_dict=True)  
results_all_values = user_content_as_dict['results']

#generate token
def generateToken(username, password, portalUrl):
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    parameters = {'username': username,
                  'password': password,
                  'client': 'referer',
                  'referer': portalUrl,
                  'expiration': 60,
                  'f': 'json'}
    url = portalUrl + '/sharing/rest/generateToken?'
    response = requests.post(url, data=parameters, headers=headers)

    try:
        jsonResponse = response.json()       
        if 'token' in jsonResponse:
            return jsonResponse['token']
        elif 'error' in jsonResponse:
            print (jsonResponse['error']['message'])
            for detail in jsonResponse['error']['details']:
                print (detail)
    except ValueError:
        print('An unspecified error occurred.')
        print(ValueError)
       
generated_token = generateToken(username, password, portalUrl)

results_filtered = []
for feature_serv in results_all_values:
    filtered = {k:v for k,v in feature_serv.items() if k=='id' or k =='url'}
    results_filtered.append(filtered)

#extract size by feature server id
save_result_csv = []
for i in results_filtered:
    url_content = i.get('url')
    feature_id = i.get('id')
    url = f'{url_content}?f=pjson&token={generated_token}'
    response = requests.get(url)
    data = response.json()
    if 'size' in data:
        size = (data['size'])
    else:
        size = 'no value for size'
    result_size = {'feature_service_id': feature_id, 'feature_service_size': size}
    save_result_csv.append(result_size)

# export results as csv
fields = ['feature_service_id', 'feature_service_size']
with open('feature_service_id_size.csv', 'w', newline='') as file: 
    writer = csv.DictWriter(file, fieldnames = fields)
    writer.writeheader() 
    writer.writerows(save_result_csv)