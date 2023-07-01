import asyncio
import aiohttp
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import requests


async def async_search_wikipedia(query):
    url = "https://es.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srprop": "titlesnippet",
        "srinfo": "suggestion",
        "sroffset": 0,
        "srlimit": 10
    }

    response = requests.get(url, params=params)
    data = response.json()
    image_url = None

    if "query" in data and "search" in data["query"]:
        search_results = data["query"]["search"]
        #result = search_results[0]
        for result in search_results:
            title = result["title"]
            url = f"https://es.wikipedia.org/wiki/{title.replace(' ', '_')}"
            pageid = result["pageid"]
            print("Title:", title)
            print("URL:", url)
            print("")
            image_url = await async_get_image_url(pageid)
            print(image_url)
            if image_url is not None and image_url.split(".")[-1] != 'svg':
                return image_url

    return image_url


async def async_get_image_url(pageid):
    url = "https://es.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "pageids": pageid,
        "piprop": "original",
        "pithumbsize": 200
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "query" in data and "pages" in data["query"]:
        page_info = data["query"]["pages"]
        if str(pageid) in page_info:
            page_data = page_info[str(pageid)]
            if "thumbnail" in page_data:
                image_url = page_data["thumbnail"]["original"]
                return image_url
            if "original" in page_data:
                image_url = page_data["original"]["source"]
                return image_url

    return None




async def async_get_entity_image_links(list_palabras):
    dict_response = {}

    async def process_pal(pal):
        lemma = pal.token_nlp.lema
        original_text = pal.token_nlp.text
        imagen = await async_search_wikipedia(lemma)
        print(imagen)
        dict_response.update({pal: imagen})
        if imagen.split(".")[-1] != 'svg':
            pal.url_image = imagen
            #TODO mejorar el cálculo de la dimension
            pal.dimension_x = 5
            pal.dimension_y = 5
            pal.tam_eje_x_figura = 5
            pal.tam_eje_y_figura = 5

    tasks = [process_pal(pal) for pal in list_palabras]
    await asyncio.gather(*tasks)

    return dict_response
