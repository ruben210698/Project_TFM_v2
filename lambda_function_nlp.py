import os

from npl_analyzer_v2 import ejecutar_nlp_texto

LOCAL = eval(os.getenv('LOCAL', 'False'))
def lambda_handler(event, context):
    print(event)
    print(context)
    text = event['text']
    ejecutar_nlp_texto(text)

if LOCAL:
    texto = "Mi perro y mi gato juegan juntos en el parque con una pelota"
    ejecutar_nlp_texto(texto)





texto = "Mi perro y mi gato juegan juntos en el parque con una pelota"

#texto = "Mi perro, mi gato y mi loro juegan juntos en el parque con una pelota"


texto = "Mi perro es un golden retriever de tres años que adora jugar con su pelota en el parque y siempre me da la bienvenida moviendo la cola cuando llego a casa."
texto = "El sol brilla en el cielo azul los pájaros cantan en los árboles verdes el viento sopla suavemente a través de las hojas en el campo las vacas pastan tranquilamente en la ciudad la gente camina apresurada por las calles en el mar los barcos navegan en aguas cristalinas en todas partes la naturaleza sigue su curso y el mundo sigue girando."
texto = "La vida es como un viaje en el que cada uno elige su propio camino a veces es fácil otras veces es difícil hay momentos de alegría y momentos de tristeza pero sin importar qué tan difícil sea el camino siempre hay algo que aprender cada experiencia buena o mala nos ayuda a crecer y a ser más fuertes la naturaleza nos rodea y nos regala su belleza y su sabiduría hay que aprender a apreciarla y cuidarla al final del camino lo importante no es lo que hayamos acumulado sino las personas que hayamos tocado y las huellas que hayamos dejado en el mundo."
texto = "Mi novia tiene una toalla de hospital para su perro"


texto = "Isthar come paja en el pajar mientras Jasper le mira mientras Tina caza palomas para cenar"
#texto = "Mi perro y mi gato juegan juntos en el parque con una pelota"
#texto = "Me llamo Rubén y tengo 25 años. Vivo en Madrid y trabajo en una empresa de tecnología. Me gusta leer, viajar y pasar tiempo con mi familia y amigos."
#texto = "Los Austrias gobernaron España en el siglo XVI y XVII, responsables también de la Inquisición, expulsión de judíos. Su legado: arquitectura y arte en Madrid y Córdoba."
#texto = "Ruben cocina hamburguesas en la Freidora de aire"
#texto = "La naturaleza es impresionante en su variedad de paisajes, desde montañas majestuosas y extensas llanuras hasta océanos y ríos caudalosos."

###################################################################################################
##### TEST Flat
texto = "Felipe II fué rey de españa hace tiempo. Maria Antonieta era reina de Francia."
texto = "Mientras programo, un pajaro ha saltado por el balcón y se ha comido una golondrina"
# Para esta, idenfica mal el CD ya que pone a Golondrina como sujeto
# el SmallModel si calcula bien que es 'obj', es decir, CD.
#texto = "La naturaleza es impresionante en su variedad de paisajes"
###################################################################################################

#### TEST Root-VB a SUJ-VB
texto = "El perro de mi vecino se llama Toby y sale a jugar al parque todos los días"
texto = "Me llamo Ruben, estudio informatica y espero poder acabar el master algún día"
texto = "Me llamo Ruben, estudio informatica y soy de Madrid"


#### TEST Sujeto omitido
texto = "Me voy a jugar al futbol"
texto = "El otro día me llamaron de una empresa nueva"
texto = "Mi perro es un golden retriever de tres años que adora jugar con su pelota en el parque y siempre me da la bienvenida moviendo la cola cuando llego a casa."


# conflictivo con muchos sujetos omitidos, a ver cómo saco las relaciones de aqui.
texto = "Pedro se compró un coche nuevo la semana pasada porque el suyo, que tenía ya 10 años, se rompió"


########################################################################################################################
########################################################################################################################
########################################################################################################################
#texto = "Ruben cocina hamburguesas en la Freidora de aire ayer"


#texto = "Yo le añadí un poco de cilantro a la pasta para que supiera más rica. Tras esto, la quemé"
#texto = "Rubén le regaló juguetes a Okami por su cumpleaños. Pero ella los rompió en dos minutos."
# TODO que el DOS vaya dentro del rectangulo
#  Que el 'a Okami' lo pille como CI y no directo
