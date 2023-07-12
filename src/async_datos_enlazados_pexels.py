import asyncio
import aiohttp
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import requests


async def async_search(string):
    try:
        url = "https://api.pexels.com/v1/search"

        params = {
            "query": string,
            "per_page": 1
        }
        headers = {
            "Authorization": "I9gaupw1IS7PLBjVBJnqiiAqerCMfOLOArC0vwBJwtEsWxOZvuNP3HiD"
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        image_url = None

        # TODO que haga un iterador buscando next-page
        if "photos" in data and "src" in data["photos"][0]:
            search_results = data["photos"][0]["src"]
            image_url = search_results['medium']
            if image_url.__contains__('.jpeg'):
                return image_url

        return image_url
    except Exception as e:
        print(e)
        return None



async def async_get_entity_image_links(list_palabras):
    dict_response = {}

    async def process_pal(pal):
        lemma = pal.token_nlp.lema
        original_text = pal.token_nlp.text
        imagen = await async_search(original_text)
        print(imagen)
        dict_response.update({pal: imagen})
        if imagen and imagen.split(".")[-1] != 'svg':
            pal.url_image = imagen
            #TODO mejorar el cálculo de la dimension
            pal.dimension_x = 5
            pal.dimension_y = 5
            pal.tam_eje_x_figura = 5
            pal.tam_eje_y_figura = 5

    tasks = [process_pal(pal) for pal in list_palabras]
    await asyncio.gather(*tasks)

    return dict_response
