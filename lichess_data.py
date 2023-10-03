import pandas as pd
import matplotlib.pyplot as plt
chess = pd.read_csv('/Users/aidanolson/Desktop/Stuff/Data/Lichess/raw_game_data.csv')

# Most of this is just reogranization so I can make a new column and group by more vague opening names rather than specific variations.
chess[['time_control', 'increment']] = chess['increment_code'].str.split('+', n=1, expand=True)

chess.insert(chess.columns.get_loc('increment_code'), 'time_control', chess.pop('time_control'))
chess.insert(chess.columns.get_loc('increment_code'), 'increment', chess.pop('increment'))
chess['time_control'] = chess['time_control'].astype(int)
chess['increment'] = chess['increment'].astype(int)

opening_series_copy = chess['opening_name'] # for syntax purposes
replace_function = lambda x: "Queen's_Pawn" if "Queen's Pawn" in x else ("Queen's_Gambit" if "Queen's Gambit" in x else ("Queen's_Indian" if "Queen's Indian" in x else x))

chess['opening_name'] = chess['opening_name'].apply(replace_function)


unique_frequency = chess.groupby('opening_name')['opening_name'].value_counts()
unique_df = pd.DataFrame(unique_frequency)
unique_df.reset_index(inplace=True)
unique_df[['first_opening_name', 'rest_opening_name']] = unique_df['opening_name'].str.split(' ', n=1, expand=True)


general_unique_df = unique_df.groupby('first_opening_name')['count'].sum().reset_index()


general_unique_df['opening_name'] = None
for index in general_unique_df.index:
    df = unique_df[unique_df['first_opening_name'] == general_unique_df['first_opening_name'][index]].reset_index()
    opening = df['opening_name'][0]
    general_unique_df['opening_name'][index] = opening

opening_zip = zip(general_unique_df['first_opening_name'], general_unique_df['opening_name'])
opening_dict = dict(opening_zip)

chess[['first_opening_name', 'rest_opening_name']] = chess['opening_name'].str.split(' ', n=1, expand=True)
chess['general_opening'] = chess['first_opening_name']

for index in chess.index:
    if chess['general_opening'][index] == "Queen's_Pawn":
        chess['general_opening'][index] = "Queen's Pawn Game"
    elif chess['general_opening'][index] == "Queen's_Indian":
        chess['general_opening'][index] = "Queen's Indian Defense"
    elif chess['general_opening'][index] == "Queen's_Gambit":
        chess['general_opening'][index] = "Queen's Gambit"
    else:
        chess['general_opening'][index] = opening_dict[chess['general_opening'][index]]

chess = chess[['opening_name', 'general_opening', 'rated', 'turns', 'victory_status', 'winner', 'time_control', 'increment', 'increment_code', 'white_id', 'white_rating', 'black_id', 'black_rating', 'moves', 'opening_eco','opening_ply']]
chess['opening_name'] = opening_series_copy


frequency_zip = zip(general_unique_df['opening_name'], general_unique_df['count'])
frequency_dict = dict(frequency_zip)


chess['frequency'] = None
for index in chess.index:
    i = chess['general_opening'][index]
    if i == "Queen's Pawn Game":
        i = "Queen's_Pawn"
    if i == "Queen's Indian Defense":
        i = "Queen's_Indian"
    if i == "Queen's Gambit":
        i = "Queen's_Gambit"
    item = frequency_dict[i]
    chess['frequency'][index] = item

chess.to_csv('lichess_data_cleaned.csv')

chess_openings = chess[chess['frequency'] >= 500]
chess_openings = chess_openings[((chess_openings['white_rating'] >= 1000) & (chess_openings['white_rating'] <= 1100)) & ((chess_openings['black_rating'] >= 1000) & (chess_openings['black_rating'] <= 1100))]
bar_y = chess_openings.groupby('general_opening')['frequency'].mean().sort_values(ascending=False)

# Top 8 Openings graph
ax = bar_y.plot(kind='bar')
ax.set_xlabel('Opening')
ax.set_ylabel('Occurrence Frequency')
ax.set_title('Occurrences of Chess Openings on lichess.com rating between (1000 - 1100)')
ax.set_xticklabels(bar_y.index, rotation=90) # Vertical bar names for openings


# Common Variations of Top Openings
sicilian = chess[chess['general_opening'] == 'Sicilian Defense']
sicilian_graph = sicilian.value_counts('opening_name').head(10).plot(kind='bar')

QPG = chess[chess['general_opening'] == "Queen's Pawn Game"]
QPG_graph = QPG.value_counts('opening_name').head(10).plot(kind='bar')