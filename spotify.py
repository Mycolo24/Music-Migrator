import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from selenium import webdriver

DRIVER = webdriver.Firefox()
global TOKEN
TOKEN = {}
CONNECTION = ""


def get_spotify_songs(playlists):
    global TOKEN
    token_info = TOKEN
    try:
        token_info = check_token()
    except:
        print("User not logged in")
        token_info = get_token()
    sp = connect_spotify(token_info['access_token'])
    # lists out all the playlists for the user
    count = 0
    print('Please enter the number of the playlist(s) you want to transfer. When done plesae type "Done"')
    for i in playlists:
        count += 1
        print(f'[{count}] {i}')
        
    playlist_numbers = []
    while True:
        user_input = input('Please enter a number: ') # Gets input from user
        if user_input.lower() != "done": # If user does state that they are done
            try: # Try to change the input into an integer and append it to playlist_numebrs list
                user_input = int(user_input)
                if user_input in playlist_numbers:
                    print("You already entered that number")
                elif user_input <= count and user_input > 0: # if input is not too big or too small and the numebr hasnt been entered yet
                    playlist_numbers.append(user_input) 
                else: 
                    print("Please enter a valid number")
            except: # If number is not an int then inform the user of the error
                print("Please enter a valid number")
        else: # if the user is done then break from loop
            break
    
    playlist_with_songs = {} # Declare variable to store playlist name and songs
    for item in playlist_numbers: # Loops through all the numbers inputted by user
        playlist_songs = []
        count = 0
        for key in playlists: # Loops through playlists and until it gets to the correct one
            count += 1
            iteration = 1
            if item == count:
                while True:
                    songs = sp.playlist_items(playlist_id=playlists[key], offset=iteration, limit= 10)
                    iteration += 1
                    playlist_songs.append(songs)

                    if len(songs) < 10:
                        break
                playlist_with_songs[key] = playlist_songs

    print(playlist_with_songs)

            




def playlists():
    global TOKEN
    token_info = TOKEN
    try:
        token_info = check_token()
    except:
        print("User not logged in")
        token_info = get_token()
    sp = connect_spotify(token_info['access_token'])

    iteration = 0
    playlistInformation = {}

    while True:
        # Grabs 10 playlists to start off with
        items = sp.current_user_playlists(limit=10, offset=iteration * 10)['items']

        # Loops through the collected playlists and adds it to a dictionary
        for i in items:
            playlistInformation[i['name']] = i['id']

        iteration += 1
        if len(items) < 10:
            break

    get_spotify_songs(playlistInformation)

def create_Spotify_OAuth():
    scopes = ['user-library-read', 'playlist-read-private']
    return SpotifyOAuth(
        client_id = "facb7c3acff84390b03238a29bc350f4",
        client_secret="6a9b7873585046418e306af7b4eaf12b",
        redirect_uri='http://localhost:5000',
        scope= scopes)


def get_token():
    global TOKEN
    global CONNECTION
    spotifyConnection = create_Spotify_OAuth() # creates a connection to spotify
    auth_url = spotifyConnection.get_authorize_url() # gets authorization url
    DRIVER.get(auth_url) # using selenium connects to authorization url
    current_url = auth_url # sets value current_url that will result false in the loop below
    while "http://localhost:5000/?code=" not in current_url: # While there is no access_code check for the access code
        current_url = DRIVER.current_url 
        time.sleep(1)
    DRIVER.quit() # close selenium
    url_split = current_url.split('=') # split url to cut out the parts I do not need
    TOKEN = spotifyConnection.get_access_token(code=url_split[1]) # gets the access token to use the api
    sp = spotipy.Spotify(auth=TOKEN['access_token'])
    CONNECTION = sp
    return TOKEN



def check_token():
    token_info = TOKEN
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        spotifyConnection = create_Spotify_OAuth()
        token_info = spotifyConnection.refresh_access_token(token_info['refresh_token'])
    return token_info

def connect_spotify(token):
    # Creates a single connection to spotify that can be used multiple times
    global CONNECTION
    sp = CONNECTION
    if not sp:
        sp = spotipy.Spotify(auth=token['access_token'])
    return sp



playlists()
