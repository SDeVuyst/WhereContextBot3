import spotipy
import re
import os

from googleapiclient.discovery import build
from spotipy.oauth2 import SpotifyClientCredentials




class SpotifyToYT:

    def __init__(self):
        self.spotify_client_id = os.environ.get("SPOTIFY_ID")
        self.spotify_client_secret = os.environ.get("SPOTIFY_SECRET")
        self.yt_api = os.environ.get("YT_TOKEN")

    #create api
    def connect(self):
        sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=self.spotify_client_id, client_secret=self.spotify_client_secret)
        )
        return sp


    #fetch the playlist
    def fetch_playlist_by_id(self, api, id):
        playlist_response = api.playlist(playlist_id=id)
        name = playlist_response['name']
        playlist_items = playlist_response['tracks']['items']
        
        return playlist_items, name


    #fetch the playlist
    def fetch_track_by_id(self, api, id):
        track_response = api.track(track_id=id)
        name = track_response['name']
        
        return track_response, name
    


    #extract song data from playlist items
    def extract_data(self, api, items):
        tracks_data = []
        for i in items:
            item = dict.fromkeys(['track_name','artist_name','album_name'])
            track_name = i['track']['name']
            artist_name = i['track']['artists'][0]['name']
            album_name = i['track']['album']['name']

            item['track_name'] = track_name
            item['artist_name']= artist_name
            item['album_name']= album_name

            tracks_data.append(item)
    
        return tracks_data


    #build queries to search on yt 
    def query_builder(self, pl_data):
        queries = []
        for obj in pl_data:
            q = "{} {} {}".format(obj['track_name'],obj['album_name'],obj['artist_name'])
            queries.append(q)
        return queries


    def makePublicService(self):
        service = build(serviceName='youtube',version='v3',developerKey=self.yt_api)
        return service


    def getVideoIds(self, queries, api):
        service = self.makePublicService()
        ids = []
        for i in range(len(queries)):
            request = service.search().list(part="snippet",
                    maxResults=2,
                    q = queries[i]
                )
            response = request.execute()
            videoid = response['items'][0]['id']['videoId']

            ids.append(f"https://www.youtube.com/watch?v={videoid}")

        return ids


    def spotifyToYoutubeURLs(self, spotifyURL):
        pl_match = re.match(r"https?:\/\/[^/]*\bspotify\.com\/playlist\/([^\s?]+)", spotifyURL)
        song_match = re.match(r"https?:\/\/[^/]*\bspotify\.com\/track\/([^\s?]+)", spotifyURL)

        if pl_match:
            spotifyID = pl_match[1]
            api = self.connect()
            items_name = self.fetch_playlist_by_id(api,spotifyID)
            queries = self.query_builder(self.extract_data(api,items_name[0]))
            return self.getVideoIds(queries, api)

        elif song_match:
            spotifyID = song_match[1]
            api = self.connect()
            items_name = self.fetch_track_by_id(api,spotifyID)
            item = dict.fromkeys(['track_name','artist_name','album_name'])
            item['track_name'] = items_name[1]
            item['artist_name']= items_name[0]['artists'][0]['name']
            item['album_name']= items_name[0]['album']['name']

            queries = self.query_builder([item])
            return self.getVideoIds(queries, api)[0]

        else:
            return None