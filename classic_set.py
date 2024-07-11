import utils

def generate_classic_set(df, num_songs, first_song=None):
    sections = utils.split_into_sections(num_songs)
    if first_song is None:
        top_hype_songs = df.head(utils.TOP_HYPE_COUNT)
        first_song = top_hype_songs.sample(1).iloc[0]  # Randomly select the first song from the top hype songs
    dj_set = [first_song]
    used_songs = {first_song['Track Name']}
    
    for i in range(1, num_songs):
        compatible_songs = df[~df['Track Name'].isin(used_songs)].copy()
        
        section_idx = next(idx for idx, (start, end) in enumerate(sections) if start <= i < end)
        
        if section_idx in {0, 2, 4}:  # First, middle, and last sections
            if section_idx == 0:  # First section prioritizes danceability
                compatible_songs.loc[:, 'Score'] = 1.1 * compatible_songs['Hype'] + 0.4 * compatible_songs['Danceability'] + 1.1 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
            else:  # Middle and last sections prioritize hype more
                compatible_songs.loc[:, 'Score'] = 1.2 * compatible_songs['Hype'] + 1.3 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
        else:  # Other sections prioritize hype and compatibility
            compatible_songs.loc[:, 'Score'] = compatible_songs['Hype'] + 2.5 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
        
        next_song = compatible_songs.sort_values(by='Score', ascending=False).iloc[0]
        dj_set.append(next_song)
        used_songs.add(next_song['Track Name'])
        df = df[df['Track Name'] != next_song['Track Name']]
    
    return dj_set

def fitness_classic(dj_set):
    total_hype = sum(song['Hype'] for song in dj_set)
    transition_compatibility = sum(utils.calculate_compatibility(dj_set[i], dj_set[i + 1]) for i in range(len(dj_set) - 1))
    
    sections = utils.split_into_sections(len(dj_set))
    section_scores = 0
    for idx, (start, end) in enumerate(sections):
        if idx == 0:
            section_hype =  0.8 * sum(song['Hype'] + 0.5 * song['Danceability'] for song in dj_set[start:end])
            section_scores += 1.3 * section_hype
        else:
            section_hype = sum(song['Hype'] for song in dj_set[start:end])
            section_scores += (1.3 if idx in {2, 4} else 1) * section_hype
    
    fitness = 1.1 * total_hype + (transition_compatibility * 1) + section_scores
    return fitness, total_hype, transition_compatibility, section_scores

