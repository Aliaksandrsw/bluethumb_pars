import json
import random
import time

import aiohttp
import asyncio
from bs4 import BeautifulSoup

URL = 'https://www.bundestag.de/ajax/filterlist/en/members/863330-863330?limit=12&noFilterSet=true&offset='

user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
]


async def fetch_url(url):
    user_agent = random.choice(user_agent_list)
    referer = 'https://www.google.com/'
    accept_language = 'en-US,en;q=0.9'

    headers = {
        'User-Agent': user_agent,
        'Referer': referer,
        'Accept-Language': accept_language
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            return await response.text()


async def get_all_url(url):
    url_lst = []
    for i in range(0, 24, 12):
        page_url = f'{URL}{i}'
        html_text = await fetch_url(page_url)
        soup = BeautifulSoup(html_text, 'lxml')
        hr = soup.find_all(class_='bt-slide-content')
        url_lst.extend([h.find('a').get('href') for h in hr if h.find('a')])
    print(url_lst)
    return url_lst


async def get_content(lst: list):
    data_lst = []
    for url in lst:
        html_text = await fetch_url(url)
        soup = BeautifulSoup(html_text, 'lxml')
        pers = soup.find(class_='col-xs-8').find('h3').text.strip().split(',')
        soc_url = soup.find(class_='bt-linkliste').find_all('li')

        data = {
            'name': pers[0],
            'name_company': pers[1],
            'soc_url': [i.find('a').get('href') for i in soc_url]
        }
        data_lst.append(data)

    with open('../data.json', 'w', encoding='utf-8') as f:
        json.dump(data_lst, f, ensure_ascii=False, indent=4)


async def main():
    all_urls = await get_all_url(URL)
    await get_content(all_urls)


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
