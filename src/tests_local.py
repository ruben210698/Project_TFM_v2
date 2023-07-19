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
    texto = "El avión aterrizó en el aeropuerto de Madrid"
    texto = "El perro juega a la pelota en el parque"
    #texto = "Nosotros en Praga primero vamos a ver el castillo, después el Reloj del ayuntamiento y posteriormente el puente de Carlos."
    # Mala graciosa ++:
    texto = "Tú vas a ver en Praga el castillo y el Reloj astronómico."
    # Mala pero aceptable:
    texto = "Harry Potter es un mago que estudia en Hogwarts."
    # Mala graciosa ++:
    # texto = "Las elecciones de España son el 23 de julio"

    #### ++++++
    texto = "Para votar se debe introducir la papeleta en la urna y enseñar el DNI."

    texto = "La salida de emergencia está al lado de la puerta."

    # Graciosa+++
    texto = "El huevo debe cocinarse en la sartén a más de 100 grados"


    texto = "España empezó la guerra de la independencia en 1808 contra Francia."
    texto = "El papa coronó a Napoleón como emperador en 1804"

    # ++
    texto = "Napoleón conquistó Europa en 1804"

    # ++++++
    texto = "EEUU y Rusia se enfrentaron en la guerra fría"
    texto = "El coche eléctrico es menos contaminante que el de gasolina"


    #texto = "Durante la guerra se creó la constitución de Cádiz"

    #texto = "Enseñar identificación y meter papeleta postal en urna."
    # Solo que claro, para llegar a esto se ha tenido que probar urna, voto, DNI...
    texto = "Debes ir al colegio electoral más cercano y enseñar tu DNI para poder votar."


    texto = "Carlos I desembarcó en Tazones mientras le esperaban en Madrid para su coronación."
    texto = "El lunes voy a cocinar un pastel de chocolate, yo necesito huevos, harina, cacao, azúcar y mantequilla."

    texto = "Yo voy a la playa en verano y mi primo va a la montaña en invierno."
    texto = "Mi perro y mi gato juegan juntos en el parque con una pelota"

    texto = "El lunes voy a cocinar un pastel de chocolate, yo necesito huevos, harina, cacao, azúcar, miel, leche y mantequilla."

    texto = "Tú vas al supermercado a por huevos y leche"
    texto = "Yo voy a la playa en verano con un pico y una pala"
    texto = "Mi coche es rojo y se estropeó, así que mi hermana me ha dejado su moto azul que usa los fines de semana"
    texto = "El otro día vi a mi jefa en el parque mientras jugaba con su perro con una pelota amarilla"
    texto = "Mi perro corre en el parque y juega a la pelota mientras yo le miro"
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
