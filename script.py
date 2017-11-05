import pandas as pd
import csv
import json
import requests
match_ids = pd.read_csv('data/game_data/pbp-2013_17.csv',usecols=['GameId'])
for match in list(match_ids['GameId']):
    print(match)
    filename = 'http://www.nfl.com/liveupdate/game-center/'+str(match)+'/'+str(match)+'_gtd.json'
    json_data = json.loads(requests.get(filename).text)
    match_id = list(json_data.keys())[0]
    try:
        drives = list(json_data[str(match_id)]['drives'].keys())
    except:
        print filename
        print match_id
        print json_data[str(match_id)].keys()

    colnames_plays = ['down','time','desc','ydstogo','qtr','ydsnet','yrdln','sp','posteam','note']
    colnames_drives = ['fds','result','penyds','ydsgained','numplays','postime']
    file_plays = match_id + '_plays.csv'
    file_drives = match_id + '_drives.csv'
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
            writer.writerow({'fds':fds, 'result':result, 'penyds':penyds, 'ydsgained':ydsgained,
                             'numplays':numplays,'postime':postime})
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
                writer.writerow({'down':down, 'time':time, 'desc':desc, 'ydstogo':ydstogo,
                                 'qtr':qtr,'ydsnet':ydsnet,'yrdln':yrdln,'sp':sp,'posteam':posteam})
