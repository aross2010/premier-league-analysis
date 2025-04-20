# gather data about each club stadium (name, city, capacity, yearOpened)
# send data to stidum.csv

import requests
from bs4 import BeautifulSoup
from write_csv import write_table_to_csv

BASE_URL = 'https://www.premierleague.com'

# contains all the clubs in the 23/24 season
league_table_url = 'https://www.premierleague.com/tables?co=1&se=578&ha=-1'

def get_stadium_links():
    club_links = []
    response = requests.get(league_table_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    league_table = soup.find('tbody', class_='league-table__tbody')
    # find all links that are children of td tags with class team and scope row
    clubs = league_table.find_all('td', class_='team', scope='row')
    # extract the href attribute from each link
    return [f'{BASE_URL}{team.find("a")["href"].replace("overview", "stadium")}' for team in clubs]

def extract_stadium_data(stadium_links):
    stadium_data = []
    for link in stadium_links:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        club_info = soup.find('span', class_='club-header__club-stadium')
        club_info_text = club_info.get_text(strip=True)
        name = club_info_text.split(',')[0].strip()
        city = club_info_text.split(',')[1].strip()
        # find based on data-ui-tab
        stadium_information = soup.find('article', attrs={'data-ui-tab': 'Stadium Information'})
        info_paragraphs = stadium_information.find_all('p')
        for p in info_paragraphs:
            strong = p.find('strong')
            if not strong: continue
            label = strong.get_text(strip=True)
            value = p.get_text(strip=True).replace(label, '').strip().replace('"', '').replace(',', '')
            print(label, value)
            if label == 'Capacity:':
                capacity = value
            elif label == 'Year Opened' or label == 'Built:':
                year_opened = value
        stadium_data.append({
            'name': name,
            'city': city,
            'capacity': capacity,
            'year_opened': year_opened
        })
    return stadium_data

def main():
    stadiums = get_stadium_links()
    stadium_data = extract_stadium_data(stadiums)
    write_table_to_csv(stadium_data, 'stadium.csv')
        

if __name__ == '__main__':
    main()



