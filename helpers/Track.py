from enum import Enum
from helpers import SpotifyToYT
from pytube import extract, YouTube, Search

import re
import requests

class TrackType(Enum):
    SPOTIFY = 1
    YOUTUBE = 2
    SOUNDCLOUD = 3
    UNKNOWN = 4


class Track():

    def __init__(self, input_str: str):

        # check als url spotify track is
        if input_str.find("open.spotify.com/track") != -1:
            spToYt = SpotifyToYT.SpotifyToYT()
            self.url = spToYt.spotifyToYoutubeURLs(input_str)
            self.track_type = TrackType.SPOTIFY

        # check als url youtube track is
        elif re.match(r"^(?:https?:)?(?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/(?:watch|v|embed)(?:\.php)?(?:\?.*v=|\/))([a-zA-Z0-9\_-]{7,15})(?:[\?&][a-zA-Z0-9\_-]+=[a-zA-Z0-9\_-]+)*$", input_str):
            self.url = input_str
            self.track_type = TrackType.YOUTUBE

        # check als url soundcloud track is
        elif re.match(r"https://soundcloud.com/([^/]+)/([^/]+)", input_str):
            self.url = input_str
            self.track_type = TrackType.SOUNDCLOUD

        # not a url, look it up on youtube later
        else:
            self.track_type = TrackType.UNKNOWN


        # set title, author, image & length of track
        if self.track_type is TrackType.YOUTUBE or self.track_type is TrackType.SPOTIFY:
            yt = YouTube(self.url)
            
            self.title = yt.title
            self.author = yt.author 
            self.image = f"http://img.youtube.com/vi/{extract.video_id(self.url)}/0.jpg"
            self.length = yt.length
        
        elif self.track_type is TrackType.SOUNDCLOUD:
            pattern = r"https:\/\/soundcloud.com\/([^\/]+)/([^\/]+)"
            self.author, self.title = re.search(pattern, self.url).groups()
            self.title = self.title.split('?si')[0]
            self.image='https://play-lh.googleusercontent.com/6FoFUmywGeblaF0iUTWb4EdH2SvXeOU_bgXQFRGhHTRiMWVlG8sAVN-BqjlWUJh3GR3a'
            
            self.length = None # niet mogelijk om te vinden

        # not a url, search on youtube
        else:
            yt = custom_search(input_str)[0]

            self.url = yt.watch_url
            self.title = yt.title
            self.author = yt.author 
            self.length = yt.length
            self.image = f"http://img.youtube.com/vi/{extract.video_id(self.url)}/0.jpg"
            self.track_type = TrackType.YOUTUBE





# Custom function to handle adSlotRenderer
def custom_search(query):
    search_results = Search(query)
    videos = []
    for result in search_results.results:
        if 'adSlotRenderer' in result:
            continue
        videos.append(result)

    return videos