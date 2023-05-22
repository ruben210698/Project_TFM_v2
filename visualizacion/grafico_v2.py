import math
import random
import shutil
import time
import os

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, RegularPolygon, Ellipse, Rectangle, Circle

from utils.Grafo import Grafo
from utils.Palabra import Palabra
from utils.Relacion import Relacion

from constants.figuras import *
from constants.type_morfologico import *
from constants.type_sintax import *
from constants import type_sintax
from constants import colores_figura, colores_figura_letra, colores
from constants.figuras import *
from constants import tam_figuras

from utils.utils_text import unir_list_all_relaciones, unir_siglos_annos_all_list, unir_conjuncion_y, \
    truncate_a_8_relaciones, unir_primera_palabra

from constants.direcciones_relaciones import DIR_DCHA, DIR_DCHA_ABAJO, DIR_DCHA_ARRIBA, DIR_ABAJO, DIR_ARRIBA, \
    DIR_IZQ, DIR_IZQ_ARRIBA, DIR_IZQ_ABAJO, FIND_DIR_CENTRO, FIND_DIR_DCHA, FIND_DIR_DCHA_ABAJO, FIND_DIR_DCHA_ARRIBA, \
    FIND_DIR_ABAJO, FIND_DIR_ARRIBA, FIND_DIR_IZQ, FIND_DIR_IZQ_ARRIBA, FIND_DIR_IZQ_ABAJO, DICT_DIR_BY_ORIGEN, CENTRO, \
    DICT_PROX_DIR, OPOSIT_DIR
from visualizacion.utils.direcciones import refresh_directions, get_rel_origen_and_dest_unidas
from visualizacion.utils.posicionesXY import get_next_location
from visualizacion.utils.matrix_functions import generate_matrix, get_pos_media_matrix, imprimir_matriz, \
    reducir_tam_matriz, ampliar_matriz, is_empty_relation_in_matrix

import logging
from utils.logger import FORMAT_1, create_logger

PAL_DEBUG = 'naturaleza'
PAL_DEBUG = os.getenv('PAL_DEBUG', '')
ZOOM_ACTIVE = eval(os.getenv('ZOOM_ACTIVE', 'True'))
create_logger()
CONTADOR_EVITAR_BUCLE_INFINITO = 0

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter(FORMAT_1)

# add formatter to ch
ch.setFormatter(formatter)
logger.addHandler(ch)
if (logger.hasHandlers()):
    logger.handlers.clear()






LINEAS_SEP_FILA = 5

PRINT_IMG = eval(os.getenv('PRINT_IMG', 'True'))
PRINT_GRAPH = eval(os.getenv('PRINT_GRAPH', 'True'))

MODE_DEBUG = "DEBUG"
MODE_NORMAL = "NORMAL"
EX_MODE = MODE_DEBUG

dict_color_figura = {
    getattr(type_sintax, nombre_variable): valor_variable
    for nombre_variable, valor_variable in vars(colores_figura).items()
    if nombre_variable.startswith("TYPE_SINTAX_")
}
dict_color_figura.update({None: colores.default, "": colores.default})

dict_color_figura_letra = {
    getattr(type_sintax, nombre_variable): valor_variable
    for nombre_variable, valor_variable in vars(colores_figura_letra).items()
    if nombre_variable.startswith("TYPE_SINTAX_")
}
dict_color_figura_letra.update({None: colores.default, "": colores.default})




"""
¿Qué necesito aqui?
Pues necesito que me saque las relaciones entre palabras. Es decir, la flecha, el verbo que necesitaré.
También tengo que saber qué tipo de palabra es.
Saber a qué hace referencia para poner bien el color.
Enlazar palabras con imágenes.

Gráficamente:
- Tengo que hacer que dinámicamente se vayan añadiendo palabras y que me las distribuya bien en el lienzo.


Web:
- Varios botones, o mejor uno de + y otro de - para ir agregando nivel de detalle en diferentes colores.
Esto simplemente lo que haría sería ir cambiando la imagen a una más compleja o menos (dejar precargada de antes
mientras ves la primera imagen).

Siguientes pasos Grafico:
ok- Que acepte relaciones a la izquierda (es decir, que la matriz empiece en la mitad y no en 0
- Que acepte más de 4 relaciones. Es decir, que para abajo me deje poner una de longitud 4 y otra en diagonal de lng 2 :) Y asi acepta 8.
- Que al buscar un hueco para poner la flecha busque que haya un hueco de 5 elementos a la dcha. Si no,
que suba otros 2. O que baje otros 2. O que vaya 5 más a la izq.

Futuro Avanzado:
- Una opcion que sea a modo arbol genealogico. Es decir, en vez de a la cha, que vaya hacia abajo
- Que cuando las relaciones sean 2, se queden bonitas con un angulo de 45º. Si son 3, con un angulo de 30º. Y no putos cuadrados.
"""


# TODO:
#  Que se añada el numero de relaciones de cada palabra y de esa forma se pueda calcular la importancia de cada palabra
#  y la posicion en la que colocarla y en la que colocar las demás.
#  - Añadir 1s cuando la relación vaya a pasar por ahi en la matriz.


def get_importance_dict(list_palabras):
    new_dict = {}
    for pal in list_palabras:
        new_dict[pal] = {"importancia": pal.importancia, "dimension": pal.dimension_x}
    # ordenar el diccionario por importancia
    new_dict = dict(sorted(new_dict.items(), key=lambda item: item[1]["importancia"]))

    return new_dict




def loop_reducir_posiciones_finales_eje_y(posiciones_finales, cambiado):
    ultima_y_leida = 0
    dim_y_reducir = 0
    i = -1
    posiciones_finales_loop = posiciones_finales.copy()
    cambiado = False
    for palabra, posicion in posiciones_finales_loop.items():
        i += 1
        pos_y_actual = posicion[1]
        if (pos_y_actual - ultima_y_leida) > 15: # asi, si hay diferencia de 15, se quita antes la de 15
            dim_y_reducir += (pos_y_actual - ultima_y_leida - 15)
        elif (pos_y_actual - ultima_y_leida) > 10:
            dim_y_reducir += (pos_y_actual - ultima_y_leida - 10)
        if dim_y_reducir > 0:
            nueva_pos_y = pos_y_actual - dim_y_reducir
            posiciones_finales.update({palabra: (posicion[0], nueva_pos_y)})
            cambiado = True
        ultima_y_leida = pos_y_actual
    return posiciones_finales, cambiado


def reducir_posiciones_finales_eje_y(posiciones_finales):
    posiciones_finales = posiciones_finales.copy()
    # Lo que hace esta funcion es
    # 1. ordena de menor a mayor todos los elementos y
    # 2. mira si entre 1 y otro de alguno hay más de 10 elementos (recurda que están ordenados de menor a mayor)
    # 3. si existe, cojo las posiciones finales iniciales y reduzco esa diferencia "excesiva" a todas las ys
    #  de todos los elementos que estén por encima de ese numero :)

    # tengo que crear un diccionario de {palabra: {pos_x: pos_y}}
    # y que ordene por pos_y en orden.

    posiciones_finales = dict(sorted(posiciones_finales.items(), key=lambda x: x[1][1]))

    cambiado = False
    posiciones_finales, cambiado = loop_reducir_posiciones_finales_eje_y(posiciones_finales, cambiado)

    while cambiado == True:
        posiciones_finales, cambiado = loop_reducir_posiciones_finales_eje_y(posiciones_finales, cambiado)

    return posiciones_finales



def loop_reducir_posiciones_finales_eje_x(posiciones_finales, cambiado):
    ultima_x_leida = 0
    dim_x_reducir = 0
    i = -1
    posiciones_finales_loop = posiciones_finales.copy()
    cambiado = False
    for palabra, posicion in posiciones_finales_loop.items():
        i += 1
        pos_x_actual = posicion[0]
        if (pos_x_actual - ultima_x_leida) > 25:
            dim_x_reducir += (pos_x_actual - ultima_x_leida - 25)
        if dim_x_reducir > 0:
            nueva_pos_x = pos_x_actual - dim_x_reducir
            posiciones_finales.update({palabra: (nueva_pos_x, posicion[1])})
            cambiado = True
        ultima_x_leida = pos_x_actual

    return posiciones_finales, cambiado


def reducir_posiciones_finales_eje_x(posiciones_finales):
    posiciones_finales = posiciones_finales.copy()
    # Lo que hace esta funcion es
    # 1. ordena de menor a mayor todos los elementos y
    # 2. mira si entre 1 y otro de alguno hay más de 10 elementos (recurda que están ordenados de menor a mayor)
    # 3. si existe, cojo las posiciones finales iniciales y reduzco esa diferencia "excesiva" a todas las ys
    #  de todos los elementos que estén por encima de ese numero :)

    # tengo que crear un diccionario de {palabra: {pos_x: pos_y}}
    # y que ordene por pos_y en orden.

    posiciones_finales = dict(sorted(posiciones_finales.items(), key=lambda x: x[1][0]))

    cambiado = False
    posiciones_finales, cambiado = loop_reducir_posiciones_finales_eje_x(posiciones_finales, cambiado)

    while cambiado == True:
        posiciones_finales, cambiado = loop_reducir_posiciones_finales_eje_x(posiciones_finales, cambiado)

    return posiciones_finales

def actualizar_posiciones_finales_palabras(posiciones_finales, list_palabras, matrix_dim):
    #pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    for pal in list_palabras:
        if posiciones_finales.get(pal, None) is None:
            continue
        else:
            pal.pos_x = posiciones_finales.get(pal)[0] #+ pos_x_media
            pal.pos_y = posiciones_finales.get(pal)[1] #+ pos_y_media



def update_relation_in_matrix(matrix_dim, relation):
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    id = relation.id
    imprimir_matriz(matrix_dim)
    if not relation.has_been_plotted:
        pal_origen = relation.pal_origen
        pal_dest = relation.pal_dest
        x_origen = pal_origen.pos_x
        x_dest = pal_dest.pos_x
        y_origen = pal_origen.pos_y
        y_dest = pal_dest.pos_y
        if x_origen is None or x_dest is None or y_origen is None or y_dest is None:
            return

        x_origen += pos_x_media
        x_dest += pos_x_media
        y_origen += pos_y_media
        y_dest += pos_y_media

        y = min(y_origen, y_dest)
        x = min(x_origen, x_dest)
        x_repres = x
        y_repres = y

        if (x_dest - x_origen) == 0:  # ARRIBA O ABAJO
            while y_repres < max(y_origen, y_dest):
                try:
                    if matrix_dim[y_repres][x_repres] == 0:
                        matrix_dim[y_repres][x_repres] = id
                    y_repres += 1
                except Exception as _:
                    matrix_dim = ampliar_matriz(matrix_dim)
                    pos_y_media_old, pos_x_media_old = pos_y_media, pos_x_media
                    y_origen_old, x_origen_old = y_origen, x_origen
                    y_dest_old, x_dest_old = y_dest, x_dest
                    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
                    y_repres = y_repres - pos_y_media_old + pos_y_media
                    x_repres = x_repres - pos_x_media_old + pos_x_media
                    y_origen = y_origen - pos_y_media_old + pos_y_media
                    y_dest = y_dest - pos_y_media_old + pos_y_media
                    x_origen = x_origen - pos_x_media_old + pos_x_media
                    x_dest = x_dest - pos_x_media_old + pos_x_media
            return

        if (y_dest - y_origen) == 0:  # DCHA O IZQ
            while x_repres < max(x_origen, x_dest):
                try:
                    if matrix_dim[y_repres][x_repres] == 0:
                        matrix_dim[y_repres][x_repres] = id
                    x_repres += 1
                except Exception as _:
                    matrix_dim = ampliar_matriz(matrix_dim)
                    pos_y_media_old, pos_x_media_old = pos_y_media, pos_x_media
                    y_origen_old, x_origen_old = y_origen, x_origen
                    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
                    y_repres = y_repres - pos_y_media_old + pos_y_media
                    x_repres = x_repres - pos_x_media_old + pos_x_media

                    y_origen = y_origen - y_origen_old + pos_y_media
                    y_dest = y_dest - pos_y_media_old + pos_y_media
                    x_origen = x_origen - pos_x_media_old + pos_x_media
                    x_dest = x_dest - pos_x_media_old + pos_x_media
            return

        m = (y_dest - y_origen) / (x_dest - x_origen)
        # if m > 0: # DCHA_ARRIBA o IZQ_ABAJO # DCHA_ABAJO o IZQ_ARRIBA
        i = 1
        while x_repres < max(x_origen, x_dest) and y_repres < max(y_origen, y_dest):
            try:
                x_repres = int(x + i)
                y_repres = int(y + i * m)
                if matrix_dim[y_repres][x_repres] == 0:
                    matrix_dim[y_repres][x_repres] = id
                i += 1
            except Exception as _:
                matrix_dim = ampliar_matriz(matrix_dim)
                pos_y_media_old, pos_x_media_old = pos_y_media, pos_x_media
                y_origen_old, x_origen_old = y_origen, x_origen
                y_dest_old, x_dest_old = y_dest, x_dest
                pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
                y_repres = y_repres - pos_y_media_old + pos_y_media
                x_repres = x_repres - pos_x_media_old + pos_x_media
                y_origen = y_origen - pos_y_media_old + pos_y_media
                y_dest = y_dest - pos_y_media_old + pos_y_media
                x_origen = x_origen - pos_x_media_old + pos_x_media
                x_dest = x_dest - pos_x_media_old + pos_x_media

        # if m < 0: # DCHA_ABAJO o IZQ_ARRIBA

        relation.has_been_plotted = True
        imprimir_matriz(matrix_dim)
    else:
        return

def update_relations_in_matrix_by_pal(matrix_dim, palabra):
    # Reactivada funcion pero en el dibujado del grafo, ya que en el calculo de posiciones estorbaba más que ayudaba

    # Esto se hizo en su dia para que no se pisasen palabras con relaciones, pero se ha visto que es mejor el método
    # de generar primero las relaciones entrelazadas, luego ponerlas en el gráfico y, en caso de que aun haya relaciones
    # que se pisen, que se haga una elipse y ya.
    #return matrix_dim

    list_rel = Palabra.relaciones_dict_origen.get(palabra) + Palabra.relaciones_dict_destino.get(palabra)
    for rel in list_rel:
        update_relation_in_matrix(matrix_dim, rel)


    return matrix_dim


def update_palabras_in_matrix(matrix_dim, palabra):
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    axis_y = palabra.pos_y + pos_y_media
    axis_x = palabra.pos_x + pos_x_media
    # bucle que recorre palabra.dimension_y desde -palabra.dimension_y//2 hasta palabra.dimension_y//2
    dim_x_total = palabra.dimension_x + palabra.cte_sum_x
    for y in range(palabra.dimension_y):
        axis_y_loop = axis_y + y - palabra.dimension_y // 2
        matrix_dim[axis_y_loop][axis_x - dim_x_total//2:axis_x + dim_x_total//2] = \
            [palabra.id for x in range(palabra.dimension_x + palabra.cte_sum_x)]

    # Esto fuera, no lo quiero hasta que llegue al calculo del grafo
    #matrix_dim = update_relations_in_matrix_by_pal(matrix_dim, palabra)
    return matrix_dim





def represent_list_relations(list_palabras_representadas, list_relaciones, matrix_dim, palabra, position_elems,
                             force_draw=False):
    global CONTADOR_EVITAR_BUCLE_INFINITO
    if palabra.texto == PAL_DEBUG:
        print("Hola")
    refresh_directions(palabra)
    palabra.refresh_subgrafo_completado()

    # TODOS los valores que no son null
    list_dir_to_check = [a for a in list(palabra.dict_posiciones.keys()) if palabra.dict_posiciones.get(a) is not None]

    if force_draw:
        list_dir_pending = [
            dir1 for dir1 in list_dir_to_check
            if (not palabra.dict_posiciones.get(dir1).subgrafo_completado or
               not palabra.dict_posiciones.get(dir1).has_been_plotted) and
               not palabra.dict_posiciones.get(dir1) == palabra.pal_raiz]
    else:
        # Solo las pendientes
        list_dir_pending = [dir1 for dir1 in list_dir_to_check if not palabra.dict_posiciones.get(dir1).has_been_plotted]

    ####################### Ordenar elementos para que haga primero los conflictivos
    # ahora saco los elementos que tienen relaciones entre si y los coloco los primeros.
    # es una lista de listas, unir todas ellas en una y quitar duplicados
    palabras_relaciones_proximas = list(set([a for b in palabra.palabras_relaciones_proximas.copy() for a in b]))

    for pal_prox in palabras_relaciones_proximas:
        if list_dir_pending != [] and pal_prox in list(palabra.dict_posiciones.values()):
            dir_tmp_prox = list(palabra.dict_posiciones.keys())[list(palabra.dict_posiciones.values()).index(pal_prox)]
            if dir_tmp_prox in list_dir_pending:
                list_dir_pending.remove(dir_tmp_prox)
                list_dir_pending.insert(0, dir_tmp_prox)
    # Y ponemos en primera posicion la palabra con menor importancia:
    pal_izq = palabra.dict_posiciones.get(DIR_IZQ)
    if pal_izq is not None and list_dir_pending != [] and DIR_IZQ in list_dir_pending:
        list_dir_pending.remove(DIR_IZQ)
        list_dir_pending.insert(0, DIR_IZQ)
    #######################

    list_rel_pending = []
    while list_dir_pending != []:
        CONTADOR_EVITAR_BUCLE_INFINITO += 1
        if CONTADOR_EVITAR_BUCLE_INFINITO > 500:
            print("Bucle infinito")
            break
        # Necesario para refrescar las palabras temporales
        list_relaciones_pal = get_rel_origen_and_dest_unidas(palabra).copy()
        dir_actual = list_dir_pending.pop(0)
        pal_to_draw = palabra.dict_posiciones.get(dir_actual)
        # buscar la relacion cuya palabta_tmp sea pal_to_draw
        relation = [elem for elem in list_relaciones_pal if elem.pal_tmp == pal_to_draw][0]


        if palabra.is_subgrafo_completado():
            continue

        # TODO
        force_draw = True

        if pal_to_draw.has_been_plotted:
            # al coger un numero random evitamos que se formen bucles infinitos
            relation = list_relaciones_pal[random.randint(0, len(list_relaciones_pal) - 1)]
            list_palabras_representadas_new, position_elems_2, matrix_dim_2 = \
                get_position_word_recursive(position_elems, matrix_dim, relation.pal_tmp, list_relaciones,
                                            relation=relation, force_draw=force_draw)
            logger.info(f"++++++++++++ Return")
            list_palabras_representadas += list_palabras_representadas_new
            if palabra.grafo.palabras_list_ordered_num_rel_pending == []:
                break
        else:
            relation.direccion_actual = dir_actual
            relation.pal_tmp.direccion_origen_tmp = dir_actual

            if palabra.texto == PAL_DEBUG:
                print("hola")
            ####################################################
            # 3a función (relations) - 2a entrada Word recursive
            logger.info(f"++++++++++++ PalTmp: {relation.pal_tmp.texto} - Rel: {relation.texto}")
            list_palabras_representadas_new, position_elems_2, matrix_dim_2 = \
                get_position_word_recursive(position_elems, matrix_dim, relation.pal_tmp, list_relaciones,
                                            relation=relation, force_draw=force_draw)
            logger.info(f"++++++++++++ Return")

        if list_palabras_representadas_new is None or position_elems is None or matrix_dim is None:
            logger.info("No se ha podido representar el grafo")
            list_direcciones_orden = palabra.deprec_lista_direcciones_orden
            list_palabras_representadas_new = []
            list_rel_pending.insert(0, relation)
        else:
            position_elems = position_elems_2
            matrix_dim = matrix_dim_2

        list_palabras_representadas += list_palabras_representadas_new
    # TODO: que todas las list_rel_pending se añadan pero sin criterio alguno con las felchas. con el max find_dir
    return list_palabras_representadas, matrix_dim, position_elems



def represent_word(matrix_dim, palabra, relation, position_elems):
    logger.info(f"################################ represent_word:::: {palabra.texto}")
    if palabra.texto == PAL_DEBUG:
        print("hola")
    axis_y, axis_x, matrix_dim = get_next_location(matrix_dim, palabra, relation)
    if axis_y is None or axis_x is None:
        logger.info(f"No se ha podido representar la palabra: {palabra.texto}")
        return matrix_dim, None, relation, position_elems
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    palabra.pos_y = axis_y - pos_y_media
    palabra.pos_x = axis_x - pos_x_media
    txt_palabra = palabra.texto
    pos_y = palabra.pos_y
    pos_x = palabra.pos_x
    position_elems.update({
        palabra: (
            palabra.pos_x,
            palabra.pos_y
        )})

    # reemplazar los 0s por IDs para range(value['dimension']+2)
    matrix_dim = update_palabras_in_matrix(matrix_dim, palabra)

    imprimir_matriz(matrix_dim)
    palabra.has_been_plotted = True
    palabra.refresh_subgrafo_completado()
    if relation is not None and palabra.direccion_origen_tmp is not CENTRO:
        # obtener de los valores de relation.pal_tmp_opuesta.dict_posiciones la key para el valor "palabra"
        dir_tmp_origen = list(relation.pal_tmp_opuesta.dict_posiciones.keys())[list(relation.pal_tmp_opuesta.dict_posiciones.values()).index(palabra)]
        palabra.direccion_origen_tmp = dir_tmp_origen
        dir_procedencia = OPOSIT_DIR.get(palabra.direccion_origen_tmp)
        palabra.dict_posiciones.update({dir_procedencia: relation.pal_tmp_opuesta})
        palabra.direccion_origen_final = dir_tmp_origen
        palabra.pal_raiz = relation.pal_tmp_opuesta


    return matrix_dim, palabra, relation, position_elems


def DEPREC_reordenar_relaciones_unir_graph_1er_grado(list_relaciones):
    # TODO sustituir por las listas de elementos contiguos que he creado para la palabra.
    # Busca las relaciones conflictivas de 2o grado y deja juntas las relaciones que pueden tener relaciones conflicitvas
    list_relaciones = list_relaciones.copy()
    dict_relaciones_2o_grado_conflictivas = {}
    list_pal_1er_grado = [a.pal_tmp for a in list_relaciones]
    for pal_2o_grado in list_pal_1er_grado:
        rel_orig_2o_grado = Palabra.relaciones_dict_origen.get(pal_2o_grado, [])
        re_dest_2o_grado = Palabra.relaciones_dict_destino.get(pal_2o_grado, [])
        rel_2o_grado = list(set(rel_orig_2o_grado + re_dest_2o_grado))
        for rel in rel_2o_grado:
            if rel in rel_orig_2o_grado and rel not in list_relaciones:
                rel.pal_tmp = rel.pal_dest
            elif rel in re_dest_2o_grado and rel not in list_relaciones:
                rel.pal_tmp = rel.pal_origen

            if rel.pal_tmp in list_pal_1er_grado and pal_2o_grado not in dict_relaciones_2o_grado_conflictivas.keys():
                dict_relaciones_2o_grado_conflictivas.update({pal_2o_grado: rel.pal_tmp})
    list_relaciones_copy = list_relaciones.copy()
    for pal1, pal2 in dict_relaciones_2o_grado_conflictivas.items():
        for rel in list_relaciones_copy:
            if rel.pal_tmp == pal1 or rel.pal_tmp == pal2:
                list_relaciones.remove(rel)
                list_relaciones.insert(0, rel)
    return list_relaciones


def get_position_word_recursive(position_elems, matrix_dim, palabra, list_relaciones, relation=None,
                                force_draw=False):
    list_palabras_representadas = []

    aaaaaaaaaaa = palabra.texto
    logger.info(f"get_position_word_recursive: {palabra.texto}")
    if palabra.texto == PAL_DEBUG:
        print("hola")

    draw_relations = not palabra.has_been_plotted_relations
    if not palabra.has_been_plotted and palabra.grafo.palabras_list_ordered_num_rel_pending != [] and \
        palabra.grafo.palabras_list_ordered_num_rel_pending[0] != palabra and draw_relations:
        draw_relations = False
    if not palabra.has_been_plotted and force_draw and palabra.grafo.palabras_list_ordered_num_rel_pending != [] and \
        palabra.grafo.palabras_list_ordered_num_rel_pending[0] == palabra:
        # En este caso, es esta palabra la que hay que dibujar con sus relaciones, asi que no hay que seguir forzando
        # el buscar la siguiente palabra
        draw_relations = True
        force_draw = False

    # time.sleep(10)
    ################################################################################################
    if not palabra.has_been_plotted:
        # 2a función - 1a entrada Word
        logger.info(f"++++++ {palabra.texto}")
        matrix_dim, palabra, relation, position_elems = \
            represent_word(matrix_dim, palabra, relation, position_elems)

        if palabra is None:
            return None, None, None
        list_print = [a for a in palabra.list_all_pal_subgrafo if a.has_been_plotted]
        print_graph(list_print, list_relaciones, position_elems, matrix_dim)
        logger.info(f"++++++ Return")

    ################################################################################################
    if force_draw or draw_relations:
        # 2a función - 2a entrada Relaciones
        logger.info(f"++++++ {palabra.texto}")
        list_palabras_representadas, matrix_dim, position_elems = \
            represent_list_relations(list_palabras_representadas, list_relaciones, matrix_dim, palabra, position_elems,
                                     force_draw)
        logger.info(f"++++++ Return")
    ################################################################################################
    if palabra not in list_palabras_representadas:
        list_palabras_representadas.append(palabra)

    # TODO peta cuando le quedan 2
    if palabra.grafo.palabras_list_ordered_num_rel_pending != [] and \
        palabra.grafo.palabras_list_ordered_num_rel_pending[0] == palabra:
        palabra.grafo.palabras_list_ordered_num_rel_pending.pop(0)
        palabra.grafo.palabras_drawn.append(palabra)

    if draw_relations:
        palabra.has_been_plotted_relations = True

    return list_palabras_representadas, position_elems, matrix_dim



def get_next_word_to_repres(palabra_old):
    palabra_old.grafo.reordenar_pal_pending()
    for pal_pending in palabra_old.grafo.palabras_list_ordered_num_rel_pending:
        list_relaciones_pal = get_rel_origen_and_dest_unidas(pal_pending)
        for rel in list_relaciones_pal:
            if rel.pal_origen in palabra_old.grafo.palabras_drawn or \
                    rel.pal_dest in palabra_old.grafo.palabras_drawn:
                return pal_pending
    return None

def get_position_dict(list_palabras, list_relaciones):
    global CONTADOR_EVITAR_BUCLE_INFINITO
    CONTADOR_EVITAR_BUCLE_INFINITO_NVL2 = 0
    importance_dict = get_importance_dict(list_palabras)
    matrix_dim, pos_y_media, pos_x_media = generate_matrix(list_palabras)

    position_elems = {}

    #list_palabras_ordenadas = list(importance_dict.keys())
    list_palabras_ordenadas = list_palabras.copy()
    list_palabras_ordenadas.sort(key=lambda x: x.numero_grafos, reverse=True)
    while len(list_palabras_ordenadas) != 0:
        CONTADOR_EVITAR_BUCLE_INFINITO = 0
        CONTADOR_EVITAR_BUCLE_INFINITO_NVL2 += 1
        if CONTADOR_EVITAR_BUCLE_INFINITO_NVL2 > 300:
            return None, None
        palabra = list_palabras_ordenadas.pop(0)

        # 1a función - 1a entrada
        logger.info(f"+ No Force Draw")
        logger.info(f"+ {palabra.texto}")
        list_palabras_representadas, position_elems, matrix_dim = \
            get_position_word_recursive(position_elems, matrix_dim, palabra, list_relaciones, force_draw = False)
        logger.info(f"+ Return")
        try:
            while palabra is not None and \
                    (not palabra.grafo.is_all_drawn() or palabra.grafo.palabras_list_ordered_num_rel_pending == []):
                # 1a función - 2a entrada
                logger.info(f"+ Si Force Draw")
                logger.info(f"+ {palabra.texto}")
                palabra.refresh_subgrafo_completado()
                list_palabras_representadas, position_elems, matrix_dim = \
                    get_position_word_recursive(position_elems, matrix_dim, palabra, list_relaciones, force_draw=True)
                logger.info(f"+ Return")
                list_palabras_ordenadas.sort(key=lambda x: x.numero_grafos, reverse=True)
                palabra = get_next_word_to_repres(palabra)

                # quitar de list_palabras_ordenadas las palabras que ya han sido representadas
                list_palabras_ordenadas = [pal for pal in list_palabras_ordenadas if pal not in list_palabras_representadas]
                list_palabras_ordenadas.sort(key=lambda x: x.numero_grafos, reverse=True)

        except Exception as _:
            logger.info("hola")

        if PRINT_GRAPH:
            print_graph(list_palabras_representadas, list_relaciones, position_elems, matrix_dim, final=True)

    position_elems = reducir_posiciones_finales_eje_y(position_elems)
    position_elems = reducir_posiciones_finales_eje_x(position_elems)
    actualizar_posiciones_finales_palabras(position_elems, list_palabras, matrix_dim)

    return position_elems, matrix_dim


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


def insertar_grafos_aproximados_palabras(list_palabras):
    for i in range(len(list_palabras) - 1, -1, -1):
        list_palabras[i].refresh_grafos_aproximados()


def remove_relations_without_words(list_relaciones, list_palabras):
    # Añadir nodos y aristas
    list_relaciones_to_remove = []
    for relation in list_relaciones:
        if relation.pal_origen is None or relation.pal_dest is None or \
                relation.pal_origen not in list_palabras or relation.pal_dest not in list_palabras:
            list_relaciones_to_remove.append(relation)

    for relation in list_relaciones_to_remove:
        list_relaciones.remove(relation)
        relation.delete_relation()
    return list_relaciones


def generate_graphs(list_palabras):
    list_palabras_copy = list_palabras.copy()
    while list_palabras_copy != []:
        palabra_origen = list_palabras_copy.pop(0)
        list_palabras_copy = generate_graphs_recursive(palabra_origen, list_palabras_copy)

def generate_graphs_recursive(palabra_origen, list_palabras_copy):
    list_rel_origen = Palabra.relaciones_dict_origen[palabra_origen]
    list_rel_dest = Palabra.relaciones_dict_destino[palabra_origen]
    list_pal_1er_grado_origen = [rel.pal_dest for rel in list_rel_origen]
    list_pal_1er_grado_dest = [rel.pal_origen for rel in list_rel_dest]
    list_pal_1er_grado = list(set(list_pal_1er_grado_origen + list_pal_1er_grado_dest))
    for pal_1er_grado in list_pal_1er_grado:
        if pal_1er_grado.grafo is not None:
            palabra_origen.grafo = pal_1er_grado.grafo
            palabra_origen.grafo.add_node(palabra_origen)
            break
    if palabra_origen.grafo is None:
        # No hay ningun grafo al que añadir la palabra
        grafo = Grafo(palabra_origen)
        palabra_origen.grafo = grafo

    for pal_1er_grado in list_pal_1er_grado:
        if not list_palabras_copy.count(pal_1er_grado) > 0:
            continue
        list_palabras_copy.remove(pal_1er_grado)
        list_palabras_copy = generate_graphs_recursive(pal_1er_grado, list_palabras_copy)

    return list_palabras_copy


def update_ctes_dim_relaciones_por_num_relaciones(list_palabras):
    for palabra in list_palabras:
        num_rel_1er_grado = len(palabra.relations_origen_and_dest)
        for relacion in palabra.relations_origen_and_dest:
            cte_sum_y = int((num_rel_1er_grado)*1)
            cte_sum_x = int((num_rel_1er_grado)*1)
            relacion.cte_sum_y = cte_sum_y if relacion.cte_sum_y < cte_sum_y else relacion.cte_sum_y
            relacion.cte_sum_x = cte_sum_x if relacion.cte_sum_x < cte_sum_x else relacion.cte_sum_x


def text_tranformations(list_palabras, list_relaciones):
    #list_palabras, list_relaciones = unir_primera_palabra(list_palabras, list_relaciones)
    #list_palabras, list_relaciones = unir_conjuncion_y(list_palabras, list_relaciones)
    #list_relaciones = unir_list_all_relaciones(list_relaciones)
    #list_palabras, list_relaciones = unir_siglos_annos_all_list(list_palabras, list_relaciones)
    #list_relaciones = unir_list_all_relaciones(list_relaciones)

    list_relaciones = remove_relations_without_words(list_relaciones, list_palabras)
    # al final:
    Palabra.refresh_relaciones_dict(list_relaciones)
    insertar_grafos_aproximados_palabras(list_palabras)
    truncate_a_8_relaciones(list_palabras)
    insertar_grafos_aproximados_palabras(list_palabras)
    generate_graphs(list_palabras)
    for palabra in list_palabras:
        palabra.refresh_pal_relations()
    for palabra in list_palabras:
        palabra.refresh_palabras_relacionadas_2o_grado()
    for palabra in list_palabras:
        palabra.refresh_relaciones_proximas_2o_grado()
    # el refresh grafo solo lo hace para el 1er grado, pero es suficiente de momento ya que no tenemos todavia la palabra raiz.
    for palabra in list_palabras:
        palabra.refresh_subgrafo_completado()
    update_ctes_dim_relaciones_por_num_relaciones(list_palabras)


    # TODO una funcion que a la primera palabra, las relaciones de esa palabra y las palabras de las relaciones las
    # ponga de color rojo, al siguiente nivel, azul, ect. Pero con el orden que da el grafo con relaciones de 1er grado
    #

    return list_palabras, list_relaciones


def generate_graph(texto, list_palabras, list_relaciones):
    print(f"Numero de palabras: {len(list_palabras)}")
    list_palabras, list_relaciones = text_tranformations(list_palabras, list_relaciones)

    # Crear un grafo dirigido
    G = nx.DiGraph()
    for relation in list_relaciones:
        G.add_edge(relation.pal_origen, relation.pal_dest)

    # Crear posiciones de nodos
    position_elems, matrix_dim = get_position_dict(list_palabras, list_relaciones)

    if position_elems is None:
        return None

    return print_graph(list_palabras, list_relaciones, position_elems, matrix_dim, final=True)

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


# Función para dibujar aristas con flechas
def draw_edge(ax, u, v, width=1.0, color='k', label='', label_offset=(0, 0), bold=False, curve = True,
              label_centered=True, pos_label_aprox = None):

    # En caso de que el parametro curve sea True, se dibujará la flecha pero con un poco de curvatura
    # es decir, que la felcha en vez de ir del punto A al B en linea recta, traza una pequeá parábola
    x_label = 0
    y_label = 0
    color = colores.black
    if curve:
        annotation = ax.annotate('', xy=u, xytext=v,
                    arrowprops=dict(facecolor=color, edgecolor=color, shrink=0.05, connectionstyle="arc3,rad=-0.4", zorder=-1),
                    xycoords='data', textcoords='data')

        if label:
            # El punto medio de la curva no se puede obtener directamente a partir de esta información. Sin embargo, puedes intentar calcular el punto medio de la línea recta que une los puntos u y v y luego ajustar la posición en función del valor de rad en connectionstyle






            # No se puede obtener el punto de pendiente mazima ya que no se tiene la ecuación de la curva
            # connectionstyle="arc3,rad=-0.4"
            # esto es
            # El valor "arc3" indica que se debe utilizar una conexión en forma de arco cúbico para conectar los puntos.
            # Un arco cúbico es un tipo de curva de Bézier cúbica

            # Entiendo. El parámetro rad en la función annotate controla la curvatura de la conexión entre los puntos de inicio y fin de la curva. Un valor negativo de rad producirá una curva cóncava, mientras que un valor positivo producirá una curva convexa.
            #
            # Dado que estás utilizando un valor de rad de -0.4, la curva que estás dibujando es cóncava. Para ajustar el punto medio de la línea para que se ajuste a esta curva cóncava, puedes intentar mover el punto medio hacia el interior de la curva. La cantidad exacta que debes mover el punto medio dependerá de la forma específica de la curva y del valor del parámetro rad que estés utilizando.
            #
            # Aquí tienes un ejemplo de cómo puedes ajustar el punto medio para que se ajuste a una curva cóncava en Python:

            # quiero sacar el punto de mayor pendiente de la curva annotation
            # bbox = annotation.get_window_extent().transformed(ax.transData.inverted())
            # import numpy as np
            # bbox = annotation.get_window_extent().transformed(ax.transData.inverted())
            # x = np.array([1, 2, 3])
            # y = np.array([1, 2, 3])
            # x_min = bbox.x0
            # y_min = bbox.y0
            # slopes = np.gradient(y)
            # max_slope_index = np.argmax(slopes)
#
            # max_slope_x = x[max_slope_index]
            # max_slope_y = y[max_slope_index]
#
            # # Esto lo hago sacando 10 puntos de la curva calculada anteriormente, cojo esos 10 vertives y cojo el punto medio
            # from shapely.geometry import LineString
            # patch = annotation.arrow_patch
            # vertices = patch.get_verts()
            # indices = [int(i) for i in range(0, len(vertices), len(vertices) // 10)]
            # points = vertices[indices]
            # line = LineString(vertices)
            # midpoint = line.interpolate(0.5, normalized=True)
            midpoint = ((u[0] + v[0]) / 2, (u[1] + v[1]) / 2)
            adjusted_midpoint = (midpoint[0], midpoint[1] - 0.1)
            x_label = adjusted_midpoint[0]
            y_label = adjusted_midpoint[1]
            #print(u, v, midpoint)
            #print("ok")

        # tengo la anotacion con esto: connectionstyle="arc3,rad=-0.4"
        # y con punto inicio y fin esto: xy=(2, 2), xytext=(1.5, 2.5)
        # quiero calcular el punto medio de la flecha curva para escribir encima el texto
        # para ello, calculo el punto medio de la recta que une los dos puntos
        # y luego le sumo un vector perpendicular a la recta
        



        ### import matplotlib.patches as patches
        ### arc = patches.Arc((0, 0), 10, 5, angle=0, theta1=0, theta2=90)
        ### ax.add_patch(arc)
        ### arrow = patches.FancyArrowPatch((0, 0), (5, 5), arrowstyle='->', mutation_scale=20)
        ### con = patches.ConnectionPatch(xyA=u, xyB=v, coordsA='data', coordsB='data', arrowstyle=arrow)
        ### ax.add_patch(con)
        ### # esta dando un error de que {TypeError}'FancyArrowPatch' object is not callable

    else:
        arrow = FancyArrowPatch(u, v, arrowstyle='->', mutation_scale=20, linewidth=width, color=color)
        ax.add_patch(arrow)

        if label and label_centered:
            x_label = (u[0] + v[0]) / 2 + label_offset[0]
            y_label = (u[1] + v[1]) / 2 + label_offset[1]
        elif label: # and not label_centered
            x_label = pos_label_aprox[0] + label_offset[0]
            y_label = pos_label_aprox[1] + label_offset[1]

    if label:
        if bold:
            ax.text(x_label, y_label, label, fontname='Times New Roman', fontsize=15, ha='center', va='center', zorder=3, weight='bold')
        else:
            ax.text(x_label, y_label, label, fontname='Times New Roman', fontsize=15, ha='center', va='center', zorder=3)

def print_graph(list_palabras, list_relaciones, position_elems, matrix_dim, final=False):
    try:
        if list_palabras == []:
            return None
        if PRINT_IMG or final:
            return _print_graph(list_palabras, list_relaciones, position_elems, matrix_dim)
    except Exception as e:
        print(e)
        return None


def get_relations_from_list_words(list_relaciones_all, list_palabras_custom):
    # Añadir nodos y aristas
    list_relaciones = list_relaciones_all.copy()
    list_relaciones_to_remove = []
    for relation in list_relaciones_all:
        if relation.pal_origen is None or relation.pal_dest is None or \
                relation.pal_origen not in list_palabras_custom or relation.pal_dest not in list_palabras_custom:
            list_relaciones_to_remove.append(relation)

    for relation in list_relaciones_to_remove:
        list_relaciones.remove(relation)

    return list_relaciones

def get_lists_zoom_palabras(list_palabras, list_relaciones, position_elems, matrix_dim):
    list_palabras = list_palabras.copy()
    list_relaciones_all = list_relaciones.copy()
    position_elems = position_elems.copy()
    matrix_dim = matrix_dim.copy()
    list_palabras_zoom = []
    list_relaciones_zoom = []

    # de todas las palabras que hay en list_palabras, cuantos grafos diferentes hay
    list_grafos = list(set([a.grafo for a in list_palabras]))
    list_grafos.sort(key=lambda x: x.id, reverse=False)

    # Primero se crean nuevas listas por grafo, y después, dentro del grafo, por importancia y por palabras proximas:

    list_pal_grafo_anterior = []
    for grafo in list_grafos:
        list_pal = grafo.palabras_list.copy()
        list_pal.sort(key=lambda x: x.importancia, reverse=False)
        limit_count_pal = [3, 7, 12, 20, 30, 40, 50, 999]
        new_list_pal = list_pal_grafo_anterior.copy()
        for limit in limit_count_pal:
            new_list_pal = list_pal_grafo_anterior.copy()
            count_pal = 0
            for pal in list_pal:
                # continuo en linea recta con un minimo de 3 palabras hasta que encuentre la siguiente palabra de mayor importancia fuera de la linea recta
                if count_pal < limit:
                    new_list_pal.append(pal)
                else:
                    # Si la siguiente palabra con mayor importancia esta a izq o dcha
                    if pal.dict_posiciones[DIR_IZQ] == pal or pal.dict_posiciones[DIR_DCHA] == pal:
                        new_list_pal.append(pal)
                    else:
                        break
                count_pal += 1
            list_palabras_zoom.append(new_list_pal)
            if len(new_list_pal) == len(list_pal) + len(list_pal_grafo_anterior):
                break
        list_pal_grafo_anterior = new_list_pal.copy()

    for list_palabras_custom in list_palabras_zoom:
        list_relaciones_new = get_relations_from_list_words(list_relaciones_all, list_palabras_custom)
        list_relaciones_zoom.append(list_relaciones_new)

    return list_palabras_zoom, list_relaciones_zoom

def _print_graph(list_palabras, list_relaciones, position_elems, matrix_dim):
    position_elems = position_elems.copy()

    imprimir_matriz(matrix_dim)
    matrix_dim_reduced = matrix_dim.copy()
    matrix_dim_reduced = reducir_tam_matriz(matrix_dim_reduced)

    max_axis_y = max([x[1] for x in position_elems.values()]) + 3
    min_axis_y = min([x[1] for x in position_elems.values()]) - 3

    # calculo preciso de la ultima palabra y su dimension
    max_axis_x = max([x[0] for x in position_elems.values()])
    list_max_x = list([x for x in position_elems.keys() if position_elems.get(x)[0] + x.dimension_x >= max_axis_x])
    list_max_x.sort(key=lambda x: position_elems.get(x)[0] + x.dimension_x, reverse=True)
    max_axis_x = list_max_x[0].dimension_x + list_max_x[0].pos_x

    min_axis_x = min([x[0] for x in position_elems.values()])
    list_min_x = list([x for x in position_elems.keys() if position_elems.get(x)[0] - x.dimension_x <= min_axis_x])
    list_min_x.sort(key=lambda x: position_elems.get(x)[0] - x.dimension_x, reverse=False)
    min_axis_x = list_min_x[0].pos_x - list_min_x[0].dimension_x


    dif_y = abs(max_axis_y - min_axis_y)//2 - abs(max_axis_y - min_axis_y)//5
    dif_x = abs(max_axis_x - min_axis_x)//2 - abs(max_axis_x - min_axis_x)//5

    if dif_y < 4:
        dif_y = 4
        max_axis_y = max_axis_y + 2
        min_axis_y = min_axis_y - 2

    #fig, ax = plt.subplots(figsize=(24, 16))
    #fig, ax = plt.subplots()
    if ZOOM_ACTIVE:
        list_palabras_zoom, list_relaciones_zoom = \
            get_lists_zoom_palabras(list_palabras, list_relaciones, position_elems, matrix_dim)
    else:
        list_palabras_zoom = [list_palabras]
        list_relaciones_zoom = [list_relaciones]

    fig = None
    # borrar la carpeta img_save/ y crearla de nuevo
    if os.path.exists("web_project/imagenes"):
        shutil.rmtree("web_project/imagenes")
    os.mkdir("web_project/imagenes")

    for i in range(len(list_palabras_zoom)):
        list_palabras = list_palabras_zoom[i]
        list_relaciones = list_relaciones_zoom[i]

        if dif_y < 5:
            fig, ax = plt.subplots(figsize=(dif_x, dif_y), subplot_kw=dict(aspect="equal"))
            ax.set_ylim(min_axis_y, max_axis_y)
        else:
            fig, ax = plt.subplots(figsize=(dif_x, dif_y))

        # Dibujar nodos
        draw_all_nodes(ax, position_elems, list_palabras)

        # Dibujar aristas
        draw_all_edges(ax, list_relaciones, position_elems, matrix_dim)

        # Configurar límites y aspecto del gráfico
        ax.set_ylim(min_axis_y, max_axis_y)
        ax.set_xlim(min_axis_x, max_axis_x)
        ax.set_aspect('equal')
        ax.axis('on')

        ax.plot()

        # Guardar figura en archivo
        plt.savefig(f"web_project/imagenes/imagen{i}")

        plt.show()

    return fig

def calcular_direccion_aprox(relation_draw, position_elems):
    logger.info(f"-- Calcular Dir Aprox: %s", relation_draw.texto)
    logger.info(f"Calcular Dir Aprox origen: %s", relation_draw.pal_origen)
    logger.info(f"Calcular Dir Aprox dest: %s", relation_draw.pal_dest)
    pal_origen = relation_draw.pal_origen
    pal_dest = relation_draw.pal_dest
    coord_pal_origen = position_elems[pal_origen]
    coord_pal_dest = position_elems[pal_dest]
    x_origen_draw = coord_pal_origen[0]
    x_dest_draw = coord_pal_dest[0]
    y_origen_draw = coord_pal_origen[1]
    y_dest_draw = coord_pal_dest[1]
    if x_origen_draw == x_dest_draw and y_origen_draw < y_dest_draw:
        return DIR_ARRIBA
    elif x_origen_draw == x_dest_draw and y_origen_draw > y_dest_draw:
        return DIR_ABAJO
    elif x_origen_draw < x_dest_draw and y_origen_draw == y_dest_draw:
        return DIR_DCHA
    elif x_origen_draw > x_dest_draw and y_origen_draw == y_dest_draw:
        return DIR_IZQ
    elif x_origen_draw < x_dest_draw and y_origen_draw < y_dest_draw:
        return DIR_DCHA_ARRIBA
    elif x_origen_draw < x_dest_draw and y_origen_draw > y_dest_draw:
        return DIR_DCHA_ABAJO
    elif x_origen_draw > x_dest_draw and y_origen_draw < y_dest_draw:
        return DIR_IZQ_ARRIBA
    elif x_origen_draw > x_dest_draw and y_origen_draw > y_dest_draw:
        return DIR_IZQ_ABAJO
    else:
        return None


def draw_all_edges(ax, list_relaciones, position_elems, matrix_dim):
    for relation_draw in list_relaciones:
        txt_rel = relation_draw.texto

        color = dict_color_figura.get(relation_draw.lugar_sintactico, dict_color_figura[None])
        x_origen_draw = 0
        x_dest_draw = 0
        if relation_draw.pal_origen.tam_eje_x_figura is None:
            relation_draw.pal_origen.tam_eje_x_figura = 0
        if relation_draw.pal_dest.tam_eje_x_figura is None:
            relation_draw.pal_dest.tam_eje_x_figura = 0

        try:
            pal_origen = relation_draw.pal_origen
            pal_dest = relation_draw.pal_dest
            coord_pal_origen = position_elems[pal_origen]
            coord_pal_dest = position_elems[pal_dest]

            x_origen_draw = coord_pal_origen[0]
            x_dest_draw = coord_pal_dest[0]
            y_origen_draw = coord_pal_origen[1]
            y_dest_draw = coord_pal_dest[1]

            relation_draw.direccion_actual = calcular_direccion_aprox(relation_draw, position_elems)

            # Control de que no se pisen relaciones de izquierda a dcha
            if relation_draw.direccion_actual == DIR_DCHA and pal_origen.dict_posiciones[DIR_DCHA] != pal_dest:
                continue
            elif relation_draw.direccion_actual == DIR_IZQ and pal_origen.dict_posiciones[DIR_IZQ] != pal_dest:
                continue

            if relation_draw.direccion_actual == DIR_DCHA:
                x_dest_draw = coord_pal_dest[0] - pal_dest.tam_eje_x_figura/2
                x_origen_draw = coord_pal_origen[0] + pal_origen.tam_eje_x_figura/2 - 0.5
            elif relation_draw.direccion_actual == DIR_IZQ:
                x_dest_draw = coord_pal_dest[0] + pal_dest.tam_eje_x_figura/2
                x_origen_draw = coord_pal_origen[0] - pal_origen.tam_eje_x_figura/2 + 0.5
            elif relation_draw.direccion_actual == DIR_ARRIBA:
                y_dest_draw = coord_pal_dest[1] - pal_dest.tam_eje_y_figura/2 - 0.4
                y_origen_draw = coord_pal_origen[1] + pal_origen.tam_eje_y_figura/2 - 0.5
            elif relation_draw.direccion_actual == DIR_ABAJO:
                y_dest_draw = coord_pal_dest[1] + pal_dest.tam_eje_y_figura/2 + 0.4
                y_origen_draw = coord_pal_origen[1] - pal_origen.tam_eje_y_figura/2 + 0.5

            elif relation_draw.direccion_actual == DIR_DCHA_ARRIBA:
                x_dest_draw = coord_pal_dest[0] - pal_dest.tam_eje_x_figura/2 + 0.2
                y_dest_draw = coord_pal_dest[1] - pal_dest.tam_eje_y_figura/2 - 0.4
                x_origen_draw = coord_pal_origen[0] + pal_origen.tam_eje_x_figura/2 - 1
                y_origen_draw = coord_pal_origen[1] + pal_origen.tam_eje_y_figura/2 - 0.5
                if x_dest_draw < x_origen_draw - 2:
                    x_dest_draw = coord_pal_dest[0]
                    x_origen_draw = coord_pal_origen[0] + 1
            elif relation_draw.direccion_actual == DIR_DCHA_ABAJO:
                x_dest_draw = coord_pal_dest[0] - pal_dest.tam_eje_x_figura/2 + 0.2
                y_dest_draw = coord_pal_dest[1] + pal_dest.tam_eje_y_figura/2 + 0.4
                x_origen_draw = coord_pal_origen[0] + pal_origen.tam_eje_x_figura/2 - 1
                y_origen_draw = coord_pal_origen[1] - pal_origen.tam_eje_y_figura/2 + 0.5
                if x_dest_draw < x_origen_draw - 2:
                    x_dest_draw = coord_pal_dest[0]
                    x_origen_draw = coord_pal_origen[0] + 1
            elif relation_draw.direccion_actual == DIR_IZQ_ARRIBA:
                x_dest_draw = coord_pal_dest[0] + pal_dest.tam_eje_x_figura/2 - 0.2
                y_dest_draw = coord_pal_dest[1] - pal_dest.tam_eje_y_figura/2 - 0.4
                x_origen_draw = coord_pal_origen[0] - pal_origen.tam_eje_x_figura/2 + 1
                y_origen_draw = coord_pal_origen[1] + pal_origen.tam_eje_y_figura/2 - 0.5
                if x_dest_draw > x_origen_draw - 2:
                    x_dest_draw = coord_pal_dest[0]
                    x_origen_draw = coord_pal_origen[0] - 1
            elif relation_draw.direccion_actual == DIR_IZQ_ABAJO:
                x_dest_draw = coord_pal_dest[0] + pal_dest.tam_eje_x_figura/2 - 0.2
                y_dest_draw = coord_pal_dest[1] + pal_dest.tam_eje_y_figura/2 + 0.4
                x_origen_draw = coord_pal_origen[0] - pal_origen.tam_eje_x_figura/2 + 1
                y_origen_draw = coord_pal_origen[1] - pal_origen.tam_eje_y_figura/2 + 0.5
                if x_dest_draw > x_origen_draw - 2:
                    x_dest_draw = coord_pal_dest[0]
                    x_origen_draw = coord_pal_origen[0] - 1
            else:
                # TODO: que si no tiene direccion_actual, la calcule :)
                logger.info("Error: dirección no contemplada", relation_draw.texto)
                logger.info("###########")

            relation_draw.x_origen_draw = x_origen_draw
            relation_draw.y_origen_draw = y_origen_draw
            relation_draw.x_dest_draw = x_dest_draw
            relation_draw.y_dest_draw = y_dest_draw

            curve = False
            conflicto_texto_relacion = False
            # TODO:
            #  1. OK -  En caso de coincidir el texto de la relacion con el texto de OTRA RELACION, se escribe el texto
            #  en uno de los extremos de la flecha (el que menos grafos tenga)
            #  2. En caso de que coincida pero con otra palabra, hace la curva y lo escribe en el extremo también.

            if txt_rel == "comprender":
                print("hola")

            conflicto_texto_relacion = False
            is_empty_position, _, id_conflicto = is_empty_relation_in_matrix(matrix_dim, None, None, relation_draw, in_draw=True)
            if not is_empty_position:
                conflicto_texto_relacion = True

            update_relation_in_matrix(matrix_dim, relation_draw)

            pos_label_aprox = None
            if conflicto_texto_relacion:
                x_dest_draw_arrow = x_dest_draw
                x_origen_draw_arrow = x_origen_draw
                y_dest_draw_arrow = y_dest_draw
                y_origen_draw_arrow = y_origen_draw
                MULTIPLICADOR_PTE = 1.5
                pte = 0
                if x_dest_draw - x_origen_draw != 0 and ((y_dest_draw - y_origen_draw) / (x_dest_draw - x_origen_draw)) != 0:
                    pte = abs(1/((y_dest_draw - y_origen_draw) / (x_dest_draw - x_origen_draw))) * MULTIPLICADOR_PTE

                if relation_draw.direccion_actual == DIR_DCHA:
                    x_dest_draw_arrow = x_dest_draw - relation_draw.get_tam_texto_real(ax)/2 - 0.5
                    x_origen_draw_arrow = x_origen_draw + relation_draw.get_tam_texto_real(ax)/2 + 0.5
                elif relation_draw.direccion_actual == DIR_IZQ:
                    x_dest_draw_arrow = x_dest_draw + relation_draw.get_tam_texto_real(ax)/2 + 0.5
                    x_origen_draw_arrow = x_origen_draw - relation_draw.get_tam_texto_real(ax)/2 - 0.5
                elif relation_draw.direccion_actual == DIR_ARRIBA:
                    y_dest_draw_arrow = y_dest_draw - 1.5
                    y_origen_draw_arrow = y_origen_draw + 1.5
                elif relation_draw.direccion_actual == DIR_ABAJO:
                    y_dest_draw_arrow = y_dest_draw + 1.5
                    y_origen_draw_arrow = y_origen_draw

                elif relation_draw.direccion_actual == DIR_DCHA_ARRIBA:
                    x_dest_draw_arrow = x_dest_draw - pte
                    y_dest_draw_arrow = y_dest_draw - 1.5
                    x_origen_draw_arrow = x_origen_draw - pte
                    y_origen_draw_arrow = y_origen_draw + 1.5
                elif relation_draw.direccion_actual == DIR_DCHA_ABAJO:
                    x_dest_draw_arrow = x_dest_draw - pte
                    y_dest_draw_arrow = y_dest_draw + 1.5
                    x_origen_draw_arrow = x_origen_draw - pte
                    y_origen_draw_arrow = y_origen_draw - 1.5
                elif relation_draw.direccion_actual == DIR_IZQ_ARRIBA:
                    x_dest_draw_arrow = x_dest_draw + pte
                    y_dest_draw_arrow = y_dest_draw - 1.5
                    x_origen_draw_arrow = x_origen_draw + pte
                    y_origen_draw_arrow = y_origen_draw + 1.5
                elif relation_draw.direccion_actual == DIR_IZQ_ABAJO:
                    x_dest_draw_arrow = x_dest_draw + pte
                    y_dest_draw_arrow = y_dest_draw + 1.5
                    x_origen_draw_arrow = x_origen_draw + pte
                    y_origen_draw_arrow = y_origen_draw - 1.5

                if len(pal_origen.list_palabras_relacionadas_1er_grado) < len(pal_dest.list_palabras_relacionadas_1er_grado):
                    pos_label_aprox = (x_origen_draw_arrow, y_origen_draw_arrow)
                else:
                    pos_label_aprox = (x_dest_draw_arrow, y_dest_draw_arrow)

            draw_edge(
                ax,
                (x_origen_draw, y_origen_draw),
                (x_dest_draw, y_dest_draw),
                color=color,
                label=relation_draw.texto,
                label_offset=(0, 0.4),
                curve = curve,
                label_centered=not(conflicto_texto_relacion),
                pos_label_aprox=pos_label_aprox
            )
        except Exception as e:
            logger.debug("Error al dibujar la relación " + str(e))


def draw_all_nodes(ax, position_elems, list_palabras):
    for pal, (x, y) in position_elems.items():
        node_text = pal.texto
        if ZOOM_ACTIVE and pal not in list_palabras:
            continue
        logger.info(pal.texto)
        color_figura = pal.color_figura
        tipo_figura = pal.tipo_figura

        if tipo_figura == FIGURA_ELIPSE:
        #if pal.lugar_sintactico.lower() in (TYPE_SINTAX_ROOT):
            pal.tipo_figura = FIGURA_ELIPSE
            pal.tam_eje_y_figura = tam_figuras.ELIPSE[1] * (pal.dimension_y + pal.cte_sum_y)
            pal.tam_eje_x_figura = tam_figuras.ELIPSE[0] * (pal.dimension_x + pal.cte_sum_x)
            ellipse_width = tam_figuras.ELIPSE[2] * (pal.dimension_x + pal.cte_sum_x + 0.5)
            #ellipse_height = pal.tam_eje_y_figura

            ellipse = Ellipse((x, y), width=ellipse_width, height=1.2,
                              facecolor=dict_color_figura.get(pal.lugar_sintactico, color_figura), zorder=2 , edgecolor='black')
            ax.add_patch(ellipse)
            ax.text(x, y, node_text, fontsize=12, ha='center', va='center', zorder=3,
                    color=dict_color_figura_letra.get(pal.lugar_sintactico, colores.black))

        elif tipo_figura == FIGURA_CIRCULO:
        #elif pal.lugar_sintactico.lower() in (TYPE_SINTAX_ROOT):
            pal.tipo_figura = FIGURA_CIRCULO
            pal.tam_eje_y_figura = tam_figuras.CIRCULO[1] * (pal.dimension_y)
            pal.tam_eje_x_figura = tam_figuras.CIRCULO[0] * (pal.dimension_x)
            circle_width = tam_figuras.CIRCULO[2] * (pal.dimension_x + pal.cte_sum_x)
            circle = Circle((x, y), radius=circle_width, facecolor=dict_color_figura.get(pal.lugar_sintactico, color_figura),
                            zorder=2, edgecolor='black')
            ax.add_patch(circle)
            ax.text(x, y, node_text, fontsize=12, ha='center', va='center', zorder=3,
                    color=dict_color_figura_letra.get(pal.lugar_sintactico, colores.black))


        elif pal.tipo_figura == FIGURA_RECTANGULO:
        #elif pal.lugar_sintactico.lower() in (TYPE_SINTAX_AMOD, TYPE_SINTAX_NMOD):
            pal.tipo_figura = FIGURA_RECTANGULO
            pal.tam_eje_y_figura = tam_figuras.RECTANGULO[1] * (pal.dimension_y)
            pal.tam_eje_x_figura = tam_figuras.RECTANGULO[0] * (pal.dimension_x)
            if pal.tam_eje_x_figura < 2:
                pal.tam_eje_x_figura = 2
            rectangle_width = pal.tam_eje_x_figura
            rectangle = Rectangle((x - rectangle_width / 2, y - 0.4*pal.dimension_y), width=rectangle_width, height=1,
                                  facecolor=dict_color_figura.get(pal.lugar_sintactico, color_figura),
                                  edgecolor='black', zorder=2)
            ax.add_patch(rectangle)
            ax.text(x, y, node_text, fontsize=12, ha='center', va='center', zorder=3,
                    color=dict_color_figura_letra.get(pal.lugar_sintactico, colores.black))
        #
        elif pal.lugar_sintactico.lower() in (): #(TYPE_SINTAX_FLAT):
            pal.tipo_figura = FIGURA_HEXAGONO
            pal.tam_eje_y_figura = tam_figuras.HEXAGONO[1] * (pal.dimension_y)
            pal.tam_eje_x_figura = tam_figuras.HEXAGONO[0] * (pal.dimension_x)
            polygon_radius = 0.4 * len(node_text)
            polygon = RegularPolygon((x, y), numVertices=6, radius=polygon_radius, orientation=0,
                                     color=dict_color_figura.get(pal.lugar_sintactico, color_figura), zorder=2)
            ax.add_patch(polygon)
            ax.text(x, y, node_text, fontsize=12, ha='center', va='center', zorder=3,
                    color=dict_color_figura_letra.get(pal.lugar_sintactico, colores.black))
        #
        elif pal.lugar_sintactico.lower() in ():
            pal.tipo_figura = FIGURA_RECTANGULO
            pal.tam_eje_y_figura = tam_figuras.RECTANGULO[1] * (pal.dimension_y)
            pal.tam_eje_x_figura = tam_figuras.RECTANGULO[0] * (pal.dimension_x)
            rectangle_width = tam_figuras.RECTANGULO[0] * pal.dimension_x
            rectangle = Rectangle((x - rectangle_width / 2, y - 0.4*pal.dimension_y), width=rectangle_width, height=0.5,
                                  color=dict_color_figura.get(pal.lugar_sintactico, color_figura),
                                  zorder=2)
            ax.add_patch(rectangle)
            ax.text(x, y, node_text, fontsize=12, ha='center', va='center', zorder=3,
                    color=dict_color_figura_letra.get(pal.lugar_sintactico, colores.black))
        else:
            pal.tipo_figura = FIGURA_RECTANGULO
            pal.tam_eje_y_figura = tam_figuras.RECTANGULO[1] * (pal.dimension_y)
            pal.tam_eje_x_figura = tam_figuras.RECTANGULO[0] * (pal.dimension_x)
            if pal.tam_eje_x_figura < 2:
                pal.tam_eje_x_figura = 2
            rectangle_width = pal.tam_eje_x_figura
            height = 1  # pal.dimension_y
            tamano_texto = 12

            rectangle = Rectangle(
                xy=(x - rectangle_width / 2, y - height * 0.4),
                width=rectangle_width,
                height=height,
                #color=dict_color_figura.get(pal.lugar_sintactico, color_figura),
                facecolor=colores.white,
                edgecolor='black',
                zorder=2)
            ax.add_patch(rectangle)
            ax.text(x, y, node_text, fontsize=12, ha='center', va='center',
                    zorder=3, color=dict_color_figura_letra.get(pal.lugar_sintactico, colores.black))

            # ellipse_width = 0.1 * len(node) + 0.2
            # ellipse_height = 0.4
            # ellipse = Ellipse((x, y), width=ellipse_width, height=ellipse_height, color=dict_color_figura[None], zorder=2)
            # ax.add_patch(ellipse)
            # ax.text(x, y, node, fontsize=12, ha='center', va='center', zorder=3, color=dict_color_figura_letra.get(pal.lugar_sintactico, colores.black))


