import asyncio
import aiohttp
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import requests


from translate import Translator

def traducir_palabra(palabra, idioma_origen, idioma_destino):
    try:
        translator = Translator(from_lang=idioma_origen, to_lang=idioma_destino)
        traduccion = translator.translate(palabra)
        return traduccion
    except Exception as e:
        return palabra


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
        #lemma = pal.token_nlp.lema
        original_text = pal.token_nlp.text
        original_text = traducir_palabra(original_text, 'es', 'en')
        imagen = await async_search(original_text)
        print(imagen)
        dict_response.update({pal: imagen})
        if imagen and imagen.split(".")[-1] != 'svg' and pal.tipo_morf not in ('VERB', 'PRON'):
            pal.url_image = imagen
            #TODO mejorar el cálculo de la dimension
            import urllib
            from matplotlib.offsetbox import OffsetImage, AnnotationBbox
            from PIL import Image, ImageDraw, ImageFont
            import svglib
            from io import BytesIO
            import requests
            response = requests.get(pal.url_image)
            image_data = response.content
            image = Image.open(BytesIO(image_data))
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height
            if original_width < original_height:
                new_width = 8
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = 8
                new_width = int(new_height * aspect_ratio)

            #pal.dimension_x = new_width + 30
            #pal.dimension_y = new_height + 50

            pal.dimension_x = new_width
            pal.dimension_y = new_height
            #pal.tam_eje_x_figura = 8
            #pal.tam_eje_y_figura = 8
        else:
            pal.dimension_x += 2



    tasks = [process_pal(pal) for pal in list_palabras]
    await asyncio.gather(*tasks)

    return dict_response
