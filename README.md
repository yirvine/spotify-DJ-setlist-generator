# DJ Set Generator Web App 🎵

## Overview
The **DJ Set Generator Web App** transforms Spotify playlists into professionally sequenced DJ sets using machine learning optimization. Users can either select from their saved Spotify playlists or input any public playlist URL, providing a flexible pool of tracks to work with. The app then analyzes this track pool, extracting musical features via Spotify's API, and constructs an optimized setlist of your specified length.

Each generated set is crafted using algorithms that consider key compatibility, energy progression, and beat matching—taking the heavy lifting out of DJ set preparation. The result? A perfectly curated setlist saved to your Spotify account. 

The app is built with **Flask** (Python) for the backend, integrates with **Spotify's Web API** via Spotipy, and is deployed on **AWS EC2**.

> ⚠️ **Note**: As of December 2024, Spotify has unfortunately discontinued 
their Web API for non-production apps. The demo below showcases the app in action during its operational period.

## ⚡ Demo in Action
![Demo of DJ Set Generator](./screenshots/demo-small.gif)

> **What's happening here?** The demo showcases two different algorithmic approaches to playlist generation:
> 1. A **Classic Set** optimizing for tonal compatibility and consistent high energy, perfect for tech house and similar genres where maintaining the groove is crucial
> 2. A **Riser Set** that intelligently builds energy throughout the sequence, using Spotify's audio features (energy, danceability) to create a gradually intensifying experience, while maintaining a reasonable level of tonal compatibility
>
> Both algorithms analyze track compatibility and extract audio features via Spotify's Web API, but each serves a distinct purpose in the art of setlist curation. 🎛️

## Screenshots
![Home Screen](./screenshots/home-screen.png)
![Set Generator](./screenshots/set-generator.png)

## Features
- 🎧 **Spotify Login**: Users authenticate via Spotify OAuth.
- 📜 **Playlist Selection**: Fetches and displays the user's Spotify playlists.
- 🔍 **Custom Set Generation**: Generates a DJ set based on playlist tracks.
- 🎼 **Set Optimization**: ML-based optimization for transitions, energy, and key compatibility.
- 🎵 **Playlist Creation**: Automatically creates the set as a new playlist in Spotify.
- 🌐 **Deployed on AWS EC2**.

## Tech Stack
| Component       | Technology Used |
|----------------|----------------|
| **Frontend**   | HTML, CSS, JavaScript |
| **Backend**    | Flask (Python) |
| **Database**   | N/A (Uses Spotify API) |
| **Auth**       | Spotify OAuth |
| **ML/Optimization** | Genetic Algorithm for DJ set optimization |
| **Deployment** | AWS EC2 |

## Installation & Setup
### 1️⃣ Clone the repository


```bash
git clone https://github.com/yirvine/spotify-DJ-setlist-generator.git
cd spotify-DJ-setlist-generator
```
### 2️⃣ Set up a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate


### 3️⃣ Install dependencies
pip install -r requirements.txt

### 4️⃣ Set up the .env file
Create a .env file in the project root and add your Spotify API credentials:
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000/callback
FLASK_SECRET_KEY=your-key
FLASK_DEBUG=True

5️⃣ Run the app
flask run
Then, open http://127.0.0.1:5000/ in your browser.

# Usage
1. Click "Get Started" to log in via Spotify.
2. Select a playlist or paste a Spotify playlist link.
3. Choose the number of tracks and set style.
4. Click "Generate DJ Set" to create your optimized setlist.
5. View the generated playlist or click the Spotify link to listen.

# Deployment on AWS EC2
This app is deployed on an AWS EC2 instance using:
- Ubuntu Server
- Flask
- Gunicorn (optional)
- Nginx (optional for production)

  
#### To deploy:
scp -i your-key.pem -r * ec2-user@your-ec2-ip:/home/ec2-user/dj-set-generator
ssh -i your-key.pem ec2-user@your-ec2-ip

#### Then run:
flask run --host=0.0.0.0
Access via http://your-ec2-ip:5000.

## Issues & Debugging
Login Loop? → Clear cache & delete .cache-* files.
Invalid Redirect URI? → Ensure the URI in Spotify Developer Dashboard matches http://127.0.0.1:5000/callback.
Playlists Not Showing? → Ensure correct Spotify OAuth Scopes are used.

## Future Improvements
🎭 Mobile UI Optimization
🤖 AI-based Playlist Mixing
�� Docker Deployment
🔄 Better Caching for Token Handling

## License
MIT License. Free to use & modify.


