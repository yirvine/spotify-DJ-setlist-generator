import utils

def generate_wedding_set(df, num_songs, first_song=None):
    df['Sum_Hype_Popularity'] = df['Hype'] + df['Adjusted Popularity']
    if first_song is None:
        top_hype_songs = df.sort_values(by='Sum_Hype_Popularity', ascending=False).head(utils.TOP_HYPE_COUNT)
        first_song = top_hype_songs.sample(1).iloc[0]  # Randomly select the first song from the top hype songs
    dj_set = [first_song]
    used_songs = {first_song['Track Name']}
    
    sections = utils.split_into_sections(num_songs)
    
    for i in range(1, num_songs):
        compatible_songs = df[~df['Track Name'].isin(used_songs)].copy()
        
        section_idx = next(idx for idx, (start, end) in enumerate(sections) if start <= i < end)
        
        if section_idx in {0, 2, 4}:  # First, middle, and last sections prioritize popularity and compatibility more
            compatible_songs.loc[:, 'Score'] = 1.2 * compatible_songs['Hype'] + 2 * compatible_songs['Adjusted Popularity'] + 2 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
        else:  # Other sections prioritize hype and compatibility
            compatible_songs.loc[:, 'Score'] = compatible_songs['Hype'] + 2 * compatible_songs['Adjusted Popularity'] + 3 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
        
        next_song = compatible_songs.sort_values(by='Score', ascending=False).iloc[0]
        dj_set.append(next_song)
        used_songs.add(next_song['Track Name'])
        df = df[df['Track Name'] != next_song['Track Name']]
    
    return dj_set

def fitness_wedding(dj_set):
    total_hype = sum(song['Hype'] for song in dj_set)
    total_popularity = sum(song['Adjusted Popularity'] for song in dj_set)
    transition_compatibility = sum(utils.calculate_compatibility(dj_set[i], dj_set[i + 1]) for i in range(len(dj_set) - 1))
    
    sections = utils.split_into_sections(len(dj_set))
    section_scores = 0
    for idx, (start, end) in enumerate(sections):
        section_hype_popularity = sum(song['Hype'] + song['Adjusted Popularity'] for song in dj_set[start:end])
        section_scores += (1.2 if idx in {0, 2, 4} else 1) * section_hype_popularity
    
    # Adjust weights to prioritize popularity and compatibility
    fitness = (total_hype * 1) + (total_popularity * 2) + (transition_compatibility * 2) + section_scores*0
    return fitness, total_hype, total_popularity, transition_compatibility, section_scores
