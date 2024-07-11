import pandas as pd
import numpy as np
import re

KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
TOP_HYPE_COUNT = 100
SONG_POOL = 400

def load_csv(file_path):
    df = pd.read_csv(file_path)
    df.dropna(subset=['Track Name', 'Artist Name(s)'], inplace=True)
    df = df[~df['Track Name'].str.contains('nan', case=False, na=False)]
    df = df[~df['Artist Name(s)'].str.contains('nan', case=False, na=False)]
    return df

def calculate_hype(df):
    df['Hype'] = (1.35 * df['Danceability']) + (1.25 * df['Energy']) - (df['Acousticness'] / 2)
    return df.sort_values(by='Hype', ascending=False).head(SONG_POOL)

def extract_year(release_date):
    match = re.search(r'\b\d{4}\b', release_date)
    if match:
        return int(match.group(0))
    return None

def adjust_popularity(df):
    df['Year'] = df['Release Date'].apply(extract_year)
    df['C_Flag'] = df['Genres'].apply(lambda x: 1 if 'canadian' in str(x).lower() else 0)
    df['Adjusted Popularity'] = ((df['Popularity'] / 40) - ((df['Year'] - 2000) / 60) + df['C_Flag'])
    return df

def is_key_compatible(song1, song2):
    k1, m1 = song1['Key'], song1['Mode']
    k2, m2 = song2['Key'], song2['Mode']
    
    if (k2 == k1) and (m2 == m1):
        return 1.65
    if (k2 == (k1 + 7) % 12) and (m2 == m1):
        return 1.65
    if m1 == 1 and (k2 == (k1 + 9) % 12) and (m2 == 0):
        return 1.65
    if m1 == 0 and (k2 == (k1 + 3) % 12) and (m2 == 1):
        return 1.65
    # Check if transposing up by one semitone makes it compatible
    k1_transposed = (k1 + 1) % 12
    if (k2 == k1_transposed) and (m2 == m1):
        return 0.55
    if (k2 == (k1_transposed + 7) % 12) and (m2 == m1):
        return 0.45
    if m1 == 1 and (k2 == (k1_transposed + 9) % 12) and (m2 == 0):
        return 0.45
    if m1 == 0 and (k2 == (k1_transposed + 3) % 12) and (m2 == 1):
        return 0.45
    return 0

def calculate_compatibility(song1, song2):
    tempo1, tempo2 = song1['Tempo'], song2['Tempo']
    avg_tempo = 127  # typical average tempo to normalize the difference

    # Normalize the tempo difference based on the average tempo
    tempo_diff = abs(tempo1 - tempo2) / ((tempo1 + tempo2) / 2 / avg_tempo)
    tempo_diff = min(tempo_diff, abs(tempo1 * 2 - tempo2) / ((tempo1 * 2 + tempo2) / 2 / avg_tempo), abs(tempo1 - tempo2 * 2) / ((tempo1 + tempo2 * 2) / 2 / avg_tempo))

    tempo_score = 1.0 - ((tempo_diff**1.8) / 20)
    key_score = is_key_compatible(song1, song2)
    compatibility_score = tempo_score + key_score
    
    # Cap the negative penalty
    if compatibility_score < -5:
        compatibility_score = -5
    
    return compatibility_score

def calculate_hype_compatibility(song1, song2):
    hype1, hype2 = song1['Hype'], song2['Hype']

    hype_diff = hype2 - hype1

    hype_compatibility_score = 2.5 * (1-abs(hype_diff))
    
    if hype_diff < 0:
       hype_compatibility_score += hype_diff

    return hype_compatibility_score

def key_mode_to_string(key, mode):
    key_str = KEYS[key]
    mode_str = 'm' if mode == 0 else ''
    return f"{key_str}{mode_str}"

def split_into_sections(num_songs, num_sections=5):
    section_size = num_songs // num_sections
    extra_songs = num_songs % num_sections

    sections = []
    start_idx = 0
    for i in range(num_sections):
        end_idx = start_idx + section_size + (1 if i < extra_songs else 0)
        sections.append((start_idx, end_idx))
        start_idx = end_idx

    return sections

def convert_to_camelot(key, mode):
    camelot_map = {
        (0, 1): '8B', (0, 0): '5A',
        (1, 1): '3B', (1, 0): '12A',
        (2, 1): '10B', (2, 0): '7A',
        (3, 1): '5B', (3, 0): '2A',
        (4, 1): '12B', (4, 0): '9A',
        (5, 1): '7B', (5, 0): '4A',
        (6, 1): '2B', (6, 0): '11A',
        (7, 1): '9B', (7, 0): '6A',
        (8, 1): '4B', (8, 0): '1A',
        (9, 1): '11B', (9, 0): '8A',
        (10, 1): '6B', (10, 0): '3A',
        (11, 1): '1B', (11, 0): '10A'
    }
    return camelot_map.get((key, mode), 'Unknown')
