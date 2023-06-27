import os
import isodate
from googleapiclient.discovery import build
from datetime import timedelta


class PlayList:
    """Класс для плейлиста"""
    api_key: str = os.getenv('YT_API_KEY')

    def __init__(self, playlist_id):
        self.__playlist_id = playlist_id
        self.title = self.get_playlist_title()
        self.url = ''.join(['https://www.youtube.com/playlist?list=', self.__playlist_id])

    def get_info(self):
        """По id плейлиста получает данные о элементах плейлиста"""
        playlist = self.get_service().playlistItems().list(part='snippet,contentDetails',
                                                           playlistId=self.__playlist_id
                                                           ).execute()
        return playlist

    def get_playlist_title(self):
        """По id канала получает список плейлистов на канале и из них получает название канала по его id"""
        playlists = self.get_service().playlists().list(channelId=self.get_info()['items'][0]['snippet']['channelId'],
                                                        part='contentDetails,snippet',
                                                        maxResults=50,
                                                        ).execute()

        for playlist in playlists.get('items', []):
            if playlist.get('id') == self.__playlist_id:
                title = playlist.get('snippet', {}).get('title')
                if title:
                    return title

        return None

    @classmethod
    def get_service(cls):
        return build('youtube', 'v3', developerKey=cls.api_key)

    def get_video_list(self):
        """Возращает список из id видео(плейлист)"""
        return [video['contentDetails']['videoId'] for video in self.get_info()['items']]

    @property
    def total_duration(self):
        video_ids = self.get_video_list()
        videos = self.get_service().videos().list(part='contentDetails', id=','.join(video_ids)).execute()

        total_duration = sum([isodate.parse_duration(video['contentDetails']['duration']) for video in videos['items']],
                             timedelta())

        return total_duration

    def show_best_video(self):
        videos = self.get_service().videos().list(part='statistics', id=','.join(self.get_video_list())).execute()
        best_video = max(videos['items'], key=lambda video: int(video['statistics']['likeCount']))

        best_video_id = best_video['id']
        best_video_url = f"https://youtu.be/{best_video_id}"

        return best_video_url
