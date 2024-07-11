import utils

def generate_riser_set(df, num_songs, first_song=None):
    sections = utils.split_into_sections(num_songs)
    if first_song is None:
        top_hype_songs = df.head(utils.TOP_HYPE_COUNT)
        first_song = top_hype_songs.sample(1).iloc[0]  # Randomly select the first song from the top hype songs
    dj_set = [first_song]
    used_songs = {first_song['Track Name']}
    
    for i in range(1, num_songs):
        compatible_songs = df[~df['Track Name'].isin(used_songs)].copy()
        
        section_idx = next(idx for idx, (start, end) in enumerate(sections) if start <= i < end)
        
        if section_idx in {0}:  # First section
            compatible_songs.loc[:, 'Score'] = (0 * compatible_songs['Hype'] 
            + 1 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
            + 1 * compatible_songs.apply(lambda x: utils.calculate_hype_compatibility(dj_set[-1], x), axis=1)
            )
        elif section_idx in {1}:  # Middle and last sections
            compatible_songs.loc[:, 'Score'] = (0.5 * compatible_songs['Hype']
            + 1 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
            + 1 * compatible_songs.apply(lambda x: utils.calculate_hype_compatibility(dj_set[-1], x), axis=1) 
            ) 
        elif section_idx in {2}:  # Middle and last sections
            compatible_songs.loc[:, 'Score'] = (1.0 * compatible_songs['Hype']
            + 1 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
            + 1 * compatible_songs.apply(lambda x: utils.calculate_hype_compatibility(dj_set[-1], x), axis=1) 
            )     
        elif section_idx in {3}:  # Middle and last sections
            compatible_songs.loc[:, 'Score'] = (1.3 * compatible_songs['Hype']
            + 1 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
            + 1 * compatible_songs.apply(lambda x: utils.calculate_hype_compatibility(dj_set[-1], x), axis=1) 
            )     
        else:  # Other sections prioritize compatibility even more
            compatible_songs.loc[:, 'Score'] = (2.6 * compatible_songs['Hype']
            + 1 * compatible_songs.apply(lambda x: utils.calculate_compatibility(dj_set[-1], x), axis=1)
            + 1 * compatible_songs.apply(lambda x: utils.calculate_hype_compatibility(dj_set[-1], x), axis=1)
            )  
        
        next_song = compatible_songs.sort_values(by='Score', ascending=False).iloc[0]
        dj_set.append(next_song)
        used_songs.add(next_song['Track Name'])
        df = df[df['Track Name'] != next_song['Track Name']]
    
    return dj_set

def fitness_riser(dj_set):
    total_hype = sum(song['Hype'] for song in dj_set)
    transition_compatibility = sum(utils.calculate_compatibility(dj_set[i], dj_set[i + 1]) for i in range(len(dj_set) - 1))
    hype_compatibility = sum(utils.calculate_hype_compatibility(dj_set[i], dj_set[i + 1]) for i in range(len(dj_set) - 1))
    
    sections = utils.split_into_sections(len(dj_set))
    section_scores = 0
    for idx, (start, end) in enumerate(sections):

        if idx == 0:  # First section
            section_hype = 0 * sum(song['Hype'] for song in dj_set[start:end])
            section_compatibility = sum(utils.calculate_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1)) + 1.3*sum(utils.calculate_hype_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1))
            section_scores += section_hype + section_compatibility
        elif idx in {1}:  
            section_hype = 0.4 * sum(song['Hype'] for song in dj_set[start:end])
            section_compatibility = sum(utils.calculate_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1)) + 1.3*sum(utils.calculate_hype_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1))
            section_scores += section_hype + section_compatibility
        elif idx in {2}:  
            section_hype = 1.0 * sum(song['Hype'] for song in dj_set[start:end])
            section_compatibility = sum(utils.calculate_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1)) + 1.3*sum(utils.calculate_hype_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1))
            section_scores += section_hype + section_compatibility
        elif idx in {3}:  
            section_hype = 1.3 * sum(song['Hype'] for song in dj_set[start:end])
            section_compatibility = sum(utils.calculate_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1)) + 1.2*sum(utils.calculate_hype_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1))
            section_scores += section_hype + section_compatibility
        else:  # last section
            section_hype = 2.6 * sum(song['Hype'] for song in dj_set[start:end])
            section_compatibility = sum(utils.calculate_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1)) + 1.1*sum(utils.calculate_hype_compatibility(dj_set[i], dj_set[i + 1]) for i in range(start, end - 1))
            section_scores += section_compatibility
    
    fitness = 1.0 * total_hype + (transition_compatibility) + hype_compatibility + section_scores
    # todo: maybe we RETURN hype compat? or just have it do stuff under the hood without passing the variable? 
    return fitness, total_hype, transition_compatibility, section_scores
