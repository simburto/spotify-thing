import subprocess
import sys

#check for packages
try: 
  if open('cache.txt', 'r').read() != '1':
    packages = open('requirements.txt', 'r').read().splitlines()
    print("installing dependencies")
    for i in range(len(packages)):
      subprocess.check_call([sys.executable, "-m", "pip", "install", packages[i]])
    with open('cache.txt', 'w') as f:
      f.write('1')
except:
  open('cache.txt', 'w')
  print("created cache file")
  print("installing dependencies")
  packages = open('requirements.txt', 'r').read().splitlines()
  for i in range(len(packages)):
    subprocess.check_call([sys.executable, "-m", "pip", "install", packages[i]])
  with open('cache.txt', 'w') as f:
    f.write('1')

import spotipy
import spotipy.oauth2 as oauth2
import os
import datetime
from dotenv import load_dotenv
import spotipy.util as util
import numpy as np
from time import sleep
from tqdm import trange

# load environment values
load_dotenv()
client_id = os.getenv('API_KEY')
client_secret = os.getenv('API_SECRET')
redirect_uri = os.getenv('API_LINK')
username = os.getenv('USERNAME')
playlist_link = os.getenv('PLAYLIST_LINK')
if len(client_id) != 0 and len(client_secret) != 0 and len(redirect_uri) != 0 and len(playlist_link) != 0 and len(username) != 0:
    print(".env values imported")
else:
    print(".env values failed to import")
    exit()

#authenticate dev key
client_credentials_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

#user authorization
scopes = 'playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public ugc-image-upload'
token = util.prompt_for_user_token(username, scopes, client_id, client_secret, redirect_uri)
sp = spotipy.Spotify(auth=token)

#filter out link to get playlist id
def PID(playlist_link):
  playlist_URI = playlist_link.split("/")[-1].split("?")[0]
  return(playlist_URI)

#get playlist tracks
def get_playlist_tracks(username, playlist_id):
    results = sp.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
      results = sp.next(results)
      tracks.extend(results['items'])
    print("got playlist tracks")
    if len(tracks) == 0:
       print("import failed")
       exit()
    return tracks

#filter out tracks to acquire release date and name
def filter(tracks):
    date = []
    date = ['balls' for x in range(len(tracks))]
    name = []
    name = ['balls' for x in range(len(tracks))]
    for i in trange(len(tracks), desc = "Filtering: "):
      date[i] = tracks[i]['track']['album']['release_date']
      name[i] = tracks[i]['track']['name']
      sleep(0.001)
    print("tracks filtered")
    return (date, name)

#average date
def dateavg(date):
    mean = (np.array(date, dtype='datetime64[D]')
        .view('i8')
        .mean()
        .astype('datetime64[D]'))
    current_date = np.datetime64(datetime.datetime.now().date())
    difference = mean - current_date
    return(difference)

#main loop
while True:
    try: 
        playlistid = PID(playlist_link)
        tracks = filter(get_playlist_tracks(username, playlistid))
        date = tracks[0]
        name = tracks[1]
        fdate = str(abs(dateavg(date).astype(int)))
        years = str(round(int(fdate)/365, 2))
        descwrite = "Average song age: " + years + " years (" + fdate + " days)"
        print(descwrite)
        sp.trace = False
        status = sp.playlist_change_details(playlistid, description=descwrite)
        i = 0
        for i in trange(3600):
          sleep(1)
    except spotipy.SpotifyOauthError as e:
        # Refresh the access token
        token = util.prompt_for_user_token(username, scopes, client_id, client_secret, redirect_uri)
        sp = spotipy.Spotify(auth=token)