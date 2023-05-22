from npl_analyzer_v2 import ejecutar_nlp_texto
from flask import Flask, request, jsonify
import pickle


def ejecutar_ec2():
    texto = "Mi perro y mi gato juegan juntos en el parque con una pelota"
    datos_serializados = ejecutar_nlp_texto(texto)
    # Deserializar los datos
    lista_palabras, lista_relaciones = pickle.loads(datos_serializados)
    print(lista_palabras)
    print(lista_relaciones)
    return datos_serializados


ejecutar_ec2()