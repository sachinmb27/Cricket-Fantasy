import requests
from bs4 import BeautifulSoup
import json
import os
import pymongo

from methods.inningsOutBy import innOutBy
from methods.catches import catches
from methods.runouts import runouts
from methods.stumpings import stumpings
from methods.getBattingInfo import getBattingInfo
from methods.getBowlingInfo import getBowlingInfo
from methods.allPlayers import allPlayers
from methods.dataToBatsman import dataToBatsman
from methods.dataToBowlers import dataToBowlers
from methods.formDict import formDict

with open('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/matchURLs.txt') as f:
    URLs = []
    for line in f:
        URLs.append(line.strip())

matchCount = 0
matchName = {}

client = pymongo.MongoClient('mongodb+srv://sachin:helloworld@cluster0.khq4w.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
database = client['test2']
collection = database['seasonpoints']

for URL in URLs:
    scoreCard = requests.get(URL).text
    soup = BeautifulSoup(scoreCard, 'html.parser')

    playerTemplate = {
        "pid": "0",
        "name": "",
        "runsScored": "0",
        "ballsFaced": "0",
        "fours": "0",
        "sixes": "0",
        "strikeRate": "0",
        "out": False,
        "overs": "0",
        "maidens": "0",
        "runsGiven": "0",
        "wickets": "0",
        "noBalls": "0",
        "wides": "0",
        "economy": "0",
        "catches": 0,
        "runouts": 0,
        "stumpings": 0
    }

    firstInn = soup.find_all('div', id='innings_1')[0]
    firstInnBat = firstInn.find_all('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')[0]
    firstInnBat = firstInnBat.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
    firstInnBowl = firstInn.find_all('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')[1]
    firstInnBowl = firstInnBowl.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
    firstInnScore = firstInn.find('span', class_='pull-right').get_text().split(' ')[0]
    firstInnTeam = firstInn.find('span').get_text()
    firstInnTeam = firstInnTeam[:firstInnTeam.find(' Innings')]

    secondInn = soup.find_all('div', id='innings_2')[0]
    secondInnBat = secondInn.find_all('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')[0]
    secondInnBat = secondInnBat.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
    secondInnBowl = secondInn.find_all('div', class_='cb-col cb-col-100 cb-ltst-wgt-hdr')[1]
    secondInnBowl = secondInnBowl.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
    secondInnScore = secondInn.find('span', class_='pull-right').get_text().split(' ')[0]
    secondInnTeam = secondInn.find('span').get_text()
    secondInnTeam = secondInnTeam[:secondInnTeam.find(' Innings')]

    firstInnCatches = catches(innOutBy(firstInnBat))
    firstInnCatches = formDict(firstInnCatches)
    secondInnCatches = catches(innOutBy(secondInnBat))
    secondInnCatches = formDict(secondInnCatches)

    firstInnRunouts = runouts(innOutBy(firstInnBat))
    firstInnRunouts = formDict(firstInnRunouts)
    secondInnRunouts = runouts(innOutBy(secondInnBat))
    secondInnRunouts = formDict(secondInnRunouts)

    firstInnStumpings = stumpings(innOutBy(firstInnBat))
    firstInnStumpings = formDict(firstInnStumpings)
    secondInnStumpings = stumpings(innOutBy(secondInnBat))
    secondInnStumpings = formDict(secondInnStumpings)

    firstInnBatInfo = getBattingInfo(firstInnBat, firstInnCatches, firstInnRunouts, firstInnStumpings, secondInnCatches, secondInnRunouts, secondInnStumpings)
    secondInnBatInfo = getBattingInfo(secondInnBat, firstInnCatches, firstInnRunouts, firstInnStumpings, secondInnCatches, secondInnRunouts, secondInnStumpings)

    firstInnBowlInfo = getBowlingInfo(firstInnBowl, firstInnCatches, firstInnRunouts, secondInnCatches, secondInnRunouts)
    secondInnBowlInfo = getBowlingInfo(secondInnBowl, firstInnCatches, firstInnRunouts, secondInnCatches, secondInnRunouts)

    playingXI = soup.find_all('div', class_='cb-col cb-col-100 cb-minfo-tm-nm')
    team = playingXI[1].find_all('a') + playingXI[3].find_all('a')
    players = allPlayers(team, playerTemplate)

    players = dataToBatsman(firstInnBatInfo, players)
    players = dataToBatsman(secondInnBatInfo, players)
    players = dataToBowlers(firstInnBowlInfo, players)
    players = dataToBowlers(secondInnBowlInfo, players)

    if not os.path.isfile('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/points/seasonPoints.json'):
        dumpPlayers = {}
        for key in players:
            try:
                dumpPlayers[players[key]['pid']] = {'name': players[key]['name'], 'points': players[key]['points']}
            except KeyError:
                pass
        
        with open('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/points/seasonPoints.json', 'w') as f:  
            json.dump(dumpPlayers, f, indent=4)
            collection.insert_many([dumpPlayers])

    else:
        with open('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/points/seasonPoints.json', 'r') as f:
            existPlayers = json.load(f)

        for key in players:
            if key in existPlayers:
                try:
                    existPlayers[key]['points'] += players[key]['points']   
                except KeyError:
                    pass
            else:
                try:
                    existPlayers[players[key]['pid']] = {'name': players[key]['name'], 'points': players[key]['points']}
                except KeyError:
                    pass
        
        with open('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/points/seasonPoints.json', 'w') as f:
            json.dump(existPlayers, f, indent=4)
            collection.delete_many({})
            collection.insert_many([existPlayers])

    matchFileName = URL.split('/')[5]
    matchCount += 1

    with open('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/points/matchPoints/' + matchFileName + '.json', 'w') as f:
        json.dump(players, f, indent=4)
        print(matchFileName + ' is done!')
    
    if not os.path.isfile('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/matches.json'):
        matchName[matchCount] = matchFileName

        with open('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/matches.json', 'w') as f:
            json.dump(matchName, f, indent=4)
    
    else:
        with open('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/matches.json', 'r') as f:
            matches = json.load(f)
            matches[matchCount] = matchFileName
        
        with open('/Users/sachinmb/Documents/GitHub/Cricket-Fantasy/matches.json', 'w') as f:
            json.dump(matches, f, indent=4)
