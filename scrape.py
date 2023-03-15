import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import sys

args = sys.argv[1:]


title_basics = 'https://datasets.imdbws.com/title.basics.tsv.gz'
title_episode = 'https://datasets.imdbws.com/title.episode.tsv.gz'
title_ratings = 'https://datasets.imdbws.com/title.ratings.tsv.gz'

basics = pd.read_csv(title_basics, sep='\t', header=0, usecols = ['tconst', 'titleType', 'originalTitle', 'startYear', 'runtimeMinutes'])
episode = pd.read_csv(title_episode, sep='\t', header=0, engine = 'pyarrow')
ratings = pd.read_csv(title_ratings, sep='\t', header=0, engine = 'pyarrow')

show_data = {}
basics = basics[basics['titleType'].isin(['tvSeries', 'tvEpisode'])]
shows = basics[basics['originalTitle'].isin(args)]
shows = shows[shows['titleType'] == 'tvSeries']
shows = shows.drop_duplicates(subset = 'originalTitle', keep = 'last').set_index('originalTitle')
episode = episode.set_index('parentTconst')
for show in args:
    try:
        code = shows.loc[show]['tconst']
        episodes = episode.loc[code]
        episodes = episodes.merge(basics).merge(ratings).set_index('episodeNumber')
        episodes = episodes.rename(columns={'originalTitle' : 'title'}).drop(columns=['tconst', 'titleType'])
        seasons = dict(tuple(episodes.groupby('seasonNumber')))
        seasons = {int(k) : v for k, v in seasons.items()}
        for season_num in seasons:
            seasons[season_num] = dict(tuple(seasons[season_num].groupby('episodeNumber')))
            seasons[season_num] = {int(k) : v for k,v in seasons[season_num].items()}
            for ep_num in seasons[season_num]:
                seasons[season_num][ep_num] = seasons[season_num][ep_num].to_dict(orient = 'list')
                seasons[season_num][ep_num] = {k : v[0] for k,v in seasons[season_num][ep_num].items()}
        show_data[show] = seasons
    except KeyError:
        pass


for title, title_data in show_data.items():
    plt.figure(figsize=(12,6))
    plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
    for sn, sn_data in title_data.items():
        plt.plot(list(range(1, 1 + len(sn_data))), [show_data[title][sn][ep + 1]['averageRating'] for ep in range(len(sn_data))])
    plt.ylabel('Rating')
    plt.xlabel('Episode')
    plt.title('Ratings per Episode of ' + title)
    plt.legend(['Season ' + str(n + 1) for n in range(len(title_data))])
    plt.savefig('plots/' + title + '.png')
    plt.close()
    
plt.figure(figsize=(20,5))
plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(1))
for title, title_data in show_data.items():
    ratings = []
    num_eps = 0
    for sn, sn_data in title_data.items():
        num_eps += len(sn_data.keys())
        ratings += [show_data[title][sn][ep + 1]['averageRating'] for ep in range(len(sn_data))]
    plt.plot(list(range(1, 1 + num_eps)), ratings)
plt.ylabel('Rating')
plt.xlabel('Episode')
plt.title('Ratings per Episode')
plt.legend(show_data.keys())
plt.savefig('plots/all.png')
plt.close()



