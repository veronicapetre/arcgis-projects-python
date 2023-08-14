#!/usr/bin/env python3

import json
import os
from shapely.geometry import shape
from datetime import datetime
import geopandas as gpd

local_chunks = []

def split_buildings_geojson(input_file, chunk_size,split_folder):
    with open(input_file, 'r') as f:
        data = json.load(f)
    chunks = [data['features'][i:i + chunk_size] for i in range(0, len(data['features']), chunk_size)]   
    for idx, chunk in enumerate(chunks):
        output_file_split = f'{split_folder}/chunk_{idx}.geojson'
        output_data = {'type': 'FeatureCollection', 'features': chunk}
        with open(output_file_split, 'w') as f:
            json.dump(output_data, f)
        print(f'Chunk {idx} written to {output_file_split}.')

def read_chunk_geojson(folder_path):
    geojson_data_list = []
    files = os.listdir(folder_path)
    for file in files:
        if file.endswith('.geojson'):
            file_path = os.path.join(folder_path, file)
            geojson_data_list.append(file)
    return geojson_data_list

def filter_polygons_by_NSW(input_file, containment_file, output_file):
    # Load the GeoJSON file containing the polygons to be filtered
    with open(input_file, 'r') as f:
        input_data = json.load(f)
    with open(containment_file, 'r') as f:
        containment_data = json.load(f)
    containment_polygon = shape(containment_data['features'][0]['geometry'])
    filtered_features = []
    for feature in input_data['features']:
        polygon = shape(feature['geometry'])
        if containment_polygon.contains(polygon):
            filtered_features.append(feature)
    # print('filtered polygons are ready')
    output_data = {
        'type': 'FeatureCollection',
        'features': filtered_features
    }
    with open(output_file, 'w') as f:
        json.dump(output_data, f)

def load_chunks(build_path, filtered_folder):
    for chunk in build_path:
        print(f"Reading chunk { chunk }")
        buildings_path = f'{filtered_folder}/{chunk}'
        buildings = gpd.read_file(buildings_path)
        local_chunks.append(buildings)
    
def check_building_intersections(property_list,build_path,filtered_folder,save_every=1):
    properties_processed = 0
    start_time = datetime.now()
    for ind in range(len(property_list)):
        name = property_list['planlabel'][ind]
        print(f'Property {ind} - {name}')
        geom = property_list['geometry'][ind]
        for chunk in local_chunks:
            has_intersection = False
            continue_outer_loop = False
            for building in chunk['geometry']:
                if geom.intersects(building):
                    has_intersection = True
                    property_list.at[ind, 'has_building'] = True
                    break
            if has_intersection:
                continue_outer_loop = True
                break
        properties_processed += 1
        total_time = datetime.now() - start_time
        time_per_property = total_time.total_seconds() / properties_processed
        properties_per_hour = 3600 / time_per_property
        print(f'Properties processed: { properties_processed} Properties per hour: {int(properties_per_hour)}')
        if properties_processed % save_every == 0:
        # Save the GeoJSON every 'save_every' properties
            print(f'Saving GeoJSON after processing {properties_processed} properties...')
            updated_geojson_path = 'update/updated_properties_.geojson'
            property_list.to_file(updated_geojson_path, driver='GeoJSON')
        if continue_outer_loop:
            continue

def create_new_folder(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

def intersected_buildings(build_path,filtered_folder,property_list):
    for chunk in build_path:
        print(f'Checking buildings for intersection in chunk { chunk }')
        buildings_gdf = gpd.read_file(f'{filtered_folder}/{chunk}')
        properties_sindex = property_list.sindex

        intersections = []
        for building_geom in buildings_gdf.geometry:
            possible_matches_index = list(properties_sindex.intersection(building_geom.bounds))
            possible_matches = property_list.iloc[possible_matches_index]
            precise_matches = possible_matches[possible_matches.intersects(building_geom)]
            intersects = len(precise_matches) > 0
            intersections.append(intersects)

        buildings_gdf['intersects_property'] = intersections
        buildings_gdf_filtered = buildings_gdf[buildings_gdf['intersects_property'] == True]

        if not buildings_gdf_filtered.empty:
            mode = 'a' if os.path.isfile('./buildings_with_intersections.geojson') else 'w'
            buildings_gdf_filtered.to_file('./buildings_with_intersections.geojson', driver='GeoJSON', mode=mode)

def within_buildings(build_path,filtered_folder,property_list):
    for chunk in build_path:
        print(f'Checking if buildings inside property in chunk {chunk}')
        buildings_gdf = gpd.read_file(f'{filtered_folder}/{chunk}')
        properties_sindex = property_list.sindex

        buildings_within = []
        for building_geom in buildings_gdf.geometry:
            possible_matches_index = list(properties_sindex.intersection(building_geom.bounds))
            possible_matches = property_list.iloc[possible_matches_index]
            within_matches = possible_matches[possible_matches.contains(building_geom)]
            within = len(within_matches) > 0
            buildings_within.append(within)

        buildings_gdf['within_property'] = buildings_within
        buildings_gdf_filtered = buildings_gdf[buildings_gdf['within_property'] == True]
        
        if not buildings_gdf_filtered.empty:
            mode = 'a' if os.path.isfile('./buildings_within_properties.geojson') else 'w'
            buildings_gdf_filtered.to_file('./buildings_within_properties.geojson', driver='GeoJSON', mode=mode)

#RUN SCRIPT
def main():
    print('Start script')
    start_time = datetime.now()

    input_geojson_file = 'Australia.geojson' 
    split_folder = 'australia_split'
    NSW_geojson_file = 'NSW.json' #source https://data.opendatasoft.com/explore/dataset/georef-australia-state%40public/export/?disjunctive.ste_code&disjunctive.ste_name
    filtered_folder = 'filtered_b'
    property_path = 'properties.json'
    update_folder= 'update'

    # # Create new folders
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # folders_name = ['australia_split','update','filtered_buildings']
    # for folder in folders_name:
    #     full_path = os.path.join(script_dir,folder)
    #     create_new_folder(full_path)
   
    # # Split Australia geojson buildings file in smaller chunks
    #chunk_size = 300000
    #split_buildings_geojson(input_geojson_file, chunk_size, split_folder)
    #print('split buildings in chunks')

    # # Fiter and export building chuncks only for the NSW region
    # geojson_list = read_chunk_geojson(split_folder)
    # for elem in geojson_list:
    #    input_geojson_file = f'{split_folder}/{elem}' 
    #    output_geojson_file = f'{filtered_folder}/filtered_{elem}'
    #    filter_polygons_by_NSW(input_geojson_file, NSW_geojson_file, output_geojson_file)
    # end_time = datetime.now()
    # print('Duration to filter just NSW region buildings: {}'.format(end_time - start_time))

    # # Update original properties file with has_building column (True/False) using intersection
    property_list = gpd.read_file(property_path)
    # property_list['has_building'] = False
    build_path = read_chunk_geojson(filtered_folder)
    # load_chunks(build_path, filtered_folder)
    # check_building_intersections(property_list, build_path,filtered_folder)

    # #Save the updated GeoJSON file with has_buildings values
    # print('updating GeoJSON')
    # updated_geojson_path = f'{update_folder}/updated_properties.geojson'
    # property_list.to_file(updated_geojson_path, driver='GeoJSON')


    # #Filter only properties with buildings and export to new file
    # updated_areas_list = gpd.read_file(updated_geojson_path)
    # filtered_areas = updated_areas_list[updated_areas_list['has_building'] == True]
    # print('save new file')
    # updated_geojson_path_intersect = f'{update_folder}/properties_with_buildings.geojson'
    # filtered_areas.to_file(updated_geojson_path_intersect, driver='GeoJSON')

    #Export only buildings that intersect properties
    intersected_buildings(build_path,filtered_folder,property_list)

    # Export only buildings that are inside properties
    within_buildings(build_path,filtered_folder,property_list)

    end_time = datetime.now()
    print('Total time: {}'.format(end_time - start_time))

if __name__ == "__main__":
    main()
