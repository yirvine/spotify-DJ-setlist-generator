document.getElementById('dj-set-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    // Reset the loading text to its original message
    document.getElementById('loading-text').textContent = 'Generating DJ set...';
    document.getElementById('loading-text').style.display = 'block';
    document.getElementById('results').style.display = 'none';

    const formData = new FormData(this);
    const playlistURL = document.getElementById('playlist_url').value;
    if (playlistURL) {
        formData.append('playlist_url', playlistURL);
        formData.delete('playlist_id');  // Remove the playlist_id if URL is provided
    }

    const playlistID = formData.get('playlist_id');
    const numSongs = parseInt(formData.get('num_songs'));

    // Check if numSongs is less than 3
    if (!numSongs || numSongs < 3) {
        document.getElementById('loading-text').textContent = 'We need at least 3 songs for a DJ set.';
        return;
    }

    // Fetch the playlist data to get the number of available tracks
    const playlistResponse = await fetch(`/get_playlist_tracks?playlist_id=${playlistID}`);
    if (playlistResponse.ok) {
        const playlistData = await playlistResponse.json();
        const availableTracks = playlistData.total_tracks;

        if (numSongs > availableTracks) {
            document.getElementById('loading-text').textContent = `Error: The number of requested songs (${numSongs}) exceeds the available songs in the playlist (${availableTracks}).`;
            return;
        }
    } else {
        document.getElementById('loading-text').textContent = 'Error fetching playlist data. Please try again.';
        return;
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

// Restrict the text field for number of songs to be numeric only
document.getElementById('num_songs').addEventListener('input', function(event) {
    this.value = this.value.replace(/[^0-9]/g, '');
});

// document.getElementById('dj-set-form').addEventListener('submit', async function(event) {
//     event.preventDefault();
//     document.getElementById('loading-text').style.display = 'block';
//     document.getElementById('results').style.display = 'none';

//     const formData = new FormData(this);
//     const playlistURL = document.getElementById('playlist_url').value;
//     if (playlistURL) {
//         formData.append('playlist_url', playlistURL);
//         formData.delete('playlist_id');  // Remove the playlist_id if URL is provided
//     }

//     const response = await fetch(this.action, {
//         method: 'POST',
//         body: formData,
//     });

//     if (response.ok) {
//         const data = await response.json();
//         document.getElementById('loading-text').style.display = 'none';
//         document.getElementById('results').style.display = 'block';

//         const setlist = document.getElementById('setlist');
//         setlist.innerHTML = '';
        
//         // Use an ordered list <ol> instead of <ul>
//         const ol = document.createElement('ol');
//         data.set_list.forEach((track, index) => {
//             const li = document.createElement('li');
//             const firstArtist = track.artist.split(',')[0].trim();  // Extract the first artist
//             li.innerHTML = `<strong>${track.name} by ${firstArtist}</strong>, ${track.key} (${track.camelot_key}), ${Math.round(track.tempo)} BPM`;
//             ol.appendChild(li);
//         });
//         setlist.appendChild(ol);
        
//         const playlistLink = document.getElementById('playlist-link');
//         playlistLink.href = data.new_playlist_url;
        
//     } else {
//         document.getElementById('loading-text').textContent = 'Error generating DJ set. Please try again.';
//     }
// });
