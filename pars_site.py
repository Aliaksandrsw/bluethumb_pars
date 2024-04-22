import time
from dataclasses import dataclass
import json
import aiohttp
import asyncio
import pyexcel as p


@dataclass
class Pic:
    id: int
    title: str
    url: str
    price: float

    def __post_init__(self):
        if self.price:
            self.price = self.price / 100


async def get_response(session, page: int):
    headers = {
        'accept': 'application/json',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://bluethumb.com.au/artworks?page=1',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    params = {
        'page': str(page),
        'per': '100',
        'category': 'All Art',
        'term': '',
        'sort': 'relevant',
        'ready_to_hang': 'all',
        'from_followeds': 'all',
        'availability': 'for_sale_web',
        'featured': 'false',
        'basePath': '/artworks',
    }
    async with session.get('https://bluethumb.com.au/api/listings', params=params, headers=headers) as response:
        return await response.json()


def get_json(g_json: json):
    content_in_page = []
    for art in g_json['listings']:
        content_in_page.append(Pic(
            id=art['id'],
            title=art['title'],
            url=art['url'],
            price=art['price']['cents'],
        ))
    return content_in_page


def save_exel(lst: list[Pic]):
    data = [['id', 'title', 'url', 'price']]
    for i in lst:
        data.append([i.id, i.title, i.url, i.price])
    excel_data = p.Book({'Art_data': data})
    excel_data.save_as("pic.xlsx")


async def main():
    async with aiohttp.ClientSession() as session:
        lst_art = []
        tasks = [get_response(session, page) for page in range(1, 101)]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            lst_art += get_json(response)
        save_exel(lst_art)


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
