import sqlite3
import requests
from bs4 import BeautifulSoup


# def parse_quote_names():
#     # Parsing basic data
#     url = 'https://www.finam.ru/quotes/stocks/'
#     headers = {
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#         'accept-encoding': 'gzip, deflate, br',
#         'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
#     }
#     pages_amount = 170
#     # Parsing quotes names
#     html = requests.get(url, headers=headers, params={})
#     if html.status_code == 200:
#         names = []
#         for page in range(pages_amount):
#             html = requests.get(url + '?pageNumber=' + str(page + 1), headers=headers, params={})
#             soup = BeautifulSoup(html.text, 'html.parser')
#             items = soup.find_all('tr', class_='QuoteTable__tableRow--1AA QuoteTable__withHover--1vT')
#             names.extend([item.find('a', class_='InstrumentLink__instrument--1PO').get_text() for item in items])
#     else:
#         print('Html parsing error')
#         return
#     # Creating quotes names database
#     with sqlite3.connect('names.sqlite3') as connection:
#         cursor = connection.cursor()
#         cursor.execute('''DROP TABLE IF EXISTS names''')
#         cursor.execute('''CREATE TABLE IF NOT EXISTS names (
#                 name VARCHAR(1024) NOT NULL UNIQUE PRIMARY KEY
#         )''')
#         for name in names:
#             try:
#                 cursor.execute(
#                     f'''INSERT INTO names VALUES ('{name.strip()}')'''
#                 )
#             except sqlite3.IntegrityError:
#                 print('Repeated name')
#                 continue
#             except sqlite3.OperationalError:
#                 print('Wrong name')
#                 continue
#         cursor.close()
from django.http import Http404


def parse_quote_names():
    # Parsing basic data
    url = 'https://finance.yahoo.com/screener/unsaved/3a284f4c-04b6-4f38-b7dc-9ca9dc10e1d6?count=100'

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    }
    pages_amount = 50
    # Parsing quotes names
    html = requests.get(url, headers=headers, params={})
    if html.status_code == 200:
        data = []
        for page in range(pages_amount):
            html = requests.get(url + '&offset=' + str(page * 100), headers=headers, params={})
            soup = BeautifulSoup(html.text, 'html.parser')
            items = soup.find_all('tr', class_='simpTblRow Bgc($hoverBgColor):h BdB Bdbc($seperatorColor) Bdbc($tableBorderBlue):h H(32px) Bgc($lv1BgColor)')
            data.extend([{
                'symbol': item.find('td', attrs={'aria-label': 'Symbol'}).get_text(),
                'name': item.find('td', attrs={'aria-label': 'Name'}).get_text(),
                'price': item.find('td', attrs={'aria-label': 'Price (Intraday)'}).get_text(),
                'change': item.find('td', attrs={'aria-label': 'Change'}).get_text(),
                'change_percent': item.find('td', attrs={'aria-label': '% Change'}).get_text(),
                'volume': item.find('td', attrs={'aria-label': 'Volume'}).get_text(),
            } for item in items])
    else:
        print('Html parsing error')
        return
    # Creating quotes names database
    with sqlite3.connect('names.sqlite3') as connection:
        cursor = connection.cursor()
        cursor.execute('''DROP TABLE IF EXISTS names''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS names (
                symbol VARCHAR(1024) NOT NULL UNIQUE PRIMARY KEY,
                name VARCHAR(1024) NOT NULL,
                price VARCHAR(1024) NOT NULL,
                change VARCHAR(1024) NOT NULL,
                change_percent VARCHAR(1024) NOT NULL,
                volume VARCHAR(1024) NOT NULL
        )''')
        for quote in data:
            try:
                cursor.execute(
                    f'''INSERT INTO names (symbol, name, price, change, change_percent, volume) VALUES (
                    '{quote['symbol']}', '{quote['name']}', '{quote['price']}',
                    '{quote['change']}', '{quote['change_percent']}', '{quote['volume']}'
                    )'''
                )
            except sqlite3.OperationalError:
                print('Wrong name format')
                continue
        cursor.close()


def quote_name_search(keyword):
    with sqlite3.connect('ui/business_logic/names.sqlite3') as connection:
        cursor = connection.cursor()
        cursor.execute(f'''
            SELECT * FROM names WHERE name LIKE "{keyword}%" OR symbol LIKE "{keyword}%"
        ''')
        result = cursor.fetchall()
        cursor.close()
        return result


def get_all_quotes(page:int, limit:int):
    with sqlite3.connect('ui/business_logic/names.sqlite3') as connection:
        cursor = connection.cursor()
        cursor.execute(
            f'''SELECT * FROM names LIMIT {limit} OFFSET {page * limit}'''
        )
        result = cursor.fetchall()
        cursor.close()
        return result


def paginate(current_page, limit):
    with sqlite3.connect('ui/business_logic/names.sqlite3') as connection:
        cursor = connection.cursor()
        cursor.execute(
            f'''SELECT * FROM names'''
        )
        total_amount = len(cursor.fetchall())
        cursor.close()
        pages_amount = (total_amount // limit) + (total_amount % limit)
        if pages_amount - current_page < 0:
            raise Http404
        else:
            return {'page_numbers': list(
                range(1, pages_amount + 1)
            )[(current_page - 5 if current_page - 5 >= 0 else 0):(current_page + 4)],
                    'no_further': pages_amount - current_page <= 4,
                    'no_back': current_page <= 4,
                    'current_page': current_page
                    }


# if __name__ == '__main__':
#     parse_quote_names()
