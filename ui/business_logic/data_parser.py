import sqlite3
import requests
from bs4 import BeautifulSoup


def parse_quote_names():
    # Parsing basic data
    url = 'https://www.finam.ru/quotes/stocks/'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
    }
    pages_amount = 170
    # Parsing quotes names
    html = requests.get(url, headers=headers, params={})
    if html.status_code == 200:
        names = []
        for page in range(pages_amount):
            html = requests.get(url + '?pageNumber=' + str(page + 1), headers=headers, params={})
            soup = BeautifulSoup(html.text, 'html.parser')
            items = soup.find_all('tr', class_='QuoteTable__tableRow--1AA QuoteTable__withHover--1vT')
            names.extend([item.find('a', class_='InstrumentLink__instrument--1PO').get_text() for item in items])
    else:
        print('Html parsing error')
        return
    # Creating quotes names database
    with sqlite3.connect('names.sqlite3') as connection:
        cursor = connection.cursor()
        cursor.execute('''DROP TABLE IF EXISTS names''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS names (
                name VARCHAR(1024) NOT NULL UNIQUE PRIMARY KEY
        )''')
        for name in names:
            try:
                cursor.execute(
                    f'''INSERT INTO names VALUES ('{name.strip()}')'''
                )
            except sqlite3.IntegrityError:
                print('Repeated name')
                continue
            except sqlite3.OperationalError:
                print('Wrong name')
                continue
        cursor.close()


def quote_name_search(name):
    with sqlite3.connect('names.sqlite3') as connection:
        cursor = connection.cursor()
        cursor.execute(f'''SELECT name FROM names WHERE name LIKE "%{name}%"''')
        result = cursor.fetchall()
        cursor.close()
        return result

# if __name__ == '__main__':
#     parse_quote_names()