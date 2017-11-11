import pandas as pd
pbp_data = pd.read_csv('data/game_data/2014111300_plays.csv')
pbp_data.sort_values(by=['drive','play'], axis=0, inplace=True)
fav = 'MIA'
spread = 4
pbp_data['scorediff'] = spread
pbp_data['scorediff'] = pbp_data.apply(lambda x: x['note']=='TD' and x+6 or x['note'] == 'XP' and x+1 or
                                 x['note']=='FG' or x['note']=='SAF' and x+3,axis=1)