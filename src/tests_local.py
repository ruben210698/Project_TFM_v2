from npl_analyzer_v2 import ejecutar_nlp_texto
from flask import Flask, request, jsonify
import pickle
import asyncio

from visualizacion.generator_graph import generate_graph

# FIXME:
# Errores detectasdos:
# texto = "Mi hermana tiene un conejo llamado Floppy, tiene dos años y disfruta saltando en el jardín."
# texto = "Soy un apasionado de la música y toco la guitarra desde hace diez años, siempre encuentro consuelo y alegría en las melodías que creo."
# texto = "Soy un entusiasta de la cocina y disfruto experimentando con diferentes recetas y sabores. Nada me hace más feliz que ver a mis seres queridos disfrutar de mis platos."
# texto = "Me apasiona la fotografía y siempre estoy buscando la oportunidad perfecta para capturar momentos especiales y crear recuerdos duraderos."
# texto = "Me encanta el arte y la creatividad. Paso horas dibujando y pintando, dejando volar mi imaginación y expresando mis emociones a través de las obras que creo."
# texto = "Me apasiona la fotografía y siempre estoy buscando la oportunidad perfecta para capturar momentos especiales y crear recuerdos duraderos."




async def ejecutar_ec2():
    texto = "Mi perro y mi gato juegan juntos en el parque con una pelota"
    texto = "Mi perro es un Golden Retriever, tiene tres años y adora jugar con su pelota en el parque."
    #texto = "Yo fuí a la playa"
    #texto = "Los perros juegan en el retiro al atardecer"

    # TODO errores por relaciones 'junto a':
    #texto = "Los perros juegan en el retiro al atardecer junto a otros gatos y patos que nadan en el lago"
    #texto = "Mi gato es un Maine Coon, tiene cinco años y le encanta dormir en su rascador junto a la ventana."
    # TODO: tengo dudas con esta:
    #texto = "Soy un viajero empedernido y estoy constantemente planeando mi próxima aventura. Explorar diferentes culturas y lugares me enriquece como persona."

    texto = "Los perros juegan en el retiro al atardecer junto a otros gatos y patos que nadan en el lago"
    #texto = "Mi casa es una acogedora cabaña de madera, rodeada de hermosos árboles y con vistas al lago."
    #texto = "Los Austrias gobernaron España en el siglo XVI y XVII, responsables también de la Inquisición, expulsión de judíos. Su legado: arquitectura y arte en Madrid y Córdoba."

    texto = "El barco se hundió en la costa de Cuba cargado de oro."
    #texto = "El avión aterrizó en el aeropuerto de Madrid"

    # datos_serializados = ejecutar_nlp_texto(texto)
    # # Deserializar los datos
    # lista_palabras, lista_relaciones, Palabra, Relacion = pickle.loads(datos_serializados)
    lista_palabras, lista_relaciones, Palabra, Relacion = await ejecutar_nlp_texto(texto, local=True)

    #####################################


    #return datos_serializados






def ejecutar_lambda_crear_grafico(texto, list_palabras, list_relaciones):
    generate_graph(texto, list_palabras, list_relaciones)


def ejecutar_lambda_dibujar_grafico():
    pass


asyncio.run(ejecutar_ec2())
