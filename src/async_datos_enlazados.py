import asyncio
import aiohttp
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import requests




"""
- Tardaba muchisimo con dbpedia
- utilizaba wikipedia igualmente para obtener la traduccion
- Encontraba muy pocas imagenes, y solo en dbpedia en ingles, por eso utilizaba wikipedia para obttener la traduccion

"""





async def async_get_dbpedia_resource(lemma):
    try:
        sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
        sparql.setQuery("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?s WHERE {
                { 
                    SELECT ?s WHERE {
                        ?s rdfs:label ?label.
                        FILTER (lang(?label) = 'es' && LCASE(str(?label)) = \"""" + lemma + """\")
                    } LIMIT 1
                }
                UNION
                { 
                    SELECT ?s WHERE {
                        ?s rdfs:label ?label.
                        FILTER (lang(?label) = 'es' && STRSTARTS(LCASE(str(?label)), \"""" + lemma + """\"))
                    } LIMIT 10
                }
            }
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if results['results']['bindings']:
            resource_uri = results["results"]["bindings"][0]["s"]["value"]
        else:
            return None

        english_resource = None
        resource = resource_uri.replace('http://es.dbpedia.org/resource/', '')

        url = 'https://es.wikipedia.org/w/api.php'  # URL for the Spanish Wikipedia API

        params = {
            'action': 'query',
            'prop': 'langlinks',
            'format': 'json',
            'titles': resource,
            'lllimit': '500'  # Increase if necessary
        }

        response = await aiohttp.request('GET', url, params=params)
        data = await response.json()

        pages = data['query']['pages']
        for page in pages.values():
            if 'langlinks' in page:
                langlinks = page['langlinks']
                for langlink in langlinks:
                    if langlink['lang'] == 'en':
                        print(f"The English version of '{resource}' is '{langlink['*']}'.")
                        english_resource = langlink['*']
                        break

        if english_resource:
            resource_uri = 'http://dbpedia.org/resource/' + english_resource
            return resource_uri

        return None
    except:
        return None

async def async_get_image_from_dbpedia_english(resource_uri):
    try:
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")  # Access point in English
        sparql.setQuery("""
            SELECT ?image WHERE {
                <""" + resource_uri + """> dbo:thumbnail ?image.
            }
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if results["results"]["bindings"]:
            image_url = results["results"]["bindings"][0]['image']['value']
            return image_url
        else:
            return None
    except:
        return None

async def async_get_entity_image_links(list_palabras):
    dict_response = {}

    async def process_pal(pal):
        lemma = pal.token_nlp.lema
        original_text = pal.token_nlp.text
        imagen = await async_get_image_from_dbpedia_english(await async_get_dbpedia_resource(lemma))
        print(imagen)
        dict_response.update({pal: imagen})
        pal.url_image = imagen

    tasks = [process_pal(pal) for pal in list_palabras]
    await asyncio.gather(*tasks)

    return dict_response

