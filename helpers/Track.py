from enum import Enum
from helpers import sptoyt
from pytube import extract, YouTube, Search
from bs4 import BeautifulSoup

import re
import requests

class TrackType(Enum):
    SPOTIFY = 1
    YOUTUBE = 2
    SOUNDCLOUD = 3
    UNKNOWN = 4


class Track():

    def __init__(self, input: str):

        # check als url spotify track is
        if input.find("open.spotify.com/track") != -1:
            spToYt = sptoyt.SpotifyToYT()
            self.url = spToYt.spotifyToYoutubeURLs(input)
            self.track_type = TrackType.SPOTIFY

        # check als url youtube track is
        elif re.match(r"^(?:https?:)?(?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/(?:watch|v|embed)(?:\.php)?(?:\?.*v=|\/))([a-zA-Z0-9\_-]{7,15})(?:[\?&][a-zA-Z0-9\_-]+=[a-zA-Z0-9\_-]+)*$", input):
            self.url = input
            self.track_type = TrackType.YOUTUBE

        # check als url soundcloud track is
        elif re.match(r"https://soundcloud.com/([^/]+)/([^/]+)", input):
            self.url = input
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

            response = requests.get(self.url)
            soup = BeautifulSoup(response.content, 'html.parser')
            self.image=soup.find('meta', {'property': 'og:image'})['content']
            
            self.length = None # niet mogelijk om te vinden

        # not a url, search on youtube
        else:
            s = Search(input)
            yt = s.results()[0]
            print(yt)
            self.url = yt.videoId
            self.title = yt.title
            self.author = yt.author 
            self.length = yt.length
        
            self.track_type = TrackType.YOUTUBE


