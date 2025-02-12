from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import asyncio
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from dj_functions import generate_dj_set
from flask import send_from_directory


load_dotenv()

bp = Blueprint('main', __name__)

sp_oauth = SpotifyOAuth(client_id=os.getenv('SPOTIPY_CLIENT_ID'),
                        client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
                        redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
                        scope='playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private')

@bp.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@bp.route('/')
def home():
    token_info = session.get("token_info", None)
    if token_info:
        print(f"Token Info in Home: {token_info}")
    return render_template('home.html')

@bp.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    print(f"Auth URL: {auth_url}")  # Diagnostic print
    return redirect(auth_url)

# @bp.route('/test_callback')
# def test_callback():
#     print("Test callback route hit")
#     return "Test callback route hit"


@bp.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    print("Code received:", code)
    
    if not code:
        return "Missing code parameter", 400

    try:
        token_info = sp_oauth.get_access_token(code)
        print("Token info received:", token_info)
    except Exception as e:
        print("Error getting token info:", e)
        return "Error getting token info", 500

    if not token_info:
        return "Failed to receive token info", 400

    session["token_info"] = token_info
    print("Session updated with token info:", session.get("token_info"))
    return redirect(url_for('main.playlists'))



@bp.route('/playlists')
def playlists():
    token_info = session.get("token_info", None)
    if not token_info:
        print("No token info in session, redirecting to login")
        return redirect(url_for('main.login'))

    print(f"Using token info: {token_info}")
    sp = Spotify(auth=token_info['access_token'])
    try:
        playlists = sp.current_user_playlists()
        print(f"Playlists fetched: {playlists['items']}")
    except Exception as e:
        print(f"Error fetching playlists: {e}")
        return "Error fetching playlists", 500

    return render_template('playlists.html', playlists=playlists['items'])

@bp.route('/generate', methods=['POST'])
def generate_dj_set_route():
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for('main.login'))

    access_token = token_info['access_token']
    original_playlist_url = request.form.get('playlist_url')
    playlist_id = request.form.get('playlist_id')
    num_songs = int(request.form['num_songs'])
    set_type = int(request.form['set_type'])

    if original_playlist_url:
        playlist_id = extract_playlist_id_from_url(original_playlist_url)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    track_info, new_playlist_url, fitness, total_hype, transition_compatibility, section_scores = loop.run_until_complete(
        generate_dj_set(playlist_id, num_songs, set_type, access_token)
    )

    return jsonify({
        'set_list': track_info,
        'new_playlist_url': new_playlist_url,
        'fitness': fitness,
        'total_hype': total_hype,
        'transition_compatibility': transition_compatibility,
        'section_scores': section_scores
    })

def extract_playlist_id_from_url(url):
    import re
    match = re.search(r'playlist\/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid playlist URL")
