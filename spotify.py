import os
from dotenv import load_dotenv

from random import shuffle

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(CLIENT_ID))

class Spotify:
    @staticmethod
    def parse_link(url):
        try:
            playlist_id = url.split('playlist/')[1]
            playlist_id = playlist_id.split('?')[0]
            return playlist_id
        except:
            raise Exception

    @staticmethod
    def get_playlist(url):
        sp_playlist = sp.playlist(Spotify.parse_link(url),fields='name,images,tracks')

        placeholder = 'https://cdn.freebiesupply.com/logos/large/2x/spotify-2-logo-png-transparent.png'
        playlist_info = {
            'name': sp_playlist['name'],
            'thumbnail': sp_playlist['images'][0]['url'] if sp_playlist['images'] else placeholder
        }

        results = sp_playlist['tracks']
        tracks = results['items']
        while results['next'] and len(tracks) < 500:
            results = sp.next(results)
            tracks.extend(results['items'])
        print(len(tracks))

        playlist = []
        for item in tracks:
            track = item['track']
            formated_artists = [artist['name'] for artist in track['artists']]
            formatted_track = {
                'name': track['name'],
                'artists': formated_artists,
                'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else placeholder
            }
            playlist.append(formatted_track)
        shuffle(playlist)
        return playlist_info, playlist
