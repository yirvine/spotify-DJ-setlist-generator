import asyncio
import aiohttp
import time
import requests
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

scope = 'playlist-read-private playlist-read-collaborative'
sp = Spotify(auth_manager=SpotifyOAuth(scope=scope))

RATE_LIMIT_STATUS_CODE = 429
RETRY_DELAY = 5  # Seconds

async def api_call_with_retry(session, url, headers):
    retries = 0
    while True:
        try:
            async with session.get(url, headers=headers) as response:
                logger.info(f"Making request to URL: {url}")
                if response.status == RATE_LIMIT_STATUS_CODE:
                    retries += 1
                    wait_time = min(RETRY_DELAY * (2 ** retries), 600)  # Exponential backoff with a cap
                    logger.warning(f"Rate limit reached. Waiting for {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                elif response.status == 401:
                    logger.error("Unauthorized access - possibly invalid token. Exiting.")
                    raise aiohttp.ClientError("Unauthorized access.")
                else:
                    response.raise_for_status()
                    logger.info(f"Response received with status code: {response.status}")
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            raise e

async def fetch_audio_features(track_ids, access_token):
    features = []
    headers = {'Authorization': f'Bearer {access_token}'}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(0, len(track_ids), 100):
            batch_ids = ','.join(track_ids[i:i+100])
            url = f'https://api.spotify.com/v1/audio-features?ids={batch_ids}'
            logger.info(f"Fetching audio features for batch {i//100 + 1}")
            tasks.append(api_call_with_retry(session, url, headers))
        results = await asyncio.gather(*tasks)
        for result in results:
            features.extend(result['audio_features'])
    return features

async def get_playlist_tracks(playlist_id, access_token):
    tracks = []
    offset = 0
    headers = {'Authorization': f'Bearer {access_token}'}
    async with aiohttp.ClientSession() as session:
        while True:
            url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit=100'
            logger.info(f"Fetching playlist tracks with offset {offset}")
            response = await api_call_with_retry(session, url, headers)
            tracks.extend([item['track']['id'] for item in response['items']])
            offset += len(response['items'])
            if len(response['items']) == 0:
                break
    return tracks

async def get_track_details(track_ids, access_token):
    track_details = []
    headers = {'Authorization': f'Bearer {access_token}'}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(0, len(track_ids), 50):
            batch_ids = ','.join(track_ids[i:i+50])
            url = f'https://api.spotify.com/v1/tracks?ids={batch_ids}'
            logger.info(f"Fetching track details for batch {i//50 + 1}")
            tasks.append(api_call_with_retry(session, url, headers))
        results = await asyncio.gather(*tasks)
        for result in results:
            track_details.extend(result['tracks'])
    return track_details

async def get_track_genres(artist_ids, access_token):
    genres = []
    headers = {'Authorization': f'Bearer {access_token}'}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(0, len(artist_ids), 50):
            batch_ids = ','.join(artist_ids[i:i+50])
            url = f'https://api.spotify.com/v1/artists?ids={batch_ids}'
            logger.info(f"Fetching artist details for batch {i//50 + 1}")
            tasks.append(api_call_with_retry(session, url, headers))
        results = await asyncio.gather(*tasks)
        for result in results:
            for artist in result['artists']:
                genres.append({
                    'id': artist['id'],
                    'genres': artist['genres']
                })
    return genres
