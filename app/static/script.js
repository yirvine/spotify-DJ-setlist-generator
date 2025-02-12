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
        
        // Use an ordered list <ol> instead of <ul>
        const ol = document.createElement('ol');
        data.set_list.forEach((track, index) => {
            const li = document.createElement('li');
            const firstArtist = track.artist.split(',')[0].trim();  // Extract the first artist
            li.innerHTML = `<strong>${track.name} by ${firstArtist}</strong>, ${track.key} (${track.camelot_key}), ${Math.round(track.tempo)} BPM`;
            ol.appendChild(li);
        });
        setlist.appendChild(ol);
        

        const playlistLink = document.getElementById('playlist-link');
        playlistLink.href = data.new_playlist_url;
        
    } else {
        document.getElementById('loading-text').textContent = 'Error generating DJ set. Please try again.';
    }
});
