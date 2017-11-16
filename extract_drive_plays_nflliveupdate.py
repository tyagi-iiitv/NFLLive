import pandas as pd
import csv
import json
import requests
from time import sleep
import os.path
from xml.etree import ElementTree


# ---------------------------------------------------------------------------- #
#   Get all the eid with assigned season and weeks
# ---------------------------------------------------------------------------- #

# Check:
# 1. Regular weeks are all valid in season
# 2. Post weeks are okay
# 3. Stop at the latest week
# 4. Save to dataframe

# season = range(2013, 2018)
# regular_weeks = range(1,18)
# print regular_weeks
# post_weeks = [x for x in xrange(18, 23) if x != 21] # 21 is blank, xrange is a generator, not a list, efficient and lazy
# # print post_weeks
#
#
# matches = pd.DataFrame()
# for s in season:
#     for r in regular_weeks:
#         res = requests.get("http://www.nfl.com/ajax/scorestrip?season=" + str(s)+ "&seasonType=REG&week=" + str(r))
#         root = ElementTree.fromstring(res.content)
#         gms = root.find('gms')
#         if gms is not None:
#             for g in gms:
#                 game = pd.Series([g.attrib['eid'], s, r, g.attrib['h'], g.attrib['v'], g.attrib['hs'], g.attrib['vs'], g.attrib['d'], g.attrib['t']])
#                 matches = matches.append(game, ignore_index=True)
#         else:
#             print "Invalid week"
#             print s, r
#     for p in post_weeks:
#         res = requests.get("http://www.nfl.com/ajax/scorestrip?season=" + str(s)+ "&seasonType=POST&week=" + str(p))
#         root = ElementTree.fromstring(res.content)
#         gms = root.find('gms')
#         if gms is not None:
#             for g in gms:
#                 game = pd.Series([g.attrib['eid'], s, p, g.attrib['h'], g.attrib['v'], g.attrib['hs'], g.attrib['vs'], g.attrib['d'], g.attrib['t']])
#                 matches = matches.append(game, ignore_index=True)
#         else:
#             print "Invalid week"
#             print s, p
# # Write to csv
# columns = {0:'eid', 1:'season', 2:'week', 3:'Home', 4:'Away', 5:'HomeScore', 6:'AwayScore', 7:'Day', 8:'Time'}
# matches.rename(columns=columns, inplace=True)
# matches.to_csv('data/game_data/matches_eid_season_week.csv', index=False)


# ---------------------------------------------------------------------------- #
#   Extract game data with given eid
#   - Fields parse from each 'play'
#     'drive',
#     'play',
#     'down',
#     'time',
#     'desc',
#     'ydstogo',
#     'qtr',
#     'ydsnet',
#     'yrdln',
#     'sp',
#     'posteam': offensive team
#     'note': Conclusion of each play
# ---------------------------------------------------------------------------- #
# match_ids = pd.read_csv('data/game_data/pbp-2013_17.csv',usecols=['GameId'])
eids = pd.read_csv('data/game_data/matches_eid_season_week.csv')
print eids.head()
# print (eids['season'] < 2017)
# eids = eids[(eids['season'] < 2017) | (eids['season'] == 2017 & eids['week'] <= 10)]
eids = eids[(eids['season'] < 2017)]
print 'num of eid:', eids.count()
for i, match in enumerate(list(set(eids['eid']))):
    match_id = str(match)
    colnames_plays = ['drive','play','down','time','desc','ydstogo','qtr','ydsnet','yrdln','sp','posteam','note']
    colnames_drives = ['drive','fds','result','penyds','ydsgained','numplays','postime']
    file_plays = 'data/game_data/'+match_id + '_plays.csv'
    file_drives = 'data/game_data/'+match_id + '_drives.csv'
    if not(os.path.isfile(file_plays)):
        print(match)
        filename = 'http://www.nfl.com/liveupdate/game-center/' + str(match) + '/' + str(match) + '_gtd.json'
        try:
            json_data = json.loads(requests.get(filename).text)
        except Exception:
            print("Exception occured, waiting")
            sleep(5)
            continue
        drives = list(json_data[match_id]['drives'].keys())
        with open(file_drives,'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=colnames_drives)
            writer.writeheader()
            for values in drives:
                if values == 'crntdrv':
                    continue
                fds = json_data[match_id]['drives'][values]['fds']
                result = json_data[match_id]['drives'][values]['result']
                penyds = json_data[match_id]['drives'][values]['penyds']
                ydsgained = json_data[match_id]['drives'][values]['ydsgained']
                numplays = json_data[match_id]['drives'][values]['numplays']
                postime = json_data[match_id]['drives'][values]['postime']
                writer.writerow({'drive': values, 'fds':fds, 'result':result, 'penyds':penyds, 'ydsgained':ydsgained,
                                 'numplays':numplays,'postime':postime})
            csvfile.close()
        with open(file_plays,'w')as csvfile:
            writer = csv.DictWriter(csvfile,fieldnames=colnames_plays)
            writer.writeheader()
            for values in drives:
                if values == 'crntdrv':
                    continue
                plays = list(json_data[match_id]['drives'][values]['plays'].keys())
                for play in plays:
                    down = json_data[match_id]['drives'][values]['plays'][play]['down']
                    time = json_data[match_id]['drives'][values]['plays'][play]['time']
                    desc = json_data[match_id]['drives'][values]['plays'][play]['desc']
                    ydstogo = json_data[match_id]['drives'][values]['plays'][play]['ydstogo']
                    qtr = json_data[match_id]['drives'][values]['plays'][play]['qtr']
                    ydsnet = json_data[match_id]['drives'][values]['plays'][play]['ydsnet']
                    yrdln = json_data[match_id]['drives'][values]['plays'][play]['yrdln']
                    sp = json_data[match_id]['drives'][values]['plays'][play]['sp']
                    posteam = json_data[match_id]['drives'][values]['plays'][play]['posteam']
                    note = json_data[match_id]['drives'][values]['plays'][play]['note']
                    try:
                        writer.writerow({'drive':values, 'play': play, 'down':down, 'time':time,'desc': desc, 'ydstogo':ydstogo,
                                         'qtr':qtr,'ydsnet':ydsnet,'yrdln':yrdln,'sp':sp,'posteam':posteam, 'note':note})
                    except UnicodeEncodeError:
                        print match_id
                        # print s, w
                        print 'UnicodeEncodeError'
                        print {'drive':values, 'play': play, 'down':down, 'time':time,'desc': desc.encode('utf-8'), 'ydstogo':ydstogo,
                                         'qtr':qtr,'ydsnet':ydsnet,'yrdln':yrdln,'sp':sp,'posteam':posteam, 'note':note}
            csvfile.close()


# # TODO: Detect the error, why 2015010300 no data:
# match_id = '2015010300'
# filename = 'http://www.nfl.com/liveupdate/game-center/2015010300/2015010300_gtd.json'
# json_data = json.loads(requests.get(filename).text)
# file_plays = 'data/game_data/'+ match_id + '_plays.csv'
# drives = list(json_data[match_id]['drives'].keys())
# with open(file_plays,'w')as csvfile:
#     writer = csv.DictWriter(csvfile,fieldnames=colnames_plays)
#     writer.writeheader()
#     for values in drives:
#         if values == 'crntdrv':
#             continue
#         plays = list(json_data[match_id]['drives'][values]['plays'].keys())
#         for play in plays:
#             down = json_data[match_id]['drives'][values]['plays'][play]['down']
#             time = json_data[match_id]['drives'][values]['plays'][play]['time']
#             desc = json_data[match_id]['drives'][values]['plays'][play]['desc']
#             ydstogo = json_data[match_id]['drives'][values]['plays'][play]['ydstogo']
#             qtr = json_data[match_id]['drives'][values]['plays'][play]['qtr']
#             ydsnet = json_data[match_id]['drives'][values]['plays'][play]['ydsnet']
#             yrdln = json_data[match_id]['drives'][values]['plays'][play]['yrdln']
#             sp = json_data[match_id]['drives'][values]['plays'][play]['sp']
#             posteam = json_data[match_id]['drives'][values]['plays'][play]['posteam']
#             note = json_data[match_id]['drives'][values]['plays'][play]['note']
#             writer.writerow({'drive':values, 'play': play, 'down':down, 'time':time,'desc': desc, 'ydstogo':ydstogo,
#                              'qtr':qtr,'ydsnet':ydsnet,'yrdln':yrdln,'sp':sp,'posteam':posteam, 'note':note})
#     csvfile.close()
#
# match_id = '2015010301'
# filename = 'http://www.nfl.com/liveupdate/game-center/' + match_id + '/' + match_id + '_gtd.json'
# json_data = json.loads(requests.get(filename).text)
# file_plays = 'data/game_data/'+ match_id + '_plays.csv'
# drives = list(json_data[match_id]['drives'].keys())
# with open(file_plays,'w')as csvfile:
#     writer = csv.DictWriter(csvfile,fieldnames=colnames_plays)
#     writer.writeheader()
#     for values in drives:
#         if values == 'crntdrv':
#             continue
#         plays = list(json_data[match_id]['drives'][values]['plays'].keys())
#         for play in plays:
#             down = json_data[match_id]['drives'][values]['plays'][play]['down']
#             time = json_data[match_id]['drives'][values]['plays'][play]['time']
#             desc = json_data[match_id]['drives'][values]['plays'][play]['desc']
#             ydstogo = json_data[match_id]['drives'][values]['plays'][play]['ydstogo']
#             qtr = json_data[match_id]['drives'][values]['plays'][play]['qtr']
#             ydsnet = json_data[match_id]['drives'][values]['plays'][play]['ydsnet']
#             yrdln = json_data[match_id]['drives'][values]['plays'][play]['yrdln']
#             sp = json_data[match_id]['drives'][values]['plays'][play]['sp']
#             posteam = json_data[match_id]['drives'][values]['plays'][play]['posteam']
#             note = json_data[match_id]['drives'][values]['plays'][play]['note']
#             writer.writerow({'drive':values, 'play': play, 'down':down, 'time':time,'desc': desc, 'ydstogo':ydstogo,
#                              'qtr':qtr,'ydsnet':ydsnet,'yrdln':yrdln,'sp':sp,'posteam':posteam, 'note':note})
#     csvfile.close()
