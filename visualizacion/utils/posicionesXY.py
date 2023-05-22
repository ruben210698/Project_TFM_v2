from visualizacion.utils.matrix_functions import get_pos_media_matrix, is_empty_relation_in_matrix
from constants.direcciones_relaciones import DIR_DCHA, DIR_DCHA_ABAJO, DIR_DCHA_ARRIBA, DIR_ABAJO, DIR_ARRIBA, \
    DIR_IZQ, DIR_IZQ_ARRIBA, DIR_IZQ_ABAJO, FIND_DIR_CENTRO, FIND_DIR_DCHA, FIND_DIR_DCHA_ABAJO, FIND_DIR_DCHA_ARRIBA, \
    FIND_DIR_ABAJO, FIND_DIR_ARRIBA, FIND_DIR_IZQ, FIND_DIR_IZQ_ARRIBA, FIND_DIR_IZQ_ABAJO, DICT_DIR_BY_ORIGEN, CENTRO
from visualizacion.utils.matrix_functions import ampliar_matriz, is_empty_pos_matrix, find_better_center_position, imprimir_matriz
import logging
from utils.logger import FORMAT_1
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL) #######################################################
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter(FORMAT_1)

# add formatter to ch
ch.setFormatter(formatter)
logger.addHandler(ch)
if (logger.hasHandlers()):
    logger.handlers.clear()


def get_dir_relativa(palabra_origen, palabra_dest):
    if palabra_origen.pos_y > palabra_dest.pos_y:
        if palabra_origen.pos_x < palabra_dest.pos_x:
            return DIR_DCHA_ABAJO
        elif palabra_origen.pos_x > palabra_dest.pos_x:
            return DIR_IZQ_ABAJO
        else:
            return DIR_ABAJO
    elif palabra_origen.pos_y < palabra_dest.pos_y:
        if palabra_origen.pos_x < palabra_dest.pos_x:
            return DIR_DCHA_ARRIBA
        elif palabra_origen.pos_x > palabra_dest.pos_x:
            return DIR_IZQ_ARRIBA
        else:
            return DIR_ARRIBA
    else:
        if palabra_origen.pos_x < palabra_dest.pos_x:
            return DIR_DCHA
        elif palabra_origen.pos_x > palabra_dest.pos_x:
            return DIR_IZQ
        else:
            return CENTRO



def update_list_dir_order(relation):
    try:
        logger.info(f"-----Fallo en la direccion {relation.pal_origen.texto} :: {relation.pal_dest.texto}")
    except:
        pass
    list_dir_origen_actual = relation.pal_origen.deprec_lista_direcciones_orden
    dir_pal_origen = relation.pal_origen.direccion_origen_tmp
    num_dir_pal_origen = len(list_dir_origen_actual)
    find_dir = DICT_DIR_BY_ORIGEN.get(dir_pal_origen)

    if num_dir_pal_origen > len(find_dir)-1:
        new_list_direcciones_orden = find_dir[-1]
    else:
        new_list_direcciones_orden = find_dir[num_dir_pal_origen]  # antes se le restaba 1

    relation.pal_origen.deprec_lista_direcciones_orden = new_list_direcciones_orden
    # relation.pal_origen.pos_actual_recorrer_dir_relaciones += 1  # de esta forma se salta el elemento actual
    ## No esto no lo hagas porque sino sumas 2, que ahora he puesto el bucle como While

    # No ha sido encontrado. Hay que buscar la siguiente posicion.
    # En caso de que falle, tengo que pasar a la siguiente lista de direccion y buscar la siguiente posicion.
    #  esto como se haria? pues se me ocurre:
    # 1. aqui haces eso de pasar a la siguiente lista de direccion.
    # 2. aumentas en 1 el numero de direccion de la palabra origen y luego en la funcion principal compruebas que
    # es ese el que tocaba o no
    # 3. Si no es el que tocaba, tienes que repetir esa relacion pero con esa nueva direccion que le vas a asignar
    # tal vez haya que sacar esa parte a una nueva funcion para poder llamarle aunque el bucle no lo permita.
    # Ya sabes, un while Dir_ok == False:  y dentro esa mierda :)



RECTA_DISTANCIA_DE_INTENTO_X = 15

def get_pos_dir_dcha(matrix_dim, palabra, relation):
    if relation is None:
        return None, None, matrix_dim
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    pos_y = relation.pal_tmp_opuesta.pos_y + pos_y_media
    pos_x = relation.pal_tmp_opuesta.pos_x + pos_x_media + \
            (relation.pal_tmp_opuesta.dimension_x + relation.pal_tmp_opuesta.cte_sum_x)//2 + \
            (palabra.dimension_x + palabra.cte_sum_x)//2 + \
            (relation.tam_text + relation.cte_sum_x)

    for x_loop in range(pos_x, pos_x + RECTA_DISTANCIA_DE_INTENTO_X, 1):
        is_empty, matrix_dim, id_conflict = is_empty_pos_matrix(
                matrix_dim, pos_y, x_loop,
                dim_y=palabra.dimension_y + palabra.cte_sum_y,
                dim_x=palabra.dimension_x + palabra.cte_sum_x)
        if is_empty:
            is_empty, matrix_dim, id_conflict = is_empty_relation_in_matrix(matrix_dim, pos_y, x_loop, relation)
            if is_empty:
                return pos_y, x_loop, matrix_dim

    update_list_dir_order(relation)

    return None, None, matrix_dim


def get_pos_dir_izq(matrix_dim, palabra, relation):
    if relation is None:
        return None, None, matrix_dim
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)

    pos_y = relation.pal_tmp_opuesta.pos_y + pos_y_media
    # la posicion x es la izquierda, no el centro, por tanto no hay que restarle nada
    pos_x = relation.pal_tmp_opuesta.pos_x + pos_x_media - \
            (relation.pal_tmp_opuesta.dimension_x + relation.pal_tmp_opuesta.cte_sum_x)//2 - \
            (palabra.dimension_x + palabra.cte_sum_x) // 2 - \
            (relation.tam_text + relation.cte_sum_x)

    for x_loop in range(pos_x, pos_x - RECTA_DISTANCIA_DE_INTENTO_X, -1):
        is_empty, matrix_dim, id_conflict = is_empty_pos_matrix(
                matrix_dim, pos_y, x_loop,
                dim_y=palabra.dimension_y + palabra.cte_sum_y,
                dim_x=palabra.dimension_x + palabra.cte_sum_x)
        if is_empty:
            is_empty, matrix_dim, id_conflict = is_empty_relation_in_matrix(matrix_dim, pos_y, x_loop, relation)
            if is_empty:
                return pos_y, x_loop, matrix_dim

    update_list_dir_order(relation)

    return None, None, matrix_dim





RECTA_DISTANCIA_DE_INTENTO_Y = 15
RECTA_MARGIN = 40
ARRIBA_MARGIN_MIN = 3

def get_pos_dir_arriba(matrix_dim, palabra, relation):
    if relation is None:
        return None, None, matrix_dim
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    pos_y = relation.pal_tmp_opuesta.pos_y + pos_y_media + (palabra.dimension_y + palabra.cte_sum_y)//2 + ARRIBA_MARGIN_MIN + relation.cte_sum_y
    pos_x = relation.pal_tmp_opuesta.pos_x + pos_x_media

    for y_loop in range(pos_y, pos_y + RECTA_DISTANCIA_DE_INTENTO_Y, 1):
        is_empty, matrix_dim, id_conflict = is_empty_pos_matrix(
                matrix_dim, y_loop, pos_x,
                dim_y=palabra.dimension_y + palabra.cte_sum_y,
                dim_x=palabra.dimension_x + palabra.cte_sum_x,
                margen_x=RECTA_MARGIN)
        if is_empty:
            is_empty, matrix_dim, id_conflict = is_empty_relation_in_matrix(matrix_dim, y_loop, pos_x, relation)
            if is_empty:
                return y_loop, pos_x, matrix_dim

    update_list_dir_order(relation)

    return None, None, matrix_dim


def get_pos_dir_abajo(matrix_dim, palabra, relation):
    if relation is None:
        return None, None, matrix_dim
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)

    pos_y = relation.pal_tmp_opuesta.pos_y + pos_y_media - (palabra.dimension_y + palabra.cte_sum_y)//2 - ARRIBA_MARGIN_MIN - relation.cte_sum_y
    pos_x = relation.pal_tmp_opuesta.pos_x + pos_x_media

    for y_loop in range(pos_y, pos_y - RECTA_DISTANCIA_DE_INTENTO_Y, -1):
        is_empty, matrix_dim, id_conflict = is_empty_pos_matrix(
                matrix_dim, y_loop, pos_x,
                dim_y=palabra.dimension_y + palabra.cte_sum_y,
                dim_x=palabra.dimension_x + palabra.cte_sum_x,
                margen_x=RECTA_MARGIN)  # va a la dcha
        if is_empty:
            is_empty, matrix_dim, id_conflict = is_empty_relation_in_matrix(matrix_dim, y_loop, pos_x, relation)
            if is_empty:
                return y_loop, pos_x, matrix_dim

    update_list_dir_order(relation)

    return None, None, matrix_dim





DIAGONAL_DISTANCIA_DE_INTENTO_Y = 3
DIAGONAL_Y_1 = 0
DIAGONAL_Y_2 = 3
DIAGONAL_Y_3 = 6
DIAGONAL_Y_4 = 9
DIAGONAL_Y_5 = 12
DIAGONAL_LIST_YS = [DIAGONAL_Y_1, DIAGONAL_Y_2]
DIAGONAL_DISTANCIA_DE_INTENTO_X = 3
DIAGONAL_X_1 = 0
DIAGONAL_X_2 = 3
DIAGONAL_X_3 = 6
DIAGONAL_X_4 = 9
DIAGONAL_X_5 = 12
DIAGONAL_LIST_XS = [DIAGONAL_X_1, DIAGONAL_X_2]
DIAGONAL_MARGIN_X = 40


def get_pos_dir_dcha_arriba(matrix_dim, palabra, relation):
    if relation is None:
        return None, None, matrix_dim

    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    for i in range(0, len(DIAGONAL_LIST_YS)):
        pos_y = relation.pal_tmp_opuesta.pos_y + pos_y_media + DIAGONAL_LIST_YS[i] + relation.cte_sum_y
        pos_x = relation.pal_tmp_opuesta.pos_x + pos_x_media + \
                (relation.pal_tmp_opuesta.dimension_x + relation.pal_tmp_opuesta.cte_sum_x)//2 + \
                (palabra.dimension_x + palabra.cte_sum_x)//2 + \
                (relation.tam_text + relation.cte_sum_x) + \
                DIAGONAL_LIST_XS[i]

        for y_loop in range(pos_y, pos_y + DIAGONAL_DISTANCIA_DE_INTENTO_Y, 1):
            for x_loop in range(pos_x, pos_x + DIAGONAL_DISTANCIA_DE_INTENTO_X, 1):
                is_empty, matrix_dim, id_conflict = is_empty_pos_matrix(
                        matrix_dim, y_loop, x_loop,
                        dim_y=palabra.dimension_y + palabra.cte_sum_y,
                        dim_x=palabra.dimension_x + palabra.cte_sum_x,
                        margen_x=DIAGONAL_MARGIN_X)
                if is_empty:
                    is_empty, matrix_dim, id_conflict = is_empty_relation_in_matrix(matrix_dim, y_loop, x_loop, relation)
                    if is_empty:
                        return pos_y, x_loop, matrix_dim

    update_list_dir_order(relation)
    return None, None, matrix_dim


def get_pos_dir_dcha_abajo(matrix_dim, palabra, relation):
    if relation is None:
        return None, None, matrix_dim

    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    for i in range(0, len(DIAGONAL_LIST_YS)):
        pos_y = relation.pal_tmp_opuesta.pos_y + pos_y_media - DIAGONAL_LIST_YS[i] - relation.cte_sum_y
        pos_x = relation.pal_tmp_opuesta.pos_x + pos_x_media + \
                (relation.pal_tmp_opuesta.dimension_x + relation.pal_tmp_opuesta.cte_sum_x) // 2 + \
                (palabra.dimension_x + palabra.cte_sum_x) // 2 + \
                (relation.tam_text + relation.cte_sum_x) + \
                DIAGONAL_LIST_XS[i]


        for y_loop in range(pos_y, pos_y - DIAGONAL_DISTANCIA_DE_INTENTO_Y, -1):
            for x_loop in range(pos_x, pos_x + DIAGONAL_DISTANCIA_DE_INTENTO_X, 1):
                is_empty, matrix_dim, id_conflict = is_empty_pos_matrix(
                        matrix_dim, y_loop, x_loop,
                        dim_y=palabra.dimension_y + palabra.cte_sum_y,
                        dim_x=palabra.dimension_x + palabra.cte_sum_x,
                        margen_x=DIAGONAL_MARGIN_X)
                if is_empty:
                    is_empty, matrix_dim, id_conflict = is_empty_relation_in_matrix(matrix_dim, y_loop, x_loop, relation)
                    if is_empty:
                        return pos_y, x_loop, matrix_dim

    update_list_dir_order(relation)

    return None, None, matrix_dim


def get_pos_dir_izq_abajo(matrix_dim, palabra, relation):
    if relation is None:
        return None, None, matrix_dim

    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    for i in range(0, len(DIAGONAL_LIST_YS)):
        pos_y = relation.pal_tmp_opuesta.pos_y + pos_y_media - DIAGONAL_LIST_YS[i] - relation.cte_sum_y
        pos_x = relation.pal_tmp_opuesta.pos_x + pos_x_media - \
                (relation.pal_tmp_opuesta.dimension_x + relation.pal_tmp_opuesta.cte_sum_x) // 2 - \
                (palabra.dimension_x + palabra.cte_sum_x) // 2 - \
                (relation.tam_text + relation.cte_sum_x) - \
                DIAGONAL_LIST_XS[i]

        for y_loop in range(pos_y, pos_y - DIAGONAL_DISTANCIA_DE_INTENTO_Y, -1):
            for x_loop in range(pos_x, pos_x - DIAGONAL_DISTANCIA_DE_INTENTO_X, -1):
                is_empty, matrix_dim, id_conflict = is_empty_pos_matrix(
                        matrix_dim, y_loop, x_loop,
                        dim_y=palabra.dimension_y + palabra.cte_sum_y,
                        dim_x=palabra.dimension_x + palabra.cte_sum_x,
                        margen_x=-DIAGONAL_MARGIN_X)
                if is_empty:
                    is_empty, matrix_dim, id_conflict = is_empty_relation_in_matrix(matrix_dim, y_loop, x_loop, relation)
                    if is_empty:
                        return pos_y, x_loop, matrix_dim

    update_list_dir_order(relation)
    return None, None, matrix_dim


def get_pos_dir_izq_arriba(matrix_dim, palabra, relation):
    if relation is None:
        return None, None, matrix_dim

    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    for i in range(0, len(DIAGONAL_LIST_YS)):
        pos_y = relation.pal_tmp_opuesta.pos_y + pos_y_media + DIAGONAL_LIST_YS[i] + relation.cte_sum_y
        pos_x = relation.pal_tmp_opuesta.pos_x + pos_x_media - \
                (relation.pal_tmp_opuesta.dimension_x + relation.pal_tmp_opuesta.cte_sum_x) // 2 - \
                (palabra.dimension_x + palabra.cte_sum_x) // 2 - \
                (relation.tam_text + relation.cte_sum_x) - \
                DIAGONAL_LIST_XS[i]

        for y_loop in range(pos_y, pos_y + DIAGONAL_DISTANCIA_DE_INTENTO_Y, 1):
            for x_loop in range(pos_x, pos_x - DIAGONAL_DISTANCIA_DE_INTENTO_X, -1):
                is_empty, matrix_dim, id_conflict = is_empty_pos_matrix(
                        matrix_dim, y_loop, x_loop,
                        dim_y=palabra.dimension_y + palabra.cte_sum_y,
                        dim_x=palabra.dimension_x + palabra.cte_sum_x,
                        margen_x=-DIAGONAL_MARGIN_X)
                if is_empty:
                    is_empty, matrix_dim, id_conflict = is_empty_relation_in_matrix(matrix_dim, y_loop, x_loop, relation)
                    if is_empty:
                        return pos_y, x_loop, matrix_dim

    update_list_dir_order(relation)
    return None, None, matrix_dim

def get_next_location(matrix_dim, palabra, relation):
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    dir_origen = palabra.direccion_origen_tmp
    pos_y, pos_x = pos_y_media, pos_x_media

    if dir_origen == CENTRO or relation is None:
        pos_y, pos_x, matrix_dim = find_better_center_position(matrix_dim, palabra, pos_y_media, pos_x_media)

    elif dir_origen == DIR_DCHA:
        pos_y, pos_x, matrix_dim = get_pos_dir_dcha(matrix_dim, palabra, relation)

    elif dir_origen == DIR_IZQ:
        pos_y, pos_x, matrix_dim = get_pos_dir_izq(matrix_dim, palabra, relation)

    elif dir_origen == DIR_ARRIBA:
        pos_y, pos_x, matrix_dim = get_pos_dir_arriba(matrix_dim, palabra, relation)

    elif dir_origen == DIR_ABAJO:
        pos_y, pos_x, matrix_dim = get_pos_dir_abajo(matrix_dim, palabra, relation)

    elif dir_origen == DIR_DCHA_ARRIBA:
        pos_y, pos_x, matrix_dim = get_pos_dir_dcha_arriba(matrix_dim, palabra, relation)

    elif dir_origen == DIR_DCHA_ABAJO:
        pos_y, pos_x, matrix_dim = get_pos_dir_dcha_abajo(matrix_dim, palabra, relation)

    elif dir_origen == DIR_IZQ_ARRIBA:
        pos_y, pos_x, matrix_dim = get_pos_dir_izq_arriba(matrix_dim, palabra, relation)

    elif dir_origen == DIR_IZQ_ABAJO:
        pos_y, pos_x, matrix_dim = get_pos_dir_izq_abajo(matrix_dim, palabra, relation)

    return pos_y, pos_x, matrix_dim
