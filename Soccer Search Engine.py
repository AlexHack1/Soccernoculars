#pip install requests
#pip install beautifulsoup4
#pip install pandas
#pip install numpy
#pip intall lmxl
#pip install html5lib

from bs4 import BeautifulSoup
from lxml import html
import requests
import pandas as pd
import time
import numpy as np
from datetime import datetime
import functools

def sleep():
    time.sleep(4)

def soup_it(url):
    sleep()
    html_text = requests.get(url).text
    return BeautifulSoup(html_text, 'lxml')

def pandas_it(url):
    sleep()
    return pd.read_html(url)

def get_link(table,k): # Given a tbody tagged table, this function scrapes a given row of the table for a link
    rows =  table.find_all('tr')
    myrow = rows[k]
    next = myrow.find('th')
    mylink = next.a['href']
    return mylink


def scrape_league(league,year): ### Given a league and a year, this function returns the fbref page for that instance

    season = '0'
    k = 0
    dfs = pd.read_html(league)
    df = dfs[0]['Season']
    while season[0:4] != year[0:4]:
        season = df[k]
        k += 1
    k = k -1

    soup = soup_it(league)
    mytable = soup.find('div', attrs = {'class':'table_wrapper','id':'all_seasons'})
    tbody = mytable.find('tbody') # get table in bs4
    
    my_link = 'https://fbref.com/' + get_link(tbody,k)
    print(f'link found: {my_link}')
    return my_link

def pos_finder(position,comp,mycode):

    FW = [3,9,10,15,19,24,37,40,42,56,57,58,60,83,85,86,102,117,123,127,128,131,132,139,141,142,143,164,166]
    MF = [9,10,15,19,37,40,42,46,50,56,57,58,60,83,85,86,102,108,109,117,123,127,128,131,132,139,141,142,143,164,166,167]
    FB = [9,10,15,19,37,40,42,50,56,57,58,60,83,85,86,102,108,109,117,123,127,128,131,139,141,142,143,164,166]
    CB = [9,10,19,37,40,42,46,50,56,57,58,60,83,102,108,109,117,123,127,131,139,141,142,164,166,167]
    print(mycode)
    if mycode == 1:
        MF[4:] = [x-1 for x in MF[4:]]
        FW[5:] = [x-1 for x in FW[5:]]
        FB[4:] = [x -1 for x in FB[4:]]
        CB[3:] = [x -1 for x in CB[3:]]
    elif mycode == 2:
        MF[19:] = [x-1 for x in MF[19:]]
        FW[17:] = [x-1 for x in FW[17:]]
        FB[19:] = [x-1 for x in FB[19:]]
        CB[17:] = [x-1 for x in CB[17:]]
    elif mycode == 3:
        MF[25:] = [x-1 for x in MF[25:]]
        FW[23:] = [x-1 for x in FW[23:]]
        FB[23:] = [x-1 for x in FB[23:]]
        CB[20:] = [x-1 for x in CB[20:]]

    if position == 'MF':
        return MF
    elif position == 'FW':
        return FW
    else:
        if 'Full' in comp:
            return FB
        else:
            return CB
    

def player_vector(url,position,comp):

    soup = soup_it('https://fbref.com/' + url)
    footer = soup.find('div',{'class':'footer no_hide_long'})
    minutes = footer.div.strong.text
    minutes = minutes.replace('minutes','').strip()

    df = pandas_it('https://fbref.com/' + url)
    t_index = 2*len(df)//3
    df2 = df[t_index]['Standard Stats'][['Per 90','Percentile']]
    length = len(df2)
    mycode = 0
    if length < 169:
        check1 = df[t_index]['Standard Stats']['Statistic'][23]
        check2 = df[t_index]['Standard Stats']['Statistic'][110]
        print(check2)
        if 'target' not in check1:
            mycode += 1
        elif '%' not in check2:
            mycode += 2
        else:
            mycode += 3

    print(length)
    stats = df2.iloc[pos_finder(position,comp,mycode),:]

    stats = pd.concat([pd.DataFrame([[minutes,0]],columns = stats.columns),stats], ignore_index=True)
    return stats


def mysum(a,b):
    return a+b

def do_dat_shit(vec_list):
    vecs = [vec.astype(np.float16) for vec in vec_list]
    vecs_un90 = []
    for vec in vecs:
        minutes = vec.iloc[0,0]
        vec[1:] = (minutes/90.0)*vec[1:]
        vecs_un90.append(vec)

    sum = functools.reduce(mysum,vecs_un90)
    total_minutes = sum.iloc[0,0]
    sum[1:] = sum[1:] / (total_minutes/90.0)
    sum = pd.melt(sum,value_vars = ['Per 90','Percentile'])

    return sum['value']

def prep_vec(ks,position,year,threesixfive):
    url = ks[0]
    url = 'https://fbref.com' + url
    soup = soup_it(url)

    info = soup.find('div',{'id':'info'})
    name = info.h1.text.replace('\n','')
    print(name)
    pees = info.find_all('p')

    foot = [p.text for p in pees if 'Footed' in p.text]
    foot = str(foot)[-7:-2].strip()

    bday = [p for p in pees if 'Born' in p.text]
    bday = bday[0]
    bday = bday.find('span').text.strip()
    print(bday)
    if threesixfive != 'y':
        age = int(year[0:4]) - int(bday[-4:])
    else:
        age = int(datetime.now().year) - int(bday[-4:])
    
    current = soup.find('div',{'class':'filter switcher'})
    comp = current.a.text[3:]

    play_vec_list = []
    for i in range(len(ks)):
        play_vec_list.append(player_vector(ks[i],position,comp))

        almost_done = do_dat_shit(play_vec_list)

    done = pd.concat([pd.DataFrame([[name],[age],[foot],[comp]]),almost_done], ignore_index=True)
    return done

def recursive_szn_find(seasons,k,year,ks):
    if k == len(seasons) or year[0:4] != seasons[k].text[0:4]:
        return ks
    else:
        ks.append(seasons[k]['href'])
        k += 1
        recursive_szn_find(seasons,k,year,ks)


def player_add(player_link,threesixfive,year,position,mega_list):

    soup = soup_it(player_link)
    bottom = soup.find('div',{'class':'section_content','id':'bottom_nav_container'})
    if bottom(lambda t: 'Scouting' in t.text):
        uls = bottom.find_all('ul')
        sc_rp = uls[-1]
        seasons = sc_rp.find_all('a')
        k = 1
        ks = []

        if threesixfive != 'y': 
            while True:
                if k != len(seasons):
                    if year[0:4] == seasons[k].text[0:4]:
                        recursive_szn_find(seasons,k,year,ks)

                        break       
                    else:
                        k+=1
                else:
                    break
        else:
            ks = [seasons[0]['href']]
        if ks != []:
            df = prep_vec(ks,position,year,threesixfive)
            mega_list.append(df)


def parse_team(team,position,threesixfive,year,mega_list):

    soup = soup_it(team)
    team_players = soup.find('table')
    table = team_players.tbody
    for tr in table.find_all('tr'):
        player_position = tr.find('td', {'class': 'center', 'data-stat': 'position'}).text
        if position in player_position:
            player_link = 'https://fbref.com' + tr.th.a['href']
            player_add(player_link,threesixfive,year,position,mega_list)
    

def extract_players(link, myposition,threesixfive,year):
        soup = soup_it(link)
        table = soup.find('table')
        table = table.tbody
        for tr in table.find_all('tr'):
            team = 'https://fbref.com' + tr.th.a['href']
            
            mega_list = []
            parse_team(team,myposition,threesixfive,year,mega_list)

            mega_frame = pd.DataFrame(index = range(len(mega_list[0])),columns=range(len(mega_list)))
            for i in range(len(mega_list)):
                mega_frame[i] = mega_list[i]
            mega_frame = mega_frame.T
            mega_frame.to_csv(r'C:\Users\Alexander Hack\Documents\Soccernoculars\It_worked4.csv',sep= '\t',header = False,index = False,index_label=False, mode='a',encoding='utf8')

def get_position():

    pos_list = ['GK','DF','MF','FW']
    position = input(f'Enter a position. Options are {pos_list}:  ')
    while position not in pos_list:
        position = input(f'Enter a position. Options are {pos_list}:  ')
    
    print('great choice!')
    return position


def get_players(lg_yr,threesixfive,year):

    soup = soup_it(lg_yr)
    Squad_n_player = soup.find('li', attrs = {'class':'full hasmore','data-fade-selector':'#inpage_nav'})
    standard_stats = Squad_n_player.find('ul')
    st_st_link = 'https://fbref.com' + standard_stats.li.a['href']

    extract_players(st_st_link, get_position(),threesixfive,year)

### MAIN
leagues_dict = {'premier league': 'https://fbref.com/en/comps/9/history/Premier-League-Seasons','la liga':'https://fbref.com/en/comps/12/history/La-Liga-Seasons','ligue 1': 'https://fbref.com/en/comps/13/history/Ligue-1-Seasons','bundesliga': 'https://fbref.com/en/comps/20/history/Bundesliga-Seasons',
'serie a': 'https://fbref.com/en/comps/11/history/Serie-A-Seasons','campeonato brasileiro': 'https://fbref.com/en/comps/24/history/Serie-A-Seasons', 'eredivisie': 'https://fbref.com/en/comps/23/history/Eredivisie-Seasons',
'primeira liga': 'https://fbref.com/en/comps/32/history/Primeira-Liga-Seasons', 'major league soccer': 'https://fbref.com/en/comps/22/history/Major-League-Soccer-Seasons','championship':'https://fbref.com/en/comps/10/history/Championship-Seasons'}


print('Looking for soccer data? \b')
pick_league = input(f'Enter the league that you would like to see data for. Options are: \n {list(leagues_dict.keys())} \n')

year = input('And which season would you like to look at? \n Input "2022-2023" or "2019-2020" \n 2017-2018 and onward only: ')

threesixfive = input('Type y to look at data from last 365 days:')

print('Fetching that info now...')

lg_yr = scrape_league(leagues_dict[pick_league],year)

get_players(lg_yr,threesixfive,year)

# transpose back to normalcy
pd.read_csv(r'C:\Users\Alexander Hack\Documents\Soccernoculars\It_worked4.csv',sep= '\t',header=None,engine='python').T.to_csv(r'C:\Users\Alexander Hack\Documents\Soccernoculars\It_worked4.csv', sep= '\t', header=False, index=False,engine='python')

# get_players('https://fbref.com/en/comps/10/2021-2022/2021-2022-Championship-Stats')
# extract_players('https://fbref.com/en/comps/9/2022-2023/stats/2022-2023-Premier-League-Stats','FW','n','2022-2023',mega_list)
# player_add('https://fbref.com/en/players/99127249/Antony','n','2022-2023','FW',mega_list)
# parse_team('https://fbref.com/en/squads/33c895d4/2022-2023/Southampton-Stats','FW','n','2022-2023',mega_list)

# mega_frame = pd.DataFrame(index = range(len(mega_list[0])),columns=range(len(mega_list)))
# for i in range(len(mega_list)):
#     mega_frame[i] = mega_list[i]

# mega_frame.to_csv(r'C:\Users\Alexander Hack\Documents\Soccernoculars\It_worked.csv',mode='a', sep= '\t',encoding='utf8')

# If want to stop writing and resume another time, read file, transpose, then append --> at end read transpose close