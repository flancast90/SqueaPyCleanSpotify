# SqaPyCleanSpotify: Replace Explicit Content on Your Spotifyy Playlists
# Author flancast90 (Finn Lancaster)
# Copyright: MIT License

# import statement calls and external libs
"""

List of external libs, can be installed by:
- pip install spotipy

"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import sys
import json
from auth import *

# global variable declaration
scope = "playlist-modify-public playlist-modify-private"
sp = ""

# we will write the users credentials to a file so that we can access them when needed
def authenticate_user():
    global username, client_id, client_secret, sp
    if ((username == "") or (client_id == "") or (client_secret == "") or sys.argv[1] == "credentials"):
        uname = str(input("\nPlease enter your spotify username: "))
        cid = str(input("Please enter your spotify client id: "))
        csec = str(input("Please enter your spotify client secret: "))
    
        username = uname
        client_id = cid
        client_secret = csec

        f = open("auth.py", "w")
        f.write("username='"+uname+"'\nclient_id='"+cid+"'\nclient_secret='"+csec+"'")
        f.close()
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(username=username, client_id=client_id, client_secret=client_secret, redirect_uri="about:blank", scope=scope))
        require_approval()    
    else:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(username=username, client_id=client_id, client_secret=client_secret, redirect_uri="https://localhost:8000", scope=scope))
        require_approval()


# CLI initialisation
# CLI Error-handling
# we only want to run when user asks, and not when imported
if __name__ == "__main__":
    if len(sys.argv) > 2:
        print('usage: SqueaPyCleanSpotify.py [url/"credentials"]')
        print('SqueaPyCleanSpotify.py: Error: You have specified too many arguments')
        sys.exit()

    if len(sys.argv) < 2:
        print('usage: SqueaPyCleanSpotify.py [url/"credentials"]')
        print('SqueaPyCleanSpotify.py: Error: You must specify a URL to your playlist')
        sys.exit()

    else:
        authenticate_user()


def get_user_action():
    # grab the argument provided by the user in the program call
    playlist_id = sys.argv[1]
    if (playlist_id == "credentials"):
        # check first if user wants to change their login info
        authenticate_user()
    else:
        # re-define playlist-id as split string containing the identifier token
        playlist_id = playlist_id.split("/playlist/", 1)[1]
        clean_playlist_from_uri(playlist_id)


# Here we will actually begin the process of removing the Explicit Songs
def clean_playlist_from_uri(playlist_id):
    playlist = sp.playlist(playlist_id, fields=None, market=None, additional_types=('track', ))
    for i, track in enumerate(playlist['tracks']['items']):
        track_uri = track['track']['uri']
        track_uri = track_uri.split('spotify:track:',1)[1]

        # get song name and artist name via API for later function call to find clean versions
        song_name = track['track']['name']
        artist = track['track']['album']['artists'][0]['name']   

        # check if song is explicit via API
        is_explicit = track['track']['explicit']
        if (str(is_explicit) == "True"):
            find_alternatives(playlist_id, track_uri, song_name, artist, i)
        else:
            print("\n   ➡️  Song '"+song_name+"' is not explicit, moving on")
    print('\n   ✅ All done!')


def find_alternatives(playlist_id, song_id, title, artist, index):
    # now we check if we can find a clean version of the item
    # based on testing, we can determine that the best results are in the form
    # Song Name + Artist + "Clean"
    search_term = title+" "+artist+" Clean"
    
    # initialise the API to search using var search_term as query
    search = sp.search(q=search_term, limit=1, offset=0, type='track', market=None)
    if (len(search['tracks']['items']) == 0):
        print("\n   ❌ Could not find a clean version of '"+title+"'")
    else:
        for i, result in enumerate(search['tracks']['items']):
            clean_track_id = result['uri']
            clean_track_id = clean_track_id.split('spotify:track:',1)[1]

            clean_track_title = result['name']
        
            replace_explicit_content(playlist_id, title, clean_track_title, song_id, clean_track_id, index)


def replace_explicit_content(playlist_id, title, new_title, song_id, new_song_id, index):
    print("\n   ✏️  Replacing '"+title+"' with '"+new_title+"'")
    sp.playlist_remove_specific_occurrences_of_items(playlist_id, [{"uri":song_id,"positions":[index]}], snapshot_id=None)
    sp.playlist_add_items(playlist_id, [new_song_id], position=None)
    


# We want to make sure the user is aware of the risk of losing songs/other issues, and that we are not liable for that
def require_approval():
    user_agrees = str(input("\nDo you give permission to this application to read and modify your Spotify account/playlist? (y/n) "))

    # Handle responses so that what the user says is actually done
    if (user_agrees.lower() == 'y'):
        get_user_action()
    elif (user_agrees.lower() == 'n'):
        exit()
    else:
        require_approval()
    
    return None

