import asyncio
import aiohttp
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

def get_dbpedia_resource(lemma):
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

        # URL del API de Wikipedia en español
        url = 'https://es.wikipedia.org/w/api.php'

        params = {
            'action': 'query',
            'prop': 'langlinks',
            'format': 'json',
            'titles': resource,
            'lllimit': '500'  # Aumentar si es necesario
        }

        response = requests.get(url, params=params)
        data = response.json()

        pages = data['query']['pages']
        for page in pages.values():
            if 'langlinks' in page:
                langlinks = page['langlinks']
                for langlink in langlinks:
                    if langlink['lang'] == 'en':
                        print(f"La versión en inglés de '{resource}' es '{langlink['*']}'.")
                        english_resource = langlink['*']
                        break

        if english_resource:
            resource_uri = 'http://dbpedia.org/resource/' + english_resource
            return resource_uri

        return None
    except:
        return None

def get_image_from_dbpedia_english(resource_uri):
    try:
        # if resource_uri is None:
        #     return None
#
        # sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
        # sparql.setQuery("""
        #     PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        #     SELECT ?image WHERE {
        #         <""" + resource_uri + """> foaf:depiction ?image.
        #     }
        # """)
#
        # sparql.setReturnFormat(JSON)
        # results = sparql.query().convert()
#
        # if results["results"]["bindings"]:
        #     image_url = results["results"]["bindings"][0]['image']['value']
        #     print(image_url)
        #     return image_url
        # return None

        sparql = SPARQLWrapper("http://dbpedia.org/sparql")  # Punto de acceso en inglés
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

# Para crear y manejar las sesiones http de manera eficiente, es mejor crear una sola vez
# y usarla para todas las solicitudes. Aquí hay una función que hace eso:

import aiohttp, asyncio
def get_entity_image_links(list_palabras):
    #async with aiohttp.ClientSession() as session:
    tasks = []
    dict_response = {}
    for pal in list_palabras:
        lemma = pal.token_nlp.lema
        original_text = pal.token_nlp.text
        imagen = get_image_from_dbpedia_english(get_dbpedia_resource(lemma))
        print(imagen)
        dict_response.update({pal: imagen})
        pal.url_image = imagen

    return dict_response








# from SPARQLWrapper import SPARQLWrapper, JSON
#
# sparql = SPARQLWrapper("http://es.dbpedia.org/sparql")
# texto = "perro"
# sparql.setQuery("""
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#     SELECT ?s WHERE {
#         {
#             SELECT ?s WHERE {
#                 ?s rdfs:label ?label.
#                 FILTER (lang(?label) = 'es' && LCASE(str(?label)) = \"""" + texto + """\")
#             } LIMIT 1
#         }
#         UNION
#         {
#             SELECT ?s WHERE {
#                 ?s rdfs:label ?label.
#                 FILTER (lang(?label) = 'es' && STRSTARTS(LCASE(str(?label)), \"""" + texto + """\"))
#             } LIMIT 10
#         }
#     }
# """)
#
# sparql.setReturnFormat(JSON)
# results = sparql.query().convert()
#
# for result in results["results"]["bindings"]:
#     print(result["s"]["value"])
