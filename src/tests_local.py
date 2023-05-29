from npl_analyzer_v2 import ejecutar_nlp_texto
from flask import Flask, request, jsonify
import pickle

from visualizacion.generator_graph import generate_graph


def ejecutar_ec2():
    #texto = "Mi perro y mi gato juegan juntos en el parque con una pelota"
    texto = "Mi perro es un Golden Retriever de tres años que adora jugar con su pelota en el parque."
    # datos_serializados = ejecutar_nlp_texto(texto)
    # # Deserializar los datos
    # lista_palabras, lista_relaciones, Palabra, Relacion = pickle.loads(datos_serializados)
    lista_palabras, lista_relaciones, Palabra, Relacion = ejecutar_nlp_texto(texto, local=True)
    print(lista_palabras)
    print(lista_relaciones)
    ejecutar_lambda_crear_grafico(texto, lista_palabras, lista_relaciones, Palabra, Relacion)

    #return datos_serializados

def ejecutar_lambda_crear_grafico(texto, list_palabras, list_relaciones, Palabra, Relacion):
    generate_graph(texto, list_palabras, list_relaciones, Palabra, Relacion)


def ejecutar_lambda_dibujar_grafico():
    pass


ejecutar_ec2()