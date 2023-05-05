from arcgis.gis import GIS

#create a GIS object using the arcgisaccount credentials
gis = GIS('https://{agolweb}.maps.arcgis.com', 'username', 'password')

#get the current user
user = gis.users.me

#initialize a dictionary to get store de feature layers for each folder
folder_feature_layers = {}

#get the list of folders for the user
folders = user.folders
folder_titles = []

#append the folder titles to your new list
for folder in folders:
    folder_titles.append(folder['title'])
print(folder_titles)
