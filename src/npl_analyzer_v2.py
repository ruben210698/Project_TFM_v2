"""
Con spicy NPL quiero pasarle una frase y que me saque las caracteristicas morg¡fologicas y sintacticas de cada palabra.
Tambien quiero que cree relaciones entre ellas.
"""
import os
import spacy
from unidecode import unidecode
from spacy.matcher import Matcher

from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.Grafo import Grafo
from utils.Palabra import Palabra
from utils.Relacion import Relacion
from constants.type_morfologico import *
from constants.type_sintax import *
from utils.TokenNLP import TokenNLP, TYPE_RELACION, TYPE_PALABRA
from utils.utils_text import unir_palabras, mover_rel_a_pal_2
from visualizacion.generator_graph import  generate_graph

import sys
from io import StringIO

import asyncio

PICTOGRAM_ACTIVE = eval(os.getenv('PICTOGRAM_ACTIVE', 'True'))


def print_spacy_tree(doc):
    print()
    # Imprimir el árbol de dependencias sintácticas en formato de árbol
    for token in doc:
        print(token.text, token.dep_, token.head.text)

    def print_tree(token, level=0):
        print('\t' * level + f"{token.text} -- {token.dep_}")
        for child in token.children:
            print_tree(child, level + 1)

    root = [token for token in doc if token.head == token][0]
    print_tree(root)
    print()

def get_list_palabras_relaciones(texto):
    list_token_nlp_oraciones = preprocesing_oracion_nlp(texto)
    list_token_nlp_oraciones = preprocesing_detailed(list_token_nlp_oraciones)
    print("#### Tras preprocesamiento: ")
    imprimir_nuevos_tokens_nlp(list_token_nlp_oraciones)


    list_palabras = get_list_palabras(list_token_nlp_oraciones)
    list_relaciones = get_list_relaciones(list_palabras)
    list_relaciones, list_palabras = get_list_relaciones_detailed(list_relaciones, list_palabras)
    manejar_palabras_restantes(list_token_nlp_oraciones)
    list_relaciones, list_palabras = get_list_relaciones_detailed(list_relaciones, list_palabras)
    relaciones_root_vb_cambio_suj_vb(list_relaciones)

    return list_palabras, list_relaciones


def borrar_palabra_y_unir_relaciones(palabra_nlp, relacion_actual, list_relaciones, list_palabras):
    origen_nlp = relacion_actual.pal_origen.token_nlp
    destino_nlp = relacion_actual.pal_dest.token_nlp
    tokens_hijos = palabra_nlp.tokens_hijos.copy() + [palabra_nlp.token_nlp_padre]
    tokens_hijos = [hijo for hijo in tokens_hijos if hijo not in [origen_nlp, destino_nlp, None]]
    # TODO sacar la relacion que tiene con los hijos la palabra origen y ver qué hacer
    pal_padre = palabra_nlp.palabra_que_representa
    if isinstance(pal_padre, Relacion):
        return list_relaciones, list_palabras

    for token_hijo in tokens_hijos:
        pal_hijo = token_hijo.palabra_que_representa
    #Palabra.relaciones_dict_origen.get(relacion_palabra.palabra_que_representa, [])
    #Palabra.relaciones_dict_destino.get(relacion_palabra.palabra_que_representa, [])
        mover_rel_a_pal_2(pal_padre, pal_hijo)

    palabra_nlp.palabra_que_representa.delete_palabra()
    return list_relaciones, list_palabras

def get_list_relaciones_detailed(list_relaciones, list_palabras):
    lista_morf_admitida = ['AUX', 'VERB']
    list_relaciones_old = list_relaciones.copy()
    # TODO: no hacer con tokens hijos sino con palabras hijos. Es decir, en la primera vuelta, las palabras_hijo
    #  son tokens hijos, pero en la segunda, las palabras hijo son palabras completas "a la playa" y de esa forma
    #  si las detecta como 1 sola y no como 3.

    for rel in list_relaciones_old:
        # TODO Si no existe algo, try-except.
        origen_nlp = rel.pal_origen.token_nlp
        destino_nlp = rel.pal_dest.token_nlp
        if origen_nlp is None or destino_nlp is None or isinstance(destino_nlp.palabra_que_representa, Relacion) \
                or isinstance(origen_nlp.palabra_que_representa, Relacion):
            continue

        relacion_palabra = None
        for hijo in origen_nlp.tokens_hijos:
            if hijo.tokens_hijos.__len__() == 1 and relacion_palabra is None \
                    and not isinstance(hijo.palabra_que_representa, Relacion):
                
                # ya que si es mayor seria relacion n-aria y sería un rombo
                hijo_hijo = hijo.tokens_hijos[0]
                #if hijo_hijo == destino_nlp and hijo.tipo_morfol in lista_morf_admitida:
                if hijo.tipo_morfol in lista_morf_admitida:
                    relacion_palabra = hijo
                    list_relaciones, list_palabras = \
                        borrar_palabra_y_unir_relaciones(hijo, rel, list_relaciones, list_palabras)


        if relacion_palabra is None:
            for hijo in destino_nlp.tokens_hijos:
                if hijo.tokens_hijos.__len__() == 1 and relacion_palabra is None \
                        and not isinstance(hijo.palabra_que_representa, Relacion):
                    # ya que si es mayor seria relacion n-aria y sería un rombo
                    hijo_hijo = hijo.tokens_hijos[0]
                    #if hijo_hijo == destino_nlp and hijo.tipo_morfol in lista_morf_admitida:
                    if hijo.tipo_morfol in lista_morf_admitida:
                        relacion_palabra = hijo

        if relacion_palabra is None:
            # En caso de que lo anterior no funcione, tal vez sea porque Pal1 <- VB -> Pal2
            # y Pal1 y Pal2 no tienen hijos, pero VB sí. En ese caso, se debe borrar VB y unir las relaciones
            # de Pal1 y Pal2
            destino_nlp_hijos = destino_nlp.tokens_hijos.copy()
            destino_nlp_hijos = [a for a in destino_nlp_hijos if a != origen_nlp]
            origen_nlp_hijos = origen_nlp.tokens_hijos.copy()
            origen_nlp_hijos = [a for a in origen_nlp_hijos if a != destino_nlp]

            if destino_nlp.tipo_morfol in lista_morf_admitida and destino_nlp_hijos.__len__() == 1:
                relacion_palabra = destino_nlp
                list_relaciones, list_palabras = \
                    borrar_palabra_y_unir_relaciones(destino_nlp, rel, list_relaciones, list_palabras)
            elif origen_nlp.tipo_morfol in lista_morf_admitida and origen_nlp_hijos.__len__() == 1:
                relacion_palabra = origen_nlp
                list_relaciones, list_palabras = \
                    borrar_palabra_y_unir_relaciones(origen_nlp, rel, list_relaciones, list_palabras)

        if relacion_palabra is not None:
            rel.texto = relacion_palabra.text
            relacion_palabra.representado = True
            relacion_palabra.palabra_que_representa = rel

    return list_relaciones, list_palabras


def preprocesing_detailed(list_token_nlp_oraciones):

    for oracion_nlp in list_token_nlp_oraciones:
        refresh_hijos_token_nlp(oracion_nlp)
        ################################################################
        # Cuando es in verbo pero no tiene hijos, se añade a la flecha
        # En este caso, ha habido un error y se ha colocado suelto cuando no se debe y debemos colocarlo
        # con la relación que le corresponde
        for token_nlp in oracion_nlp:
            if token_nlp.position_doc == 0:
                continue
            if token_nlp.tipo_morfol == 'AUX' and token_nlp.token_nlp_padre is not None \
                    and token_nlp.tokens_hijos == []:
                # Un verbo suelto. Se deben refrescar las relaciones para que sean correctas.
                old_token_padre = token_nlp.token_nlp_padre
                pos_doc_padre = token_nlp.token_nlp_padre.position_doc
                pos_doc_actual = token_nlp.position_doc
                if pos_doc_actual < pos_doc_padre and old_token_padre.token_nlp_padre is None:
                    new_token_hijo = old_token_padre
                    # aqui obtenemos una lista de elementos que están por delante de la posición actual
                    # y que son actuales hijos del actual padre. De esta forma buscaremos a la palabra enlazada.
                    list_posibles_padres = [token for token in token_nlp.token_nlp_padre.tokens_hijos if token.position_doc < pos_doc_actual]
                    # Se ordena por posicion y se el de mayor posicion
                    new_token_padre = sorted(list_posibles_padres, key=lambda x: x.position_doc, reverse=True)[0]
                    token_nlp.token_nlp_padre = new_token_padre
                    new_token_hijo.tokens_hijos.remove(token_nlp)
                    new_token_hijo.token_nlp_padre = token_nlp
                    new_token_padre.tokens_hijos.append(token_nlp)
                    token_nlp.tokens_hijos.append(new_token_hijo)
                else:
                    if pos_doc_actual < pos_doc_padre:
                        list_posibles_hijos = [token for token in token_nlp.token_nlp_padre.tokens_hijos if token.position_doc < pos_doc_actual]
                        list_posibles_hijos = sorted(list_posibles_hijos, key=lambda x: x.position_doc, reverse=True)
                    else:
                        list_posibles_hijos = [token for token in token_nlp.token_nlp_padre.tokens_hijos if token.position_doc > pos_doc_actual]
                        list_posibles_hijos = sorted(list_posibles_hijos, key=lambda x: x.position_doc, reverse=False)

                    for token_hijo in list_posibles_hijos:
                        if token_hijo.token_nlp_padre is None:
                            token_hijo.token_nlp_padre = token_nlp
                            token_nlp.tokens_hijos.append(token_hijo)
                            break
                    # Si no encuentra ninguno, se queda como está

        ################################################################

    return list_token_nlp_oraciones


def refresh_hijos_token_nlp(list_token_nlp_oracion):
    for token in list_token_nlp_oracion:
        if token.token_nlp_padre != None:
            token.token_nlp_padre.tokens_hijos.append(token)
            token.token_nlp_padre.tokens_hijos = list(set(token.token_nlp_padre.tokens_hijos))


def relaciones_root_vb_cambio_suj_vb(list_relaciones):
    # Modificar las relaciones para que, si ROOT es VB y la palDest es VERBO, se cambie la relación al Sujeto
    # Existe alguna relacion entre root y Sujeto
    sujeto = None
    for rel in list_relaciones:
        if rel.pal_dest.lugar_sintactico == TYPE_SINTAX_ROOT and rel.pal_origen.lugar_sintactico == TYPE_SINTAX_NSUBJ:
            sujeto = rel.pal_origen
            break
    if sujeto is not None:
        for rel in list_relaciones:
            if rel.pal_origen.lugar_sintactico == TYPE_SINTAX_ROOT and rel.pal_origen.tipo_morf == TYPE_MORF_VERB \
                    and rel.pal_dest.tipo_morf == TYPE_MORF_VERB and rel.pal_dest.lugar_sintactico not in LIST_SINTAX_TYPES_ROOT_VB_OK:
                rel.change_pal_origen(sujeto)


def manejar_palabras_restantes(list_token_nlp_oraciones):
    # Sacar las palabras que no se han sacado antes, omitiendo las Ys (que ya se verá como hacer enumeraciones después)
    # Y hay que comprobar que, si una palabra es igual a la que hay en la relación, no se ponga (en minusculas y sin acentos)
    for oracion in list_token_nlp_oraciones:
        for token in oracion:
            if token.representado or token.tipo_morfol == 'SPACE' or token.tipo_morfol == 'PUNCT':
                continue
            else:
                if token.tipo_morfol == TYPE_MORF_CCONJ:
                    continue
                if token.token_nlp_padre is not None:
                    pal_padre = token.token_nlp_padre.palabra_que_representa
                    if pal_padre is None:
                        pal_padre = token.palabra_padre_final
                    rel_dest_padre = Palabra.relaciones_dict_destino.get(pal_padre)
                    entontrada = False
                    if rel_dest_padre is not None and rel_dest_padre != []:
                        for rel in rel_dest_padre:
                            if rel.texto == token.text or rel.texto.__contains__(' ' + token.text + ' '):
                                entontrada = True
                                break
                    if entontrada:
                        continue
                    if pal_padre is not None and isinstance(pal_padre, Palabra):
                        # Si no esta en la relacion, se lo añado a la palabra, ya que no tiene relación hijo
                        pal_padre.add_aux_text(token.text, token.position_doc)

                print("hola")
                print(token)


def get_list_relaciones(list_palabras):
    list_relaciones = []
    for palabra in list_palabras:
        token_nlp = palabra.token_nlp
        if token_nlp.palabra_padre_final is None:
            continue

        list_rel_padre = token_nlp.tokens_relacion_padre_final

        if list_rel_padre != []:
            for token_rel in list_rel_padre:
                pal_origen = token_nlp.palabra_padre_final
                pal_dest = palabra
                if pal_dest.lugar_sintactico == TYPE_SINTAX_NSUBJ:
                    pal_origen = palabra
                    pal_dest = token_nlp.palabra_padre_final
                nueva_relacion = Relacion(
                    texto=token_rel.text,
                    pal_origen=pal_origen,
                    pal_dest=pal_dest,
                    position_doc=token_rel.position_doc,
                    lugar_sintactico=token_nlp.tipo_sintagma)
                list_relaciones.append(nueva_relacion)
                token_rel.representado = True
                token_rel.list_rel_que_representa.append(nueva_relacion)
            print(list_rel_padre)
        else:
            # Relación sin texto
            pal_origen = token_nlp.palabra_padre_final
            pal_dest = palabra
            if pal_dest.lugar_sintactico == TYPE_SINTAX_NSUBJ:
                pal_origen = palabra
                pal_dest = token_nlp.palabra_padre_final
            nueva_relacion = Relacion(
                texto='',
                pal_origen=pal_origen,
                pal_dest=pal_dest,
                position_doc=token_nlp.position_doc,
                lugar_sintactico=token_nlp.tipo_sintagma)
            list_relaciones.append(nueva_relacion)
    return list_relaciones


def get_list_palabras(list_token_nlp_oraciones):
    list_palabras = []
    for oracion_nlp in list_token_nlp_oraciones:
        for token_nlp in oracion_nlp:
            if token_nlp.tipo_morfol == 'SPACE' or token_nlp.tipo_morfol == 'PUNCT':
                continue
            if token_nlp.tipo_palabra is TYPE_PALABRA:
                if (token_nlp.tipo_morfol == 'AUX' and token_nlp.token_nlp_padre is not None and
                        token_nlp.token_nlp_padre.tipo_morfol == 'VERB'):
                    # Es el auxiliar de un verbo (ha saltado, se ha comido...)
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)
                elif token_nlp.tipo_morfol == 'VERB' and token_nlp.lugar_sintact_original in ('xcomp') and \
                        token_nlp.token_nlp_padre is not None and token_nlp.token_nlp_padre.tipo_morfol == 'VERB':
                    # Es el verbo que acompaña a otro verbo (adora jugar)
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)




                # Numeros
                elif token_nlp.tipo_morfol == 'NUM' and token_nlp.lugar_sintact_original in ('nummod') and \
                     token_nlp.token_nlp_padre is not None and token_nlp.token_nlp_padre.tipo_morfol == 'NOUN':
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)

                # preposision Que (a veces no lo identifica como preposicion)
                elif token_nlp.token_nlp_padre is not None and token_nlp.token_nlp_padre.tipo_morfol == 'VERB' and \
                        token_nlp.lema == 'que':
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)


                elif token_nlp.tipo_morfol == 'PRON' and token_nlp.lugar_sintact_original not in ('nsubj', 'obj') and \
                     token_nlp.token_nlp_padre is not None and token_nlp.token_nlp_padre.tipo_morfol == 'VERB':
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)
                # En caso de que efectivamente sean pronombres que acompañen al verbo
                elif token_nlp.tipo_morfol == 'PRON' and token_nlp.lugar_sintact_original not in ('nsubj') and \
                     token_nlp.token_nlp_padre is not None and token_nlp.token_nlp_padre.tipo_morfol == 'VERB' and \
                        token_nlp.lema in ("yo", "tú", "él", "ella", "usted", "nosotros", "nosotras", "vosotros",
                                           "vosotras", "ellos", "ellas", "ustedes"):
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)

                # Ahora el AUX que va con adjetivo, para "es impresionante"
                elif token_nlp.tipo_morfol == 'AUX' and token_nlp.lugar_sintact_original == 'cop' and \
                    token_nlp.token_nlp_padre is not None and token_nlp.token_nlp_padre.tipo_morfol in ('ADJ', 'NOUN'):
                    nueva_palabra = Palabra.constructor_alternativo(token_nlp=token_nlp)
                    list_palabras.append(nueva_palabra)
                    # Se crea la palabra para luego hacer bien las relaciones y luego ya se borrará
                    #nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    #if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                    #    nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)


                # más rico, que vaya junto
                elif token_nlp.tipo_morfol == 'ADV' and token_nlp.lugar_sintact_original == 'advmod' and \
                     token_nlp.token_nlp_padre is not None and token_nlp.token_nlp_padre.tipo_morfol in ('ADJ', 'VERB'):
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)
                #
                elif token_nlp.tipo_morfol == 'ADJ' and token_nlp.lugar_sintact_original == 'advmod' and \
                     token_nlp.token_nlp_padre is not None and token_nlp.token_nlp_padre.tipo_morfol in ('ADJ', 'NOUN'):
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)

                # estudio informatica:
                elif token_nlp.tipo_morfol == 'ADJ' and token_nlp.token_nlp_padre is not None and \
                    token_nlp.token_nlp_padre.lugar_sintact_original in ('appos'):
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)
                elif token_nlp.tipo_morfol == 'SCONJ' and token_nlp.token_nlp_padre is not None:
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)
                elif token_nlp.lugar_sintact_original == TYPE_SINTAX_FLAT and token_nlp.token_nlp_padre is not None:
                    # Es el auxiliar de una palabra (Felipe II...)
                    nueva_palabra = token_nlp.token_nlp_padre.palabra_que_representa
                    if nueva_palabra is not None and isinstance(nueva_palabra, Palabra):
                        nueva_palabra.add_aux_text(token_nlp.text, token_nlp.position_doc)
                elif token_nlp.tipo_morfol in ['AUX', 'VERB'] and token_nlp.tokens_hijos.__len__() == 1:
                    # Relaciones de 1 solo elemento.
                    # Se crea la palabra para luego hacer bien las relaciones y luego ya se borrará
                    nueva_palabra = Palabra.constructor_alternativo(token_nlp=token_nlp)
                    list_palabras.append(nueva_palabra)

                else:
                    nueva_palabra = Palabra.constructor_alternativo(token_nlp=token_nlp)
                    list_palabras.append(nueva_palabra)

                token_nlp.representado = True
                token_nlp.palabra_que_representa = nueva_palabra
                for child in token_nlp.list_children_nlp:
                    child.palabra_padre_final = nueva_palabra

            if token_nlp.tipo_palabra is TYPE_RELACION:
                # De momento no creo la relacion, solo guardo el token en tokens_relacion_padre_final
                for child in token_nlp.list_children_nlp:
                    child.palabra_padre_final = token_nlp.palabra_padre_final  # Si es relacion, hereda el padre del padre
                    child.tokens_relacion_padre_final.append(token_nlp)
        print(oracion_nlp)
    return list_palabras


def analyse_token_recursive(token_padre, token_actual, num_oracion):
    new_list_token_nlp = []
    if TokenNLP.nlp_token_dict.get(token_actual.idx, None) is not None or \
            (token_actual.pos_ == TYPE_MORF_PUNCT and token_actual.lemma_ == '.'):
        return []

    new_token_nlp = TokenNLP(token_actual, num_oracion, token_padre, token_actual.children)
    new_list_token_nlp.append(new_token_nlp)

    print(token_actual)
    for child in token_actual.children:
        new_list_token_nlp_2 = analyse_token_recursive(token_actual, child, num_oracion)
        new_list_token_nlp = new_list_token_nlp + new_list_token_nlp_2

    return new_list_token_nlp



def completar_sujeto_omitido(oraciones, nlp):
    list_oraciones = []
    for oracion in oraciones.split('.'):
        doc = nlp(oracion)
        sujeto_omitido = None

        hay_sujeto = False
        for token in doc:
            if token.dep_ == "nsubj":
                hay_sujeto = True
            if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                sujeto_omitido = token
                break

        if sujeto_omitido is None and not hay_sujeto:
            for token in doc:
                if token.tag_ == 'PRON' and token.head.pos_ == "VERB":
                    sujeto_omitido = token
                    break

        if sujeto_omitido is not None and not hay_sujeto and sujeto_omitido.text != sujeto_omitido.lemma_:
            sujeto_completo = sujeto_omitido.lemma_
            list_oraciones.append(oracion.replace(sujeto_omitido.text, sujeto_completo + " " + sujeto_omitido.text))
        else:
            list_oraciones.append(oracion)

    return '. '.join(list_oraciones)


def hay_sujeto(doc):
    for token in doc:
        if token.dep_ == "nsubj":
            return True
    return False


def cambiar_root_nombre_propio(doc):
    # Igual es porque el ROOT es el sujeto y no el verbo principal.
    # Ocurre con los nombres propios, si ent_type es persona, debo cambiarlo
    root = None
    encontrado = False
    for token in doc:
        if token.dep_ == "ROOT" and token.ent_type_ == 'PER':
            root = token
            break
    if root is None:
        return doc, False

    for chile_root in root.children:
        if chile_root.dep_ == "ROOT" and chile_root.ent_type_ == "PERSON":
            chile_root.dep_ = "nsubj"
            encontrado = False
            break
    return doc, encontrado



def preprocesing_oracion_nlp(texto):
    texto = texto.replace('\n', '. ').replace('\r', '. ').replace('\t', '. ').\
        replace("    ", " ").replace("   ", " ").replace("  ", " ")

    encontrado = False
    doc = None
    nlp = None
    list_spacy_loads = ['es_dep_news_trf', 'es_core_news_lg', 'es_core_news_md', 'es_core_news_sm', 'es_dep_news_trf']
    while not encontrado and list_spacy_loads != []:
        try:
            spacy_load = list_spacy_loads.pop(0)
            nlp = spacy.load(spacy_load)
            texto = completar_sujeto_omitido(texto, nlp)
            doc = nlp(texto)
            print("Spacy load: ", spacy_load)
            print("Resultado sin procesar: ")
            imprimir_doc(doc)
            #print_spacy_tree(doc)

            # Cambiar los ROOT personales por sujetos y los verbos principales por ROOT con sus relaciones.
            if not hay_sujeto(doc):
                doc, encontrado = cambiar_root_nombre_propio(doc)
            else:
                encontrado = True
        except Exception as e:
            print("Error con spacy load: ", e)
            continue

    print("#### Resultado añadiendo sujeto omitido: ")
    imprimir_doc(doc)

    spacy_patrones(doc, nlp)

    print("#### Resultado añadiendo patrones (CCL, CCT): ")
    imprimir_doc(doc)

    ## Primero lo divido en oraciones
    list_token_oraciones = []
    list_token_nlp_oraciones = []
    list_oracion_actual = []

    get_list_token_oraciones(doc, list_oracion_actual, list_token_oraciones)

    print("#### Obtenida nueva clase Token mia: ")
    imprimir_nuevos_tokens_nlp(list_token_oraciones)

    # Después, recorro la oración empezando por el Root
    num_oracion = -1
    for list_token_oracion in list_token_oraciones:
        num_oracion += 1
        list_token_nlp = []

        print("Oracion: ", num_oracion)
        # Ordenar la lista de tokens de la oracion por el número de children
        list_token_oracion.sort(key=lambda x: len(list(x.children)), reverse=True)
        list_token_oracion = [token for token in list_token_oracion if token.pos_ not in ('SPACE', 'PUNCT') ]

        # sacar de list_token_oracion el elemento cuyo token.dep_ == ROOT
        root = None
        for token in list_token_oracion:
            if token.dep_ == TYPE_SINTAX_ROOT:
                root = token
                break
        if root is not None:
            list_token_oracion.remove(root)
            list_token_oracion.insert(0, root)
        # Recorrer tokens y buscar palabras y relaciones
        for token in list_token_oracion:
            list_texts_ok = [token.text for token in list_token_nlp]
            if token.text not in list_texts_ok and not (token.pos_ == TYPE_MORF_PUNCT and token.lemma_ == '.')\
                    and not (token.pos_ == 'SPACE'):
                list_token_nlp_2 = analyse_token_recursive(None, token, num_oracion)
                list_token_nlp = list_token_nlp + list_token_nlp_2

        for token_nlp in list_token_nlp:
            token_nlp.refresh_parents_children()
        # quitar todos los tokens que sean de tipo puntuacion
        list_token_nlp = [token_nlp for token_nlp in list_token_nlp if token_nlp.tipo_morfol != TYPE_MORF_PUNCT]
        if list_token_nlp != []:
            list_token_nlp_oraciones.append(list_token_nlp)

    return list_token_nlp_oraciones



def spacy_patrones(doc, nlp):
    # Definir los patrones de coincidencia
    # Ref: https://www.ejemplos.co/ejemplos-de-adverbios-de-tiempo/
    adverbsCCT = [
        "actualmente", "enseguida", "normalmente", "ahora", "entretanto", "nunca", "anoche", "eternamente",
        "ocasionalmente", "anteriormente", "finalmente", "posteriormente", "antes", "frecuentemente", "primeramente",
        "antiguamente", "hoy", "pronto", "asiduamente", "inicialmente", "puntualmente", "aún", "inmediatamente",
        "recién", "ayer", "instantáneamente", "recientemente", "constantemente", "jamás", "siempre",
        "contemporáneamente", "luego", "simultáneamente", "cuando", "mañana", "tarde", "desde", "mientras",
        "temprano", "después", "momentáneamente", "ya", "día", "días", "dia", "dias", "semana", "semanas", "mes",
        "meses",
        "aun","recien", "instantaneamente", "contemporaneamente", "cuando", "despues", "momentaneamente"
    ]
    unicode_adverbsCCT = [unidecode(adverbCCT) for adverbCCT in adverbsCCT]

    patterns = [[{"LOWER": adverbCCT}] for adverbCCT in adverbsCCT+unicode_adverbsCCT]

    matcher = Matcher(nlp.vocab)
    matcher.add("Time_Patterns", patterns)

    matches = matcher(doc)

    for match_id, start, end in matches:
        matched_span = doc[start:end]
        print("CCT: ", matched_span.text)
        for token in matched_span:
            if token.dep_ in LIST_SINTAX_PATTERN_MODIFY:
                token.dep_ = TYPE_SINTAX_PATTERN_CCT

    ######################################################
    ######################################################
    # REF: https://www.ejemplos.co/25-ejemplos-de-adverbios-de-lugar/
    adverbsCCL = [
        "a través", "aquí", "donde", "abajo", "arriba", "en",
        "acá", "atrás", "encima", "afuera", "bajo", "enfrente",
        "ahí", "cerca", "entre", "al borde", "delante", "junto a",
        "allá", "dentro", "lejos de", "allí", "desde", "por debajo",
        "alrededor", "detrás", "sobre",
        "a traves", "aqui", "aca", "atras", "ahi", "alla", "alli", "detras"
    ]
    unicode_adverbsCCL = [unidecode(adverbCCL) for adverbCCL in adverbsCCL]
    patterns = [[{"LOWER": unidecode(adverbCCL)}] for adverbCCL in adverbsCCL + unicode_adverbsCCL]

    matcher = Matcher(nlp.vocab)
    matcher.add("Time_Patterns", patterns)

    matches = matcher(doc)

    for match_id, start, end in matches:
        matched_span = doc[start:end]
        print("CCL: ", matched_span.text)
        for token in matched_span:
            if token.dep_ in LIST_SINTAX_PATTERN_MODIFY:
                print("Old token:")
                print(token.text, ": ", token.idx, token.lemma_, "|| pos_:", token.pos_, "|| tag_:", token.tag_,
                      "|| dep_:", token.dep_, "|| ent_type_:", token.ent_type_, "|| ", token.shape_, token.is_alpha,
                      token.is_stop)
                token.dep_ = TYPE_SINTAX_PATTERN_CCL
                print("New token:")
                print(token.text, ": ", token.idx, token.lemma_, "|| pos_:", token.pos_, "|| tag_:", token.tag_,
                      "|| dep_:", token.dep_, "|| ent_type_:", token.ent_type_, "|| ", token.shape_, token.is_alpha,
                      token.is_stop)


def imprimir_doc(doc):
    for token in doc:
        ########################################
        print(token.text, ": ", token.idx, token.lemma_, "|| pos_:", token.pos_, "|| tag_:", token.tag_,
              "|| dep_:", token.dep_, "|| ent_type_:", token.ent_type_, "|| ", token.shape_, token.is_alpha, token.is_stop)
        for child in token.children:
            print("-->child:", child)
    print()
    print()
def imprimir_nuevos_tokens_nlp(list_token_oraciones):
    for oracion in list_token_oraciones:
        for token in oracion:
            ########################################
            if isinstance(token, TokenNLP):
                print(token.text, ": ", token.position_doc, token.lema, "|| pos_:", token.tipo_morfol, "|| tag_:", token.token_tag,
                      "|| dep_:", token.lugar_sintact_original, "|| ent_type_:", token.ent_type)
                for child_nlp in token.list_children_nlp:
                    print("-->child:", child_nlp.text)
            else:
                print(token.text, ": ", token.idx, token.lemma_, "|| pos_:", token.pos_, "|| tag_:", token.tag_,
                      "|| dep_:", token.dep_, "|| ent_type_:", token.ent_type_, "|| ", token.shape_, token.is_alpha,
                      token.is_stop)
                for child in token.children:
                    print("-->child:", child)
    print()
    print()




def get_list_token_oraciones(doc, list_oracion_actual, list_token_oraciones):
    for token in doc:
        tipo_morfol = token.pos_

        if tipo_morfol == TYPE_MORF_PUNCT and token.lemma_ == ".":
            # TODO hacer y que solo lo haga con los puntos, no con las comas.
            list_token_oraciones.append(list_oracion_actual)
            list_oracion_actual = []
            continue
        else:
            list_oracion_actual.append(token)
    if list_oracion_actual not in list_token_oraciones:
        list_token_oraciones.append(list_oracion_actual)


def borrar_imagenes():
    pass


txt_prints = ""
async def ejecutar_nlp_texto(texto, local=False):
    import pickle
    # Crear un objeto StringIO para redirigir la salida
    string_io = StringIO()
    #sys.stdout = string_io
    global txt_prints

    list_palabras = []
    list_relaciones = []
    try:
        list_palabras, list_relaciones = get_list_palabras_relaciones(texto)
        if list_palabras is None or list_palabras == []:
            return "No se ha recibido texto"

        #print("Palabras: ", list_palabras)
        #print("Relaciones: ", list_relaciones)
        for pal in list_palabras:
            print(pal.to_create_Palabra_str())

        # TODO new

        if PICTOGRAM_ACTIVE:
            from async_datos_enlazados_pexels import async_get_entity_image_links
            #from async_datos_enlazados import get_image_from_dbpedia_english, get_dbpedia_resource, get_entity_image_links
            #import aiohttp, asyncio
            # entity_image_links = {entity: get_image_from_dbpedia(get_dbpedia_resource(entity.token_nlp)) for entity in list_palabras}
            import tracemalloc
            tracemalloc.start()
            result = await async_get_entity_image_links(list_palabras)

            # asegúrate de que 'entities' es una lista de entidades
            #TODO
            ####################entity_image_links = get_entity_image_links(list_palabras)
            # for pal in list_palabras:
            #     if pal.texto == 'Los perros':
            #         pal.url_image = 'http://commons.wikimedia.org/wiki/Special:FilePath/Blue_merle_koolie_short_coat_heading_sheep.jpg?width=300'
            #     elif pal.texto == 'patos':
            #         pal.url_image = 'http://commons.wikimedia.org/wiki/Special:FilePath/Bucephala-albeola-010.jpg?width=300'

            ######################


        print()
        for rel in list_relaciones:
            print(rel.to_create_Relacion_str())

        Palabra.refresh_dict_palabras()

        # Obtener el contenido del string

        txt_prints = string_io.getvalue()
        print(txt_prints)
        # Restaurar la salida estándar
        sys.stdout = sys.__stdout__

        print(list_palabras)
        print(list_relaciones)

        fig = generate_graph(texto, list_palabras, list_relaciones)
        # TODO que aqui devuelva las listas serializadas para que luego el grafo lo genere bien
        # dependiendo de lo que le pida

    except Exception as e:
        print("Error: ", e)

    # Antes de serializar, hay que quitar los tokens de las palabras ya que no se pueden serializar
    for palabra in list_palabras:
        palabra.token = None
        palabra.token_nlp = None
    for relacion in list_relaciones:
        relacion.token = None
        relacion.token_nlp = None

    # Serializar las listas de objetos
    if not local:
        datos_serializados = pickle.dumps((list_palabras, list_relaciones, Palabra, Relacion))
        return datos_serializados

    else:
        return list_palabras, list_relaciones, Palabra, Relacion
