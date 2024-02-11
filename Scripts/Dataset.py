import pandas as pd
import numpy as np
import swifter
from pathlib import Path
import os

def main():
    ## Creates an absolute path to the dataset
    abspath = str(os.getcwd()).split("/")
    relpath = r"Data/charts.csv"
    abspath = "/".join([i for i in abspath[:-1]])
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