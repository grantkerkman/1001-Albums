import requests
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

####################
# Functions file
####################

def getData(url: str) -> dict:
    """
    Get data and return as JSON.  No retries or robustness needed,
    its not that big of a deal.
    """

    # Get the response
    response = requests.get(
        url, 
        headers={"Accept": "application/json"}, 
        timeout=30
    )

    # Raise an error for bad responses
    response.raise_for_status()
    
    return response.json()

def getProjectInfo(PROJECT_ID) -> dict:

    # Generate the url
    url = f'https://1001albumsgenerator.com/api/v1/projects/{PROJECT_ID}'

    # Get Data
    data_json = getData(url)

    return data_json

def getAlbumStats() -> dict:

    # Generate the url
    url = f'https://1001albumsgenerator.com/api/v1/albums/stats'

    # Get Data
    data_json = getData(url)

    return data_json

def getUserAlbumStats() -> dict:

    # Generate the url
    url = f'https://1001albumsgenerator.com/api/v1/user-albums/stats'

    # Get Data
    data_json = getData(url)

    return data_json

def getCurrentAlbum(data_json: dict) -> pd.DataFrame:

    # Extract the data from the project JSON
    current_album = data_json.get('currentAlbum', None)

    keys = [
        'artist',
        'name',
        'releaseDate',
        'artistOrigin',
        'genres',
        'subGenres',
        'uuid'
    ]

    data_dict = {key: current_album.get(key, None) for key in keys}

    # Create the DataFrame
    df = pd.DataFrame([data_dict])

    return df

def getListeningHistory(project_json: dict) -> pd.DataFrame:

    # Extract the history from the project JSON
    history_json = project_json.get('history', None)
    history_df = pd.DataFrame(history_json)

    # Reduce down data from albums
    keys = [
        'artist',
        'name',
        'releaseDate',
        'artistOrigin',
        'genres',
        'subGenres',
        'uuid',
    ]

    album_df = pd.DataFrame.from_records(history_df['album'])[keys]

    # Combine datasets and drop unneeded columns
    df = pd.concat([album_df, history_df], axis=1)
    df = df.drop(columns=['album', 'review', 'revealedAlbum'])

    # Convert dates
    df['generatedAt'] = pd.to_datetime(df['generatedAt']).dt.tz_localize(None).dt.floor('D')

    return df