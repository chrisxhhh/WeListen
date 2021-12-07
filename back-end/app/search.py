from googleapiclient.discovery import build
import json
import pafy

from API_KEYS import *
from app.models import *

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def insert_new_song(id, user_title, user_artist, thumbnails, video_title, video_channel):
    newSong = Song(songID=id, songName=user_title,songArtist=user_artist,
                   songThumbnails=thumbnails,songVidTitle=video_title, songChannelName=video_channel)
    db.session.add(newSong)
    db.session.commit()



def search_youtube_url(title, artist):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # search for the top result using songname and author
    # https://developers.google.com/youtube/v3/docs/search#resource
    songInDB = Song.query.filter_by(songName=title,songArtist=artist).first()
    if songInDB:
        songID = songInDB.songID
        return songID
    print("search YOUTUBE using quota")
    search_response = youtube.search().list(q = title+" "+artist, part='id,snippet',maxResults=1).execute()
    songID = search_response['items'][0]['id']['videoId']
    songInDB = Song.query.filter_by(songID = songID).first()
    if not songInDB:
        thumbnails = json.dumps(search_response['items'][0]['snippet']['thumbnails'])
        video_title = search_response['items'][0]['snippet']['title']
        video_channel = search_response['items'][0]['snippet']['channelTitle']
        print(type(thumbnails))
        print("insert {} to db".format(songID))
        insert_new_song(songID,title,artist, thumbnails,video_title,video_channel)

    #print(search_response)
    return songID




# prepare the format for returning search song request
# return a python dictionary
def formulate_response(songID):
    response_dict = {}

    song = Song.query.filter_by(songID=songID).first()

    # use search function
    # search_response = search_youtube_url(songID, "")

    #extract information
    songID = song.songID
    print(songID)

    channelName = song.songArtist
    songTitle = song.songVidTitle
    thumbnails = song.songThumbnails

    #query in database using songID

    # get data
    # use pafy to convert webstie url to a audio stream url
    # TODO: Still bugging gdata=False
    #video = pafy.new(url, gdata=False)
    video = pafy.new(songID, basic=False)
    # print(video.length)
    duration = video.length
    num_likes = video.likes
    num_views = video.viewcount
    # video_title = video.title
    audio = video.getbestaudio()
    audio_url = audio.url

    response_dict = {
                     "artist":channelName,
                     "audio_stream": audio_url,
                     "songID": songID,
                     "thumbnails": thumbnails,
                     "duration": duration,
                     "num_likes": num_likes,
                     "video_title": songTitle,
                     }
    print(response_dict)
    return response_dict
