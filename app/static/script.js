document.getElementById('dj-set-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    document.getElementById('loading-text').style.display = 'block';
    document.getElementById('results').style.display = 'none';

    const formData = new FormData(this);
    const playlistURL = document.getElementById('playlist_url').value;
    if (playlistURL) {
        formData.append('playlist_url', playlistURL);
        formData.delete('playlist_id');  // Remove the playlist_id if URL is provided
    }

    const response = await fetch(this.action, {
        method: 'POST',
        body: formData,
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById('loading-text').style.display = 'none';
        document.getElementById('results').style.display = 'block';

        const setlist = document.getElementById('setlist');
        setlist.innerHTML = '';
        
        // Create a styled ordered list for the setlist
        const ol = document.createElement('ol');
        
        data.set_list.forEach((track, index) => {
            const li = document.createElement('li');
            const firstArtist = track.artist.split(',')[0].trim();  // Extract the first artist
            
            // Create a more structured HTML for each track
            li.innerHTML = `
                <div class="track-item">
                    <div class="track-main">
                        <strong class="track-name">${track.name}</strong> 
                        <span class="track-artist">by ${firstArtist}</span>
                    </div>
                    <div class="track-details">
                        <span class="track-key">${track.key} (${track.camelot_key})</span>
                        <span class="track-bpm">${Math.round(track.tempo)} BPM</span>
                    </div>
                </div>
            `;
            
            ol.appendChild(li);
        });
        
        setlist.appendChild(ol);
        
        const playlistLink = document.getElementById('playlist-link');
        playlistLink.href = data.new_playlist_url;
        
    } else {
        document.getElementById('loading-text').textContent = 'Error generating DJ set. Please try again.';
        document.getElementById('loading-text').style.color = '#e74c3c';
    }
});
