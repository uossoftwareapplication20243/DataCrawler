import time

API_KEY = 'RGAPI-dd66c4f5-cd22-4ce5-a0c2-fd43ab3b3cb7'  # Riot API 키
import requests
import pandas as pd
import csv

REGION = 'kr'  # 한국 서버

# 아이템 정보 가져오기
def get_item_names():
    item_url = 'https://ddragon.leagueoflegends.com/cdn/14.18.1/data/ko_KR/item.json'  # 최신 버전의 아이템 데이터 URL
    response = requests.get(item_url)
    if response.status_code == 200:
        items_data = response.json()
        return  items_data
        #{item['id']: item['name'] for item in items_data['data'].values()}
    else:
        print("아이템 정보를 가져오는 데 실패했습니다.")
        return {}

# 아이템 이름 맵 가져오기
items_data = get_item_names()

# CSV 파일에서 Summoner ID 읽기
df = pd.read_csv('high_tier_user.csv')

# 결과를 저장할 리스트
results = []


file = open('matchv2.csv', mode='w', newline='', encoding='utf-8')
writer = csv.writer(file)
writer.writerow(['Win','NickName','Champion','item'])

Nullcheck =1
savedUUID = ''
for index, row in df.iterrows():
    SUMMONER_ID = row['Summoner ID']  # Summoner ID 가져오기

    # Summoner ID로 소환사 정보(PUUID) 가져오기
    summoner_url = f'https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/{SUMMONER_ID}'

    headers = {'X-Riot-Token': API_KEY}

    summoner_response = requests.get(summoner_url, headers=headers)

    if summoner_response.status_code == 200:
        summoner_data = summoner_response.json()
        PUUID = summoner_data['puuid']

        for idx in range(10):
            # 소환사 PUUID로 최근 게임 리스트 가져오기
            match_url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{PUUID}/ids?start='+str(idx*20)+'&count=20'

            match_response = requests.get(match_url, headers=headers)

            while(match_response.status_code != 200):
                print(match_response.status_code)
                time.sleep(60)
                match_response = requests.get(match_url, headers=headers)

            if match_response.status_code == 200:
                matches = match_response.json()

                # 각 게임의 템트리 정보 가져오기
                for match_id in matches:
                    time.sleep(0.1)
                    match_detail_url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}'
                    match_detail_response = requests.get(match_detail_url, headers=headers)

                    if match_detail_response.status_code == 200:
                        match_detail = match_detail_response.json()

                        # 소환사 정보 출력 (템트리와 게임 닉네임)
                        participants = match_detail['info']['participants']
                        for participant in participants:
                            if participant['puuid'] == PUUID:
                                item_names = [participant[f'item{i}'] for i in range(6)]
                                for idx, item_code in enumerate(item_names):
                                    try:
                                        item_names[idx] = items_data['data'][str(item_code)]['name']
                                    except:
                                        item_names[idx] = str(item_code)

                                if participant['summonerName'] == None:
                                    if (savedUUID != PUUID):
                                        savedUUID = PUUID
                                        Nullcheck+=1
                                    user_name = 'None'+str(Nullcheck)

                                else:
                                    user_name = participant['summonerName']
                                writer.writerow([
                                    participant['win'],
                                    user_name,
                                    participant['championName'],
                                    ' '.join(item_names),
                                ])

                                break
    else:
        print(f"Error fetching summoner data for {SUMMONER_ID}: {summoner_response.status_code}")

print("게임 아이템 및 캐릭터 정보가 game_item_tree.csv로 저장되었습니다.")
