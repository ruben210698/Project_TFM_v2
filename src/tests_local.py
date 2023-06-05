from npl_analyzer_v2 import ejecutar_nlp_texto
from flask import Flask, request, jsonify
import pickle

from visualizacion.generator_graph import generate_graph


def ejecutar_ec2():
    #texto = "Mi perro y mi gato juegan juntos en el parque con una pelota"
    texto = "Mi perro es un Golden Retriever, tiene tres años y adora jugar con su pelota en el parque."
    #texto = "Yo fuí a la playa"
    # datos_serializados = ejecutar_nlp_texto(texto)
    # # Deserializar los datos
    # lista_palabras, lista_relaciones, Palabra, Relacion = pickle.loads(datos_serializados)
    lista_palabras, lista_relaciones, Palabra, Relacion = ejecutar_nlp_texto(texto, local=True)

    #####################################


    #return datos_serializados

def ejecutar_lambda_crear_grafico(texto, list_palabras, list_relaciones):
    generate_graph(texto, list_palabras, list_relaciones)


def ejecutar_lambda_dibujar_grafico():
    pass


ejecutar_ec2()
