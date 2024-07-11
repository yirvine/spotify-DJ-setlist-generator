import random
import numpy as np
import classic_set
import wedding_set
import tonal_set
import riser_set
import utils

GENERATIONS=1

def compatibility_aware_crossover(parent1, parent2, df):
    num_songs = len(parent1)
    child = parent1.copy()
    
    # Swap only 1 or 2 songs
    num_swaps = random.randint(1, 2)
    for _ in range(num_swaps):
        idx = random.randint(0, num_songs - 1)
        compatible_songs = df[df.apply(lambda x: utils.calculate_compatibility(child[idx], x) > 0, axis=1)]
        if not compatible_songs.empty:
            best_song = compatible_songs.sort_values(by='Hype', ascending=False).iloc[0]
            child[idx] = best_song

    # Ensure no duplicates in the child
    track_names = set()
    unique_child = []
    for track in child:
        if track['Track Name'] not in track_names:
            unique_child.append(track)
            track_names.add(track['Track Name'])

    # If the child is not the correct length, fill in with tracks from the original df
    remaining_tracks = df[~df['Track Name'].isin(track_names)]
    while len(unique_child) < num_songs:
        next_track = remaining_tracks.sample(1).iloc[0]
        unique_child.append(next_track)
        track_names.add(next_track['Track Name'])
        remaining_tracks = remaining_tracks[remaining_tracks['Track Name'] != next_track['Track Name']]

    return unique_child

def compatibility_aware_mutation(child, original_df, probability=0.05):
    if random.random() < probability:
        idx1, idx2 = random.sample(range(1, len(child)), 2)
        # Swap only if they are compatible
        if utils.calculate_compatibility(child[idx1 - 1], child[idx2]) > 0 and utils.calculate_compatibility(child[idx2 - 1], child[idx1]) > 0:
            child[idx1], child[idx2] = child[idx2], child[idx1]
        else:
            similar_song = original_df[
                (original_df['Key'] == child[idx1]['Key']) & 
                (original_df['Mode'] == child[idx1]['Mode']) & 
                (original_df['Tempo'] > child[idx1]['Tempo'] - 5) & 
                (original_df['Tempo'] < child[idx1]['Tempo'] + 5)
            ].sample(1)
            if not similar_song.empty:
                child[idx1] = similar_song.iloc[0]
             
    return child

def ensure_uniqueness(child, original_df, num_songs):
    track_names = set()
    unique_child = []
    for track in child:
        if track['Track Name'] not in track_names:
            unique_child.append(track)
            track_names.add(track['Track Name'])
    
    # If the child is not the correct length, fill in with tracks from the original df
    remaining_tracks = original_df[~original_df['Track Name'].isin(track_names)]
    while len(unique_child) < num_songs:
        next_track = remaining_tracks.sample(1).iloc[0]
        unique_child.append(next_track)
        track_names.add(next_track['Track Name'])
        remaining_tracks = remaining_tracks[remaining_tracks['Track Name'] != next_track['Track Name']]
    return unique_child

def genetic_algorithm(df, num_songs, population_size=utils.TOP_HYPE_COUNT, generations=GENERATIONS, set_type='classic'):
    population_size = max(utils.TOP_HYPE_COUNT, population_size)
    
    if set_type == 'classic':
        fitness_function = classic_set.fitness_classic
    elif set_type == 'wedding':
        fitness_function = wedding_set.fitness_wedding
    elif set_type == 'tonal':  
        fitness_function = tonal_set.fitness_tonal
    elif set_type == 'riser':  
        fitness_function = riser_set.fitness_riser
    else:
        raise ValueError("Invalid set type. Choose 'classic', 'wedding', 'tonal', or 'riser.'")
    population = generate_initial_population(df, num_songs, population_size, set_type)
    best_overall_dj_set = None
    best_overall_fitness = -float('inf')
    
    for generation in range(generations):
        fitness_results = [fitness_function(dj_set) for dj_set in population]
        fitness_scores = [result[0] for result in fitness_results]
        
        # Track the best DJ set overall
        best_fitness = max(fitness_scores)
        best_fitness_index = np.argmax(fitness_scores)
        if best_fitness > best_overall_fitness:
            best_overall_fitness = best_fitness
            best_overall_dj_set = population[best_fitness_index]
        
        print(f"Generation {generation + 1}: Best Fitness = {best_fitness:.2f}")
        print(f"Best DJ Set of Generation {generation + 1}:")
        for idx, song in enumerate(population[best_fitness_index]):
            key_mode = utils.key_mode_to_string(song['Key'], song['Mode'])
            if idx == 0:
                print(f"\033[92m{idx + 1}. {song['Track Name']} by {song['Artist Name(s)']}\033[0m, Key: {key_mode}, Hype: {song['Hype']:.2f}, Tempo: {song['Tempo']:.1f}, Pop.: {song['Adjusted Popularity']:.2f}")
            else:
                compatibility = utils.calculate_compatibility(population[best_fitness_index][idx-1], song)
                compatibility_str = f"\033[91m{compatibility:.2f}\033[0m" if compatibility < 0 else (f"\033[94m{compatibility:.2f}\033[0m" if compatibility >= 2 else f"{compatibility:.2f}")
                print(f"\033[92m{idx + 1}. {song['Track Name']} by {song['Artist Name(s)']}\033[0m, Key: {key_mode}, Hype: {song['Hype']:.2f}, Tempo: {song['Tempo']:.1f}, Comp.: {compatibility_str}")

        # Select top-performing sets (elite selection)
        selected_population = [population[i] for i in np.argsort(fitness_scores)[-population_size:]]
        
        # Introduce a shake-up mechanism based on the fitness score
        new_population = []
        for i in range(population_size):
            parent1, parent2 = random.sample(selected_population, 2)
            if fitness_scores[i] < np.median(fitness_scores):  # If the fitness score is below the median, shake things up more
                child = compatibility_aware_crossover(parent1, parent2, df)
            else:  # Otherwise, perform more conservative swaps
                child = compatibility_aware_mutation(parent1, df, probability=0.1)
            child = ensure_uniqueness(child, df, num_songs)
            new_population.append(child)
        
        population = new_population
    
    # Print the best fitness score found in all generations
    print(f"Best Fitness in Final Population: {best_overall_fitness:.2f}")
    
    # Print the best DJ set
    for idx, song in enumerate(best_overall_dj_set):
        key_mode = utils.key_mode_to_string(song['Key'], song['Mode'])
        if idx == 0:
            print(f"\033[92m{idx + 1}. {song['Track Name']} by {song['Artist Name(s)']}\033[0m, Key: {key_mode}, Hype: {song['Hype']:.2f}, Tempo: {song['Tempo']:.1f}, Pop.: {song['Adjusted Popularity']:.2f}")
        else:
            compatibility = utils.calculate_compatibility(best_overall_dj_set[idx-1], song)
            compatibility_str = f"\033[91m{compatibility:.2f}\033[0m" if compatibility < 0 else (f"\033[94m{compatibility:.2f}\033[0m" if compatibility >= 2 else f"{compatibility:.2f}")
            print(f"\033[92m{idx + 1}. {song['Track Name']} by {song['Artist Name(s)']}\033[0m, Key: {key_mode}, Hype: {song['Hype']:.2f}, Tempo: {song['Tempo']:.1f}, Comp.: {compatibility_str}, Pop.: {song['Adjusted Popularity']:.2f}")
    
    return best_overall_dj_set

def generate_initial_population(df, num_songs, population_size, set_type):
    top_hype_songs = df.head(utils.TOP_HYPE_COUNT)
    population = []

    # Ensure each of the first TOP_HYPE_COUNT sets starts with a unique song from the top hype songs
    for i in range(min(population_size, len(top_hype_songs))):
        first_song = top_hype_songs.iloc[i]
        if set_type == 'classic':
            population.append(classic_set.generate_classic_set(df, num_songs, first_song))
        elif set_type == 'wedding':
            population.append(wedding_set.generate_wedding_set(df, num_songs, first_song))
        elif set_type == 'tonal':
            population.append(tonal_set.generate_tonal_set(df, num_songs, first_song))
        elif set_type == 'riser':
            population.append(riser_set.generate_riser_set(df, num_songs, first_song))

    # If population size is greater than TOP_HYPE_COUNT, fill the rest randomly
    while len(population) < population_size:
        first_song = top_hype_songs.sample(1).iloc[0]
        if set_type == 'classic':
            population.append(classic_set.generate_classic_set(df, num_songs, first_song))
        elif set_type == 'wedding':
            population.append(wedding_set.generate_wedding_set(df, num_songs, first_song))
        elif set_type == 'tonal':
            population.append(tonal_set.generate_tonal_set(df, num_songs, first_song))        
        elif set_type == 'riser':
            population.append(riser_set.generate_riser_set(df, num_songs, first_song))        
    return population

