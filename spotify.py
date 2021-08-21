import os
from dotenv import load_dotenv

from random import shuffle

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
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
	def generate_playlist_from_url(url):
		sp_playlist = sp.playlist_items(Spotify.parse_link(url))
		playlist = []
		for item in sp_playlist['items']:
			track = item['track']
			formated_artists = [artist['name'] for artist in track['artists']]
			formatted_track = {'name': track['name'], 'artists': formated_artists}
			playlist.append(formatted_track)
		shuffle(playlist)
		return playlist
