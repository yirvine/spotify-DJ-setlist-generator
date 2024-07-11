from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import asyncio
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from dj_functions import generate_dj_set
from flask import send_from_directory
from spotipy.cache_handler import CacheFileHandler

load_dotenv()

bp = Blueprint('main', __name__)

def create_spotify_oauth():
    cache_path = session.get('cache_path')
    if not cache_path:
        cache_path = f".cache-{os.urandom(24).hex()}"
        session['cache_path'] = cache_path

    cache_handler = CacheFileHandler(cache_path=cache_path)
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIPY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
        scope='playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private',
        cache_handler=cache_handler,
        show_dialog=True
    )


# def create_spotify_oauth():
#     cache_handler = CacheFileHandler(cache_path=session.get('cache_path'))
#     return SpotifyOAuth(
#         client_id=os.getenv('SPOTIPY_CLIENT_ID'),
#         client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
#         redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
#         scope='playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private',
#         cache_handler=cache_handler
#     )

@bp.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@bp.route('/')
def home():
    return render_template('home.html')

# @bp.route('/login')
# def login():
#     session.clear()  # Clear the session before a new login attempt
#     session['cache_path'] = f".cache-{os.urandom(24).hex()}"  # Generate unique cache path
#     sp_oauth = create_spotify_oauth()
#     auth_url = sp_oauth.get_authorize_url()
#     return redirect(auth_url)

@bp.route('/login')
def login():
    print("Login route accessed. Clearing session.")
    session.clear()  # Clear the session before a new login attempt
    session['cache_path'] = f".cache-{os.urandom(24).hex()}"  # Generate unique cache path
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(f"Redirecting to: {auth_url}")
    return redirect(auth_url)

@bp.route('/logout')
def logout():
    print("Logout route accessed. Clearing session.")
    cache_path = session.get('cache_path')
    if cache_path and os.path.exists(cache_path):
        os.remove(cache_path)  # Remove cache file

    session.clear()  # Clear the session
    print("Logged out, session cleared")
    return redirect(url_for('main.home'))


@bp.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    try:
        token_info = sp_oauth.get_access_token(request.args['code'])
        session['token_info'] = token_info
        print(f"Callback received token: {token_info}")  # Debugging information
        return redirect(url_for('main.playlists'))
    except Exception as e:
        print(f"Error in callback: {e}")
        return redirect(url_for('main.login'))


# @bp.route('/callback')
# def callback():
#     sp_oauth = create_spotify_oauth()
#     try:
#         token_info = sp_oauth.get_access_token(request.args['code'])
#         session['token_info'] = token_info
#         return redirect(url_for('main.playlists'))
#     except Exception as e:
#         print(f"Error in callback: {e}")
#         return redirect(url_for('main.login'))

@bp.route('/playlists')
def playlists():
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for('main.login'))

    access_token = token_info['access_token']
    sp = Spotify(auth=access_token)
    try:
        playlists = sp.current_user_playlists(limit=50)
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


@bp.route('/get_playlist_tracks')
def get_playlist_tracks():
    playlist_id = request.args.get('playlist_id')
    token_info = session.get("token_info", None)
    if not token_info:
        return jsonify({"error": "No token info"}), 401

    access_token = token_info['access_token']
    sp = Spotify(auth=access_token)
    try:
        playlist = sp.playlist(playlist_id)
        total_tracks = playlist['tracks']['total']
        return jsonify({"total_tracks": total_tracks})
    except Exception as e:
        print(f"Error fetching playlist data: {e}")
        return jsonify({"error": "Error fetching playlist data"}), 500
















# from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
# import asyncio
# import os
# from spotipy import Spotify
# from spotipy.oauth2 import SpotifyOAuth
# from dotenv import load_dotenv
# from dj_functions import generate_dj_set
# from flask import send_from_directory
# from spotipy.cache_handler import FlaskSessionCacheHandler

# load_dotenv()

# bp = Blueprint('main', __name__)

# sp_oauth = SpotifyOAuth(client_id=os.getenv('SPOTIPY_CLIENT_ID'),
#                         client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
#                         redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
#                         scope='playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private')

# @bp.route('/static/<path:filename>')
# def static_files(filename):
#     return send_from_directory('static', filename)


# @bp.route('/')
# def home():
#     token_info = session.get("token_info", None)
#     if token_info:
#         print(f"Token Info in Home: {token_info}")
#     return render_template('home.html')

# @bp.route('/login')
# def login():
#     auth_url = sp_oauth.get_authorize_url()
#     print(f"Auth URL: {auth_url}")  # Diagnostic print
#     return redirect(auth_url)

# def get_spotify_oauth():
#     return SpotifyOAuth(
#         client_id=os.getenv('SPOTIPY_CLIENT_ID'),
#         client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
#         redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
#         scope='playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private',
#         cache_handler=FlaskSessionCacheHandler(session)
#     )

# @bp.route('/callback')
# def callback():
#     sp_oauth = get_spotify_oauth()
#     code = request.args.get('code')
    
#     if not code:
#         return "Missing code parameter", 400

#     try:
#         token_info = sp_oauth.get_access_token(code)
#         print("Token info received:", token_info)
#     except Exception as e:
#         print("Error getting token info:", e)
#         return "Error getting token info", 500

#     if not token_info:
#         return "Failed to receive token info", 400

#     session['token_info'] = token_info
#     print("Session updated with token info:", session.get('token_info'))
#     return redirect(url_for('main.playlists'))


# @bp.route('/playlists')
# def playlists():
#     token_info = session.get("token_info", None)
#     if not token_info:
#         print("No token info in session, redirecting to login")
#         return redirect(url_for('main.login'))

#     access_token = token_info['access_token']
#     sp = Spotify(auth=access_token)
#     try:
#         playlists = sp.current_user_playlists(limit=50)
#         print(f"Playlists fetched: {playlists['items']}")
#     except Exception as e:
#         print(f"Error fetching playlists: {e}")
#         return "Error fetching playlists", 500

#     return render_template('playlists.html', playlists=playlists['items'])


# @bp.route('/generate', methods=['POST'])
# def generate_dj_set_route():
#     token_info = session.get("token_info", None)
#     if not token_info:
#         return redirect(url_for('main.login'))

#     access_token = token_info['access_token']
#     original_playlist_url = request.form.get('playlist_url')
#     playlist_id = request.form.get('playlist_id')
#     num_songs = int(request.form['num_songs'])
#     set_type = int(request.form['set_type'])

#     if original_playlist_url:
#         playlist_id = extract_playlist_id_from_url(original_playlist_url)

#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     track_info, new_playlist_url, fitness, total_hype, transition_compatibility, section_scores = loop.run_until_complete(
#         generate_dj_set(playlist_id, num_songs, set_type, access_token)
#     )

#     return jsonify({
#         'set_list': track_info,
#         'new_playlist_url': new_playlist_url,
#         'fitness': fitness,
#         'total_hype': total_hype,
#         'transition_compatibility': transition_compatibility,
#         'section_scores': section_scores
#     })

# def extract_playlist_id_from_url(url):
#     import re
#     match = re.search(r'playlist\/([a-zA-Z0-9]+)', url)
#     if match:
#         return match.group(1)
#     else:
#         raise ValueError("Invalid playlist URL")















# def get_spotify_oauth():
#     return SpotifyOAuth(
#         client_id=SPOTIPY_CLIENT_ID,
#         client_secret=SPOTIPY_CLIENT_SECRET,
#         redirect_uri=SPOTIPY_REDIRECT_URI,
#         scope=scope,
#         cache_handler=FlaskSessionCacheHandler(session)
#     )

# @bp.route('/callback')
# def callback():
#     session.clear()
#     code = request.args.get('code')
#     print("Code received:", code)
    
#     if not code:
#         return "Missing code parameter", 400

#     try:
#         token_info = sp_oauth.get_access_token(code)
#         print("Token info received:", token_info)
#     except Exception as e:
#         print("Error getting token info:", e)
#         return "Error getting token info", 500

#     if not token_info:
#         return "Failed to receive token info", 400

#     session["token_info"] = token_info
#     print("Session updated with token info:", session.get("token_info"))
#     return redirect(url_for('main.playlists'))

# @bp.route('/playlists')
# def playlists():
#     token_info = session.get("token_info", None)
#     if not token_info:
#         print("No token info in session, redirecting to login")
#         return redirect(url_for('main.login'))
#     print(f"Using token info: {token_info}")
#     sp = Spotify(auth=token_info['access_token'])
#     try:
#         playlists = sp.current_user_playlists()
#         print(f"Playlists fetched: {playlists['items']}")
#     except Exception as e:
#         print(f"Error fetching playlists: {e}")
#         return "Error fetching playlists", 500

#     return render_template('playlists.html', playlists=playlists['items'])



# @bp.route('/playlists')
# def playlists():
#     token_info = session.get("token_info", None)
#     if not token_info:
#         print("No token info in session, redirecting to login")
#         return redirect(url_for('main.login'))

#     print(f"Using token info: {token_info}")
#     sp = Spotify(auth=token_info['access_token'])
#     try:
#         # Use the new API call to fetch the current user's playlists
#         playlists = sp.current_user_playlists(limit=50)
#         print(f"Playlists fetched: {playlists['items']}")
#     except Exception as e:
#         print(f"Error fetching playlists: {e}")
#         return "Error fetching playlists", 500

#     return render_template('playlists.html', playlists=playlists['items'])
