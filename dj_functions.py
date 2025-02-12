import classic_set
import wedding_set
import tonal_set
import riser_set
import utils
import optimizer
import playlist_processor
import config
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os

# Set up environment variables
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
CACHE_PATH = '.spotipyoauthcache'

scope = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'

# Initialize Spotify OAuth object with cache path
sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=scope,
                        cache_path=CACHE_PATH)

def get_token():
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        print(f"Please navigate to the following URL to authenticate: {auth_url}")
        response = input("Paste the full URL you were redirected to: ")
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code, as_dict=False)
    
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    
    return token_info['access_token']

async def generate_dj_set(playlist_id, num_songs, set_type, access_token):
    sp = Spotify(auth=access_token)

    # Process the playlist data and create a DataFrame
    df_playlist = await playlist_processor.process_playlist_data(playlist_id, access_token)

    # Calculate hype and get top songs
    df_SONG_POOL = utils.calculate_hype(df_playlist)

    if set_type == 1:
        set_type_str = 'classic'
    elif set_type == 2:
        set_type_str = 'wedding'
    elif set_type == 3:
        set_type_str = 'tonal'
    elif set_type == 4:
        set_type_str = 'riser'

    # Optimize the DJ set
    dj_set = optimizer.genetic_algorithm(df_SONG_POOL, num_songs, set_type=set_type_str)

    # Print the final fitness, total_hype, transition_compatibility, and section_scores
    if set_type_str == 'classic':
        fitness, total_hype, transition_compatibility, section_scores = classic_set.fitness_classic(dj_set)
    elif set_type_str == 'wedding':
        fitness, total_hype, total_popularity, transition_compatibility, section_scores = wedding_set.fitness_wedding(dj_set)
    elif set_type_str == 'tonal':
        fitness, total_hype, transition_compatibility, section_scores = tonal_set.fitness_tonal(dj_set)    
    elif set_type_str == 'riser':
        fitness, total_hype, transition_compatibility, section_scores = riser_set.fitness_riser(dj_set)   

    # Debugging
    print(f"Best Fitness in Final DJ Set: {fitness:.2f}")
    # print("DJ Set:", dj_set)

    # Extract track information correctly
    track_info = []
    for track in dj_set:
        try:
            track_name = track['Track Name']
            artist_name = track['Artist Name(s)']
            key_mode = utils.key_mode_to_string(track['Key'], track['Mode'])
            camelot_key = utils.convert_to_camelot(track['Key'], track['Mode'])
            tempo = track['Tempo']
            track_info.append({
                'name': track_name,
                'artist': artist_name,
                'key': key_mode,
                'camelot_key': camelot_key,
                'tempo': tempo
            })
        except KeyError:
            track_info.append({
                'name': 'Unknown Track',
                'artist': 'Unknown Artist',
                'key': 'Unknown Key',
                'tempo': 'Unknown Tempo'
            })

    # Pass the track IDs to playlist_creator
    track_ids = [track['Track ID'] for track in dj_set]
    user_id = sp.current_user()['id']
    playlist_url = create_playlist_and_add_tracks(sp, user_id, track_ids)

    return track_info, playlist_url, fitness, total_hype, transition_compatibility, section_scores

def create_playlist_and_add_tracks(sp, user_id, track_ids):
    playlist_name = "Generated DJ Set"
    playlist_description = "A DJ set generated using a genetic algorithm"
    playlist = sp.user_playlist_create(user_id, playlist_name, public=True, description=playlist_description)
    sp.playlist_add_items(playlist['id'], track_ids)
    print(f"Playlist '{playlist_name}' created successfully with {len(track_ids)} tracks.")
    return playlist['external_urls']['spotify']
