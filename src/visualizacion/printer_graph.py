
import random
import shutil
import os

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, RegularPolygon, Ellipse, Rectangle, Circle

from utils.Grafo import Grafo
from utils.Palabra import Palabra

from constants import type_sintax
from constants import colores_figura, colores_figura_letra, colores
from constants.figuras import *
from constants import tam_figuras

from utils.utils_text import truncate_a_8_relaciones

from constants.direcciones_relaciones import DIR_DCHA, DIR_DCHA_ABAJO, DIR_DCHA_ARRIBA, DIR_ABAJO, DIR_ARRIBA, \
    DIR_IZQ, DIR_IZQ_ARRIBA, DIR_IZQ_ABAJO, CENTRO, OPOSIT_DIR
from visualizacion.utils.direcciones import refresh_directions, get_rel_origen_and_dest_unidas
from visualizacion.utils.posicionesXY import get_next_location
from visualizacion.utils.matrix_functions import generate_matrix, get_pos_media_matrix, imprimir_matriz, \
    reducir_tam_matriz, ampliar_matriz, is_empty_relation_in_matrix

import logging
from utils.logger import FORMAT_1, create_logger

PAL_DEBUG = 'naturaleza'
PAL_DEBUG = os.getenv('PAL_DEBUG', '')
ZOOM_ACTIVE = eval(os.getenv('ZOOM_ACTIVE', 'True'))

PRINT_IMG = eval(os.getenv('PRINT_IMG', 'True'))
PRINT_GRAPH = eval(os.getenv('PRINT_GRAPH', 'True'))

MODE_DEBUG = "DEBUG"
MODE_NORMAL = "NORMAL"
EX_MODE = MODE_DEBUG


create_logger()
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






def print_graph(list_palabras, list_relaciones, position_elems, matrix_dim, final=False):
    try:
        if list_palabras == []:
            return None
        if PRINT_IMG or final:
            return _print_graph(list_palabras, list_relaciones, position_elems, matrix_dim)
    except Exception as e:
        print(e)
        return None



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
    dim_pal_max_x = 3 if list_max_x[0].dimension_x < 3 else list_max_x[0].dimension_x
    max_axis_x = dim_pal_max_x + list_max_x[0].pos_x

    min_axis_x = min([x[0] for x in position_elems.values()])
    list_min_x = list([x for x in position_elems.keys() if position_elems.get(x)[0] - x.dimension_x <= min_axis_x])
    list_min_x.sort(key=lambda x: position_elems.get(x)[0] - x.dimension_x, reverse=False)
    dim_pal_min_x = 3 if list_min_x[0].dimension_x < 3 else list_min_x[0].dimension_x
    min_axis_x = list_min_x[0].pos_x - dim_pal_min_x


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
        list_pal_grafo_anterior = list(set(new_list_pal.copy()))

    for list_palabras_custom in list_palabras_zoom:
        list_relaciones_new = get_relations_from_list_words(list_relaciones_all, list_palabras_custom)
        list_relaciones_zoom.append(list_relaciones_new)

    return list_palabras_zoom, list_relaciones_zoom



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

    return list(set(list_relaciones))



# Función para dibujar aristas con flechas
def draw_edge(ax, u, v, width=1.0, color='k', label='', label_offset=(0, 0), bold=False, curve=True,
              label_centered=True, pos_label_aprox=None):
    # En caso de que el parametro curve sea True, se dibujará la flecha pero con un poco de curvatura
    # es decir, que la felcha en vez de ir del punto A al B en linea recta, traza una pequeá parábola
    x_label = 0
    y_label = 0
    color = colores.black
    if curve:
        annotation = ax.annotate('', xy=u, xytext=v,
                                 arrowprops=dict(facecolor=color, edgecolor=color, shrink=0.05,
                                                 connectionstyle="arc3,rad=-0.4", zorder=-1),
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
            # print(u, v, midpoint)
            # print("ok")

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
        elif label:  # and not label_centered
            x_label = pos_label_aprox[0] + label_offset[0]
            y_label = pos_label_aprox[1] + label_offset[1]

    if label:
        if bold:
            ax.text(x_label, y_label, label, fontname='Times New Roman', fontsize=15, ha='center', va='center',
                    zorder=3, weight='bold')
        else:
            ax.text(x_label, y_label, label, fontname='Times New Roman', fontsize=15, ha='center', va='center',
                    zorder=3)


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
                x_origen_draw = coord_pal_origen[0] + pal_origen.tam_eje_x_figura/2 - 0.3
            elif relation_draw.direccion_actual == DIR_IZQ:
                x_dest_draw = coord_pal_dest[0] + pal_dest.tam_eje_x_figura/2
                x_origen_draw = coord_pal_origen[0] - pal_origen.tam_eje_x_figura/2 + 0.3
            elif relation_draw.direccion_actual == DIR_ARRIBA:
                y_dest_draw = coord_pal_dest[1] - pal_dest.tam_eje_y_figura/2 - 0.4
                y_origen_draw = coord_pal_origen[1] + pal_origen.tam_eje_y_figura/2 - 0.3
            elif relation_draw.direccion_actual == DIR_ABAJO:
                y_dest_draw = coord_pal_dest[1] + pal_dest.tam_eje_y_figura/2 + 0.4
                y_origen_draw = coord_pal_origen[1] - pal_origen.tam_eje_y_figura/2 + 0.3

            elif relation_draw.direccion_actual == DIR_DCHA_ARRIBA:
                x_dest_draw = coord_pal_dest[0] - pal_dest.tam_eje_x_figura/2 - 0.2
                y_dest_draw = coord_pal_dest[1] - pal_dest.tam_eje_y_figura/2 - 0.4
                x_origen_draw = coord_pal_origen[0] + pal_origen.tam_eje_x_figura/2 - 0.5
                y_origen_draw = coord_pal_origen[1] + pal_origen.tam_eje_y_figura/2 - 0.3
                if x_dest_draw < x_origen_draw - 2:
                    x_dest_draw = coord_pal_dest[0]
                    x_origen_draw = coord_pal_origen[0] + 1
            elif relation_draw.direccion_actual == DIR_DCHA_ABAJO:
                x_dest_draw = coord_pal_dest[0] - pal_dest.tam_eje_x_figura/2 - 0.2
                y_dest_draw = coord_pal_dest[1] + pal_dest.tam_eje_y_figura/2 + 0.4
                x_origen_draw = coord_pal_origen[0] + pal_origen.tam_eje_x_figura/2 - 0.5
                y_origen_draw = coord_pal_origen[1] - pal_origen.tam_eje_y_figura/2 + 0.3
                if x_dest_draw < x_origen_draw - 2:
                    x_dest_draw = coord_pal_dest[0]
                    x_origen_draw = coord_pal_origen[0] + 1
            elif relation_draw.direccion_actual == DIR_IZQ_ARRIBA:
                x_dest_draw = coord_pal_dest[0] + pal_dest.tam_eje_x_figura/2 + 0.2
                y_dest_draw = coord_pal_dest[1] - pal_dest.tam_eje_y_figura/2 - 0.4
                x_origen_draw = coord_pal_origen[0] - pal_origen.tam_eje_x_figura/2 + 0.5
                y_origen_draw = coord_pal_origen[1] + pal_origen.tam_eje_y_figura/2 - 0.3
                if x_dest_draw > x_origen_draw - 2:
                    x_dest_draw = coord_pal_dest[0]
                    x_origen_draw = coord_pal_origen[0] - 1
            elif relation_draw.direccion_actual == DIR_IZQ_ABAJO:
                x_dest_draw = coord_pal_dest[0] + pal_dest.tam_eje_x_figura/2 + 0.2
                y_dest_draw = coord_pal_dest[1] + pal_dest.tam_eje_y_figura/2 + 0.4
                x_origen_draw = coord_pal_origen[0] - pal_origen.tam_eje_x_figura/2 + 0.5
                y_origen_draw = coord_pal_origen[1] - pal_origen.tam_eje_y_figura/2 + 0.3
                if x_dest_draw > x_origen_draw - 2:
                    x_dest_draw = coord_pal_dest[0]
                    x_origen_draw = coord_pal_origen[0] - 1
            else:
                # TODO: que si no tiene direccion_actual, la calcule :)
                logger.info("Error: dirección no contemplada", relation_draw.texto)
                logger.info("###########")

            if relation_draw.pal_dest.tipo_figura == FIGURA_ROMBO:
                x_dest_draw, x_origen_draw, y_dest_draw, y_origen_draw = \
                    calculo_flecha_dest_rombo(coord_pal_dest,
                                              coord_pal_origen,
                                              pal_dest, pal_origen,
                                              relation_draw,
                                              x_dest_draw,
                                              x_origen_draw,
                                              y_dest_draw,
                                              y_origen_draw)

            if relation_draw.pal_origen.tipo_figura == FIGURA_ROMBO:
                x_dest_draw, x_origen_draw, y_dest_draw, y_origen_draw = \
                    calculo_flecha_origen_rombo(coord_pal_dest,
                                              coord_pal_origen,
                                              pal_dest, pal_origen,
                                              relation_draw,
                                              x_dest_draw,
                                              x_origen_draw,
                                              y_dest_draw,
                                              y_origen_draw)



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
            # TODO arreglar ##############################
            conflicto_texto_relacion = False
            ##############################################
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


def calculo_flecha_dest_rombo(coord_pal_dest, coord_pal_origen, pal_dest, pal_origen, relation_draw, x_dest_draw,
                              x_origen_draw, y_dest_draw, y_origen_draw):
    """

            pal.tam_eje_x_figura = tam_figuras.ROMBO[0] * pal.dimension_x
            pal.tam_eje_y_figura = (tam_figuras.ROMBO[1] * pal.dimension_x) + pal.dimension_y
            # Crear el rombo
            vertices = [(x - pal.tam_eje_x_figura / 2, y),  # Punto izquierdo
                        (x, y + pal.tam_eje_y_figura / 2),  # Punto superior
                        (x + pal.tam_eje_x_figura / 2, y),  # Punto derecho
                        (x, y - pal.tam_eje_y_figura / 2)]  # Punto inferior


    """
    if relation_draw.direccion_actual == DIR_DCHA:
        x_dest_draw = coord_pal_dest[0] - pal_dest.tam_eje_x_figura / 2 - 0.5
    elif relation_draw.direccion_actual == DIR_IZQ:
        x_dest_draw = coord_pal_dest[0] + pal_dest.tam_eje_x_figura / 2 + 0.5
    elif relation_draw.direccion_actual == DIR_ARRIBA:
        y_dest_draw = coord_pal_dest[1] - pal_dest.tam_eje_y_figura / 2 - 0.4
    elif relation_draw.direccion_actual == DIR_ABAJO:
        y_dest_draw = coord_pal_dest[1] + pal_dest.tam_eje_y_figura / 2 + 0.4

    elif relation_draw.direccion_actual == DIR_DCHA_ARRIBA:
        x_dest_draw = coord_pal_dest[0] - pal_dest.tam_eje_x_figura / 4 - 0.2
        y_dest_draw = coord_pal_dest[1] - pal_dest.tam_eje_y_figura / 4 - 0.2
        if x_dest_draw < x_origen_draw - 2:
            x_dest_draw = coord_pal_dest[0]
    elif relation_draw.direccion_actual == DIR_DCHA_ABAJO:
        x_dest_draw = coord_pal_dest[0] - pal_dest.tam_eje_x_figura / 4 - 0.2
        y_dest_draw = coord_pal_dest[1] + pal_dest.tam_eje_y_figura / 4 + 0.2
        if x_dest_draw < x_origen_draw - 2:
            x_dest_draw = coord_pal_dest[0]
    elif relation_draw.direccion_actual == DIR_IZQ_ARRIBA:
        x_dest_draw = coord_pal_dest[0] + pal_dest.tam_eje_x_figura / 4 + 0.2
        y_dest_draw = coord_pal_dest[1] - pal_dest.tam_eje_y_figura / 4 - 0.2
        if x_dest_draw > x_origen_draw - 2:
            x_dest_draw = coord_pal_dest[0]
    elif relation_draw.direccion_actual == DIR_IZQ_ABAJO:
        x_dest_draw = coord_pal_dest[0] + pal_dest.tam_eje_x_figura / 4 + 0.2
        y_dest_draw = coord_pal_dest[1] + pal_dest.tam_eje_y_figura / 4 + 0.2
        if x_dest_draw > x_origen_draw - 2:
            x_dest_draw = coord_pal_dest[0]
    else:
        logger.info("Error: dirección no contemplada", relation_draw.texto)
        logger.info("###########")
    return x_dest_draw, x_origen_draw, y_dest_draw, y_origen_draw



def calculo_flecha_origen_rombo(coord_pal_dest, coord_pal_origen, pal_dest, pal_origen, relation_draw, x_dest_draw,
                              x_origen_draw, y_dest_draw, y_origen_draw):
    """

            pal.tam_eje_x_figura = tam_figuras.ROMBO[0] * pal.dimension_x
            pal.tam_eje_y_figura = (tam_figuras.ROMBO[1] * pal.dimension_x) + pal.dimension_y
            # Crear el rombo
            vertices = [(x - pal.tam_eje_x_figura / 2, y),  # Punto izquierdo
                        (x, y + pal.tam_eje_y_figura / 2),  # Punto superior
                        (x + pal.tam_eje_x_figura / 2, y),  # Punto derecho
                        (x, y - pal.tam_eje_y_figura / 2)]  # Punto inferior


    """
    if relation_draw.direccion_actual == DIR_DCHA:
        x_origen_draw = coord_pal_origen[0] + pal_origen.tam_eje_x_figura / 2 - 0.5
    elif relation_draw.direccion_actual == DIR_IZQ:
        x_origen_draw = coord_pal_origen[0] - pal_origen.tam_eje_x_figura / 2 + 0.5
    elif relation_draw.direccion_actual == DIR_ARRIBA:
        y_origen_draw = coord_pal_origen[1] + pal_origen.tam_eje_y_figura / 2 - 0.5
    elif relation_draw.direccion_actual == DIR_ABAJO:
        y_origen_draw = coord_pal_origen[1] - pal_origen.tam_eje_y_figura / 2 + 0.5

    elif relation_draw.direccion_actual == DIR_DCHA_ARRIBA:
        x_origen_draw = coord_pal_origen[0] + pal_origen.tam_eje_x_figura / 4 - 0.5
        y_origen_draw = coord_pal_origen[1] + pal_origen.tam_eje_y_figura / 4 - 0.5
        if x_dest_draw < x_origen_draw - 2:
            x_origen_draw = coord_pal_origen[0] + 1
    elif relation_draw.direccion_actual == DIR_DCHA_ABAJO:
        x_origen_draw = coord_pal_origen[0] + pal_origen.tam_eje_x_figura / 4 - 0.5
        y_origen_draw = coord_pal_origen[1] - pal_origen.tam_eje_y_figura / 4 + 0.5
        if x_dest_draw < x_origen_draw - 2:
            x_origen_draw = coord_pal_origen[0] + 1
    elif relation_draw.direccion_actual == DIR_IZQ_ARRIBA:
        x_origen_draw = coord_pal_origen[0] - pal_origen.tam_eje_x_figura / 4 + 0.5
        y_origen_draw = coord_pal_origen[1] + pal_origen.tam_eje_y_figura / 4 - 0.5
        if x_dest_draw > x_origen_draw - 2:
            x_origen_draw = coord_pal_origen[0] - 1
    elif relation_draw.direccion_actual == DIR_IZQ_ABAJO:
        x_origen_draw = coord_pal_origen[0] - pal_origen.tam_eje_x_figura / 4 + 0.5
        y_origen_draw = coord_pal_origen[1] - pal_origen.tam_eje_y_figura / 4 + 0.5
        if x_dest_draw > x_origen_draw - 2:
            x_origen_draw = coord_pal_origen[0] - 1
    else:
        logger.info("Error: dirección no contemplada", relation_draw.texto)
        logger.info("###########")
    return x_dest_draw, x_origen_draw, y_dest_draw, y_origen_draw


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

        elif pal.tipo_figura == FIGURA_ROMBO:
            import matplotlib.patches as patches
            if pal.dimension_x < 3:
                pal.dimension_x = 3
            pal.tam_eje_x_figura = tam_figuras.ROMBO[0] * pal.dimension_x
            pal.tam_eje_y_figura = (tam_figuras.ROMBO[1] * pal.dimension_x) + pal.dimension_y
            # Crear el rombo
            vertices = [(x - pal.tam_eje_x_figura / 2, y),  # Punto izquierdo
                        (x, y + pal.tam_eje_y_figura / 2),  # Punto superior
                        (x + pal.tam_eje_x_figura / 2, y),  # Punto derecho
                        (x, y - pal.tam_eje_y_figura / 2)]  # Punto inferior

            #polygon_radius = 0.4 * len(node_text)
            #polygon = RegularPolygon((x, y), numVertices=4, radius=polygon_radius, orientation=0,
            #                         facecolor=dict_color_figura.get(pal.lugar_sintactico, color_figura),
            #                         edgecolor='black', zorder=2)
            polygon = patches.Polygon(vertices, closed=True,
                                    facecolor=dict_color_figura.get(pal.lugar_sintactico, color_figura),
                                     edgecolor='black', zorder=2)

            ax.add_patch(polygon)
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

