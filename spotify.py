import os
from dotenv import load_dotenv

from random import shuffle

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(CLIENT_ID))

def parse_link(url):
    try:
        playlist_id = url.split('playlist/')[1]
        playlist_id = playlist_id.split('?')[0]
        return playlist_id
    except:
        raise Exception

def get_playlist(url, rounds):
    sp_playlist = sp.playlist(parse_link(url), fields='name,images,tracks')
    results = sp_playlist['tracks']
    tracks = results['items']
    while results['next'] and len(tracks) < 500:
        results = sp.next(results)
        tracks.extend(results['items'])
    shuffle(tracks)
    print(len(tracks))

    placeholder = 'https://cdn.freebiesupply.com/logos/large/2x/spotify-2-logo-png-transparent.png'
    playlist = []
    for item in tracks[:rounds]:
        track = item['track']
        formated_artists = [artist['name'] for artist in track['artists']]
        formatted_track = {
            'name': track['name'],
            'artists': formated_artists,
            'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else placeholder
        }
        playlist.append(formatted_track)

    playlist_info = {
        'name': sp_playlist['name'],
        'thumbnail': sp_playlist['images'][0]['url'] if sp_playlist['images'] else placeholder,
        'length': min(rounds, len(playlist))
    }
    return playlist_info, playlist
