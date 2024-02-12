## Make sure to update the client_id and client_secret variables
## before running.
## The API request code may fail - I need to update that part of
## the code (in Version 1.0.0)

import pandas as pd
import numpy as np
import swifter
from pathlib import Path
import os
import base64
from requests import post, get
import json

version = "1.0.0"

client_id = '1435ba72a607475eab2e2184cabc2777'
client_secret = '61951b1287e94f91bb4a57c664606e59'

def get_token():
    '''
    Generates a token to make an API request
    '''
    auth_string= client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {"Authorization" : 'Basic '+ auth_base64,
               'Content_type': 'application/x-www-form-urlencoded'
               }
    data = {'grant_type': 'client_credentials'}
    result = post(url, headers = headers, data = data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token):
    return {'Authorization': 'Bearer ' + token }

def get_features(token, song_id):
    '''
    Retreives all the information based on the track ID passed
    '''
    url = f'https://api.spotify.com/v1/tracks/{song_id}?market=US'
    headers = get_auth_header(token)
    result = get(url , headers = headers)
    json_result = json.loads(result.content)

    return json_result

def main():
    try:
        ## Creates an absolute path to the dataset
        abspath = str(os.getcwd()).split("/")
        abspath = "/".join([i for i in abspath[:-1]])
        relpath = r"Data/charts.csv"
        path = abspath + "/" + relpath

        ## Loads the dataset
        df = pd.read_csv(path)

        ## Sort values and drops duplicates
        df.sort_values(by= ["date", "position"], inplace= True)
        df.drop_duplicates(subset= ["name", "position", "date"], keep= "first", inplace= True)

        ## Transforms all dates into datetime objects
        df.date = pd.to_datetime(df.date)

        ## Changes the 'artists' column format
        artists = []
        for (index, row) in df.iterrows():
            artist = row.artists.replace("[", "").replace("'", "").replace("]", "")
            artist = artist.split(",")
            artist = artist[0].strip()
            artists.append(artist)

        df.drop(columns= ["artists"], inplace= True)
        df["artists"] = artists

        ## Creates the Dummy 1 variable
        variable = []
        songs = {}
        previous_date = {}

        for date in df.date.unique():
            temp_df = df.loc[(df.date == date)]
            for (index, row) in temp_df.iterrows():
                if row.name not in songs:
                    variable.append(0)
                    songs[row.name] = date
                else:
                    if previous_date == songs.get(row.name):
                        variable.append(1)
                        songs[row.name] = date
                    elif previous_date != songs.get(row.name):
                        variable.append(0)
                        songs[row.name] = date
            
            previous_date = date

        df["dummy_1"] = variable

        ## Creates a token for the API request
        token = get_token()

        ## Creates a secondary DataFrame with the track IDs and
        ## the release date
        data = {"track_id": [], "release_date": []}
        for id in df.track_id.unique():
            track = get_features(token, id)
            data["track_id"].append(id)
            data["release_date"].append(track["album"]["release_date"])
        dates = pd.DataFrame(data= data)

        ## Maps the track ID in the main DataFrame and appends
        ## the release date
        df["release_date"] = df["track_id"].map(dates.set_index("track_id")["release_date"])

        ## Loads the raw dataset again
        df2 = pd.read_csv(path)
        df2.date = pd.to_datetime(df2.date)

        ## Sorts values
        df2.sort_values(by= ["date", "position"], inplace= True)

        ## Creates the Dummy 2 variable
        chart_dates = df2.date.unique()
        previous_date = chart_dates[0]
        variable = []
        for date in chart_dates:
            temp_df = df2.loc[(df2.date == date)]
            for (index, row) in temp_df.iterrows():
                if previous_date <= row.release_date <= date:
                    variable.append(1)
                else:
                    variable.append(0)
            
            previous_date = date

        df["dummy_2"] = variable

        ## Exports the DataFrame
        abspath = str(os.getcwd()).split("/")
        abspath = "/".join([i for i in abspath[:-1]])
        relpath = r"Data/Dataset.xlsx"
        path = abspath + "/" + relpath
        df.to_excel(path, index= False)
    except Exception as error:
        print(error)
        raise

if __name__ == "__name__":
    main()