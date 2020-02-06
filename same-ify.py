# -*- coding: utf-8 -*-
# <nbformat>4</nbformat>

# <codecell> {}

#!pip install pandas matplotlib seaborn spotipy

# <codecell> {}

# ********** Import Statements ************************************************************ #
import sys
import spotipy
import spotipy.util as util

import pandas as pd
import math

import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option('display.max_rows', 500)

# <codecell> {}

# Spotify user IDs for testing: these are public information.
user_ids = {'Cassie':'1242091675',
            'Caity':'12166088827',
            'Ben':'yaojxcyh5tczzlln0ygm9sfla',
            'Alex':'alex-soto',
            'Jason':'jason.albert'}

# <codecell> {}

class Sameify:
    
    def __init__(self, user_id):
        self.id = user_id
        # Connect to Spotify
        self.sp = self.spotify_connect()
        self.playlists = self.get_all_playlists() 
        #self.playlist_tracks = self.get_all_playlist_tracks(self.playlists['playlist_id'][0])
        
        
    # Spotify credentials
    scope = 'user-library-read'
    #client_id removed
    #client_secret removed
    redirect_uri = 'http://localhost:1410/'

    # Connects to Spotify
    def spotify_connect(self):
        token = util.prompt_for_user_token(self.id,
                                           self.scope,
                                           self.client_id,
                                           self.client_secret,
                                           self.redirect_uri)

        sp = spotipy.Spotify(auth=token)
        return sp
    
    #def overstep_limit(self, item_id):

    def get_playlist_id(self, playlist_name):
        return self.playlists.loc[self.playlists['playlist_name'] == playlist_name,'playlist_id'].values[0]
    
    def get_playlist_name(self, playlist_id):
        return self.playlists.loc[self.playlists['playlist_id'] == playlist_id,'playlist_name'].values[0]
    
    def playlist_tracks(self, playlist_id):
        ret_df = pd.DataFrame()
        
        playlist = self.sp.user_playlist_tracks(self.id, playlist_id)
        playlist_name = self.get_playlist_name(playlist_id)
        tracks = playlist['items']
        
        while playlist['next']:
            playlist = self.sp.next(playlist)
            tracks.extend(playlist['items'])
            
        for track in tracks:
            x = track['track']
            data = {'playlist_id'  : playlist_id,
                    'playlist_name': playlist_name,
                    'track_name'   : x['name'],
                    'track_id'     : x['id'], 
                    'track_artist' : x['artists'][0]['name'], #[artist['name'] for artist in x['artists']]
                    'added_by'     : track['added_by']['id'],
                    'added_at'     : track['added_at']
                   }
            data_df = pd.DataFrame([data])
            song_deets = pd.DataFrame(self.sp.audio_features(data['track_id']))
            
            full_data = pd.concat([data_df, song_deets],axis=1)
            
            ret_df = ret_df.append(full_data)
        ret_df.reset_index(drop=True, inplace=True)
        return ret_df
            
        
    def get_all_playlists(self):
        playlists = pd.DataFrame()
        
        total = self.sp.user_playlists(self.id)['total'] #number of playlists
        limit = 50 # pull at a time
        
        for x in range(0, total, limit): # for each set of playlists
            new_playlist = self.sp.user_playlists(self.id, limit=limit, offset=x)
            for x in new_playlist['items']:
                items = {'playlist_name': x['name'],
                         'playlist_id'  : x['id'],
                         'owner_name'   : x['owner']['display_name'],
                         'owner_id'     : x['owner']['id'],
                         'num_tracks'   : x['tracks']['total'],
                         'collaborative': x['collaborative'],
                         }
                playlists = playlists.append(pd.DataFrame([items]))
        playlists.reset_index(drop=True, inplace=True)
        return playlists

# <codecell> {}

def recursive_skim(obj, d={}, f=0):
    for x in obj.keys():
        level = obj[x]
        print(f, '\t'*f, '*', x, type(level), '[0] {}'.format(type(level[0] if type(level) == list else level)) if type(level) == list else '')
        if type(level) in (list, dict):
            level_next = level[0] if type(level) == list else level
            if type(level_next) in (list, dict):
                recursive_skim(level_next, d, f+1)

# <codecell> {}

Cassie = Sameify(user_ids['Cassie'])
Caity = Sameify(user_ids['Caity'])
Ben = Sameify(user_ids['Ben'])
Alex = Sameify(user_ids['Alex'])
Jason = Sameify(user_ids['Jason'])

# <markdowncell> {}

# # How to see playlists

# <codecell> {"scrolled": true}

playlists = Alex.get_all_playlists()
playlists

# <markdowncell> {}

# # How to see songs in a playlist

# <codecell> {"scrolled": false}

a_tracks = Alex.playlist_tracks(Alex.get_playlist_id('Desamor'))
a_tracks

# <markdowncell> {}

# # See original depth tree of playlist info

# <codecell> {}

x = Alex.sp.user_playlist(Alex.id, Alex.get_playlist_id('Desamor'))
recursive_skim(x)

# <markdowncell> {}

# # See new depth tree of playlist info
# I pulled out the values I felt were most useful, see above in the class definition

# <codecell> {}

y = Alex.playlist_tracks(Alex.get_playlist_id('Desamor'))
recursive_skim(y)

# <markdowncell> {}

# # Visualize a playlist

# <codecell> {}

# simplify and melt playlist
def melt_df(df):
    new_df = df[['playlist_name', 'track_id', 'acousticness', 'danceability', 'energy', 'liveness', 'valence', 'speechiness']]
    return new_df.melt(id_vars=['playlist_name', 'track_id'])

# <codecell> {"scrolled": true}

# melt playlist
alex_playlist_melt = melt_df(a_tracks)
alex_playlist_melt

# <codecell> {}

# display musical information
fig, ax = plt.subplots(figsize=(20,15))
ax = sns.boxplot(x='variable', y='value', hue='playlist_name', data=alex_playlist_melt, palette='Accent')

# <markdowncell> {}

# # Compare playlists

# <codecell> {}

# pull french playlist from cassie
c_tracks = Cassie.playlist_tracks(Cassie.get_playlist_id('Mes Favoris Français'))

# melt playlist
cassie_playlist_melt = melt_df(c_tracks)
cassie_playlist_melt

# <codecell> {}

melted = alex_playlist_melt.append(cassie_playlist_melt)

# display musical information
fig, ax = plt.subplots(figsize=(20,15))
ax = sns.boxplot(x='variable', y='value', hue='playlist_name', data=melted, palette='Accent')

# <codecell> {}



# <metadatacell>

{"kernelspec": {"display_name": "Python 3", "name": "python3", "language": "python"}}