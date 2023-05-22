import os

from utils.Palabra import Palabra

from utils.logger import FORMAT_1
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
##############################################################################################################
##############################################################################################################
# variables de entorno
PRINT_MATRIX = eval(os.getenv('PRINT_MATRIX', 'True'))


DIM_Y_MATRIX = 50
DIM_X_MATRIX = 200
def get_pos_media_matrix(matrix_dim):
    pos_y_media = len(matrix_dim) // 2
    pos_x_media = len(matrix_dim[0]) // 2
    return pos_y_media, pos_x_media

def generate_matrix(list_palabras):
    dim_y_matrix = 3 * len(list_palabras) + 50
    dim_x_matrix = 15 * len(list_palabras) + 500

    dim_y_matrix = DIM_Y_MATRIX
    dim_x_matrix = DIM_X_MATRIX
    matrix_dim = [[] for i in range(DIM_Y_MATRIX)]
    for y in range(dim_y_matrix):
        matrix_dim[y] += [0 for x in range(dim_x_matrix)]
    # logger.info(matrix_dim)
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix_dim)
    return matrix_dim, pos_y_media, pos_x_media


def imprimir_matriz(matriz):


    try:
        if not PRINT_MATRIX:
            return
        pos_y_media, pos_x_media = get_pos_media_matrix(matriz)
        matriz = matriz.copy()
        matriz = reducir_tam_matriz(matriz)
        ################################################################################################################
        ################################################################################################################
        ################################################################################################################
        # Imprimir numeros
        # De esta forma saco la posicion de la primera palabra que encuentre y voy imprimiendo todas las posiciones
        # del resto
        id_tmp = -1
        fila = 0
        col = 0
        while fila < len(matriz):
            while col < len(matriz[0]):
                if matriz[fila][col] != 0:
                    id_tmp = matriz[fila][col]
                    break
                col += 1
            if id_tmp != -1:
                break
            fila += 1
        if id_tmp == -1:
            return

        pos_x = Palabra.palabras_dict_id.get(id_tmp).pos_x
        pos_y = Palabra.palabras_dict_id.get(id_tmp).pos_y

        print("-----------------------------------------------------------------------")
        # Primero imprimo los numeros de la matriz de las columnas y luego los numeros de posiciones reales
        i = pos_x - col + pos_x_media
        print(f"          ", end="")
        for elemento in matriz[0]:
            print(f"{i:<4}", end="")
            i += 1
        print()

        i = pos_x - col
        print(f"          ", end="")
        for elemento in matriz[0]:
            print(f"{i:<4}", end="")
            i += 1
        print()
        print(f"          ", end="")
        for _ in matriz[0]:
            print(f"{'____'}", end="")
        print()
        ##############################

        j = pos_y - fila + len(matriz) -1
        j_bis = pos_y - fila + pos_y_media + len(matriz) -1

        for fila in matriz[::-1]:
            print(f"{j_bis:<5}", end="")
            print(f"{j:<4}", end="")
            print(f"{'|':<1}", end="")
            num_col = 0
            for elemento in fila:
                if elemento == 0:
                    print(f"{elemento:<4}", end="")
                else:
                    print(f"{elemento:<4}", end="")
                num_col += 1
            j -= 1
            j_bis -= 1
            print()
        print("-----------------------------------------------------------------------")
    except Exception as e:
        print(e)
        pass


def reducir_tam_matriz(matrix_dim):
    # Reducir Matriz
    matrix_dim = matrix_dim.copy()
    matrix_dim_copy = matrix_dim.copy()
    for x in matrix_dim_copy:
        if sum(x) == 0:
            matrix_dim.pop(0)
        else:
            break
    matrix_dim_reverse = matrix_dim.copy()
    matrix_dim_reverse.reverse()
    for x in matrix_dim_reverse:
        if sum(x) == 0:
            matrix_dim.pop()
        else:
            break
    matrix_dim_transpose = [list(fila) for fila in zip(*matrix_dim)]
    matrix_dim_transpose_copy = matrix_dim_transpose.copy()
    for x in matrix_dim_transpose_copy:
        if sum(x) == 0:
            matrix_dim_transpose.pop(0)
        else:
            break
    matrix_dim_transpose_reverse = matrix_dim_transpose.copy()
    matrix_dim_transpose_reverse.reverse()
    for x in matrix_dim_transpose_reverse:
        if sum(x) == 0:
            matrix_dim_transpose.pop()
        else:
            break
    matrix_dim = [list(fila) for fila in zip(*matrix_dim_transpose)]
    return matrix_dim



def ampliar_matriz(matrix_dim):
    AMPLIAR_X = 200
    AMPLIAR_Y = 50
    MARGEN_Y = 50
    MARGEN_X = 100
    logger.info("################## Ampliando matriz")
    # comprueba los bordes de la matriz y en caso de existir alguno con un valor != 0

    # amplia la matriz en 250 en x y en y
    dim_y_matrix = len(matrix_dim)
    dim_x_matrix = len(matrix_dim[0])
    matrix_dim_copy = matrix_dim.copy()

    conteo_arriba = 0
    sumar_arriba = False
    for x in matrix_dim_copy:
        if sum(x) == 0:
            conteo_arriba +=1
        else:
            sumar_arriba = True
            break
        if conteo_arriba > MARGEN_Y:
            break


    conteo_abajo = 0
    sumar_abajo = False
    # recorrer la matriz al reves
    for x in matrix_dim_copy[::-1]:
        if sum(x) == 0:
            conteo_abajo +=1
        else:
            sumar_abajo = True
            break
        if conteo_arriba > MARGEN_Y:
            break

    conteo_dcha = 0
    sumar_dcha = False
    # recorrer la matriz al reves
    for x in matrix_dim_copy[::-1]:
        if sum(x) == 0:
            conteo_abajo += 1
        else:
            sumar_abajo = True
            break
        if conteo_arriba > MARGEN_Y:
            break

    matrix_dim_transpose = [list(fila) for fila in zip(*matrix_dim)]
    matrix_dim_transpose_copy = matrix_dim_transpose.copy()
    conteo_dcha = 0
    sumar_dcha = False
    for x in matrix_dim_transpose_copy:
        if sum(x) == 0:
            conteo_dcha += 1
        else:
            sumar_dcha = True
            break
        if conteo_dcha > MARGEN_X:
            break

    conteo_izq = 0
    sumar_izq = False
    for x in matrix_dim_transpose_copy[::-1]:
        if sum(x) == 0:
            conteo_izq += 1
        else:
            sumar_izq = True
            break
        if conteo_izq > MARGEN_X:
            break

    # Se suman en ambos lados lo mismo y asi la posicion media sigue siendo el centro :)
    if sumar_arriba or sumar_abajo:
        logger.info("############# Sumando arriba")
        matrix_dim = [[0 for x in range(dim_x_matrix)] for y in range(AMPLIAR_Y)] + matrix_dim
    if sumar_abajo or sumar_arriba:
        logger.info("############# Sumando abajo")
        matrix_dim = matrix_dim + [[0 for x in range(dim_x_matrix)] for y in range(AMPLIAR_Y)]
    if sumar_dcha or sumar_izq:
        logger.info("############# Sumando dcha")
        matrix_dim = [x + [0 for x in range(AMPLIAR_X)] for x in matrix_dim]
    if sumar_izq or sumar_dcha:
        logger.info("############# Sumando izq")
        matrix_dim = [[0 for x in range(AMPLIAR_X)] + x for x in matrix_dim]
    return matrix_dim


MARGIN_RELATION_ARRIBA = 3
MARGIN_RELATION_DCHA = 3
MARGIN_RELATION_DCHA_ARRIBA = 3


def get_id_ocupando_relacion_matrix(matrix, y, x):
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix)
    x = x + pos_x_media
    y = y + pos_y_media




def is_empty_relation_in_matrix(matrix, y_dest, x_dest, relacion, in_draw=False):
    matrix = matrix.copy()
    if not in_draw and relacion.has_been_plotted:
       return True, matrix, None
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix)
    if in_draw:
        pal_origen = relacion.pal_origen
        pal_dest = relacion.pal_dest
        x_origen = relacion.x_origen_draw
        y_origen = relacion.y_origen_draw
        x_dest = relacion.x_dest_draw
        y_dest = relacion.y_dest_draw

        if x_origen is None or x_dest is None or y_origen is None or y_dest is None:
            x_origen = pal_origen.pos_x
            y_origen = pal_origen.pos_y
            x_dest = pal_dest.pos_x
            y_dest = pal_dest.pos_y

    else:
        pal_origen = relacion.pal_origen
        pal_dest = relacion.pal_dest
        x_origen = pal_origen.pos_x
        y_origen = pal_origen.pos_y
        y_dest = y_dest - pos_y_media
        x_dest = x_dest - pos_x_media
    id_orig = relacion.pal_origen.id
    id_dest = relacion.pal_dest.id

    if x_origen is None or x_dest is None or y_origen is None or y_dest is None:
        return True, matrix, None

    x_origen = int(x_origen + pos_x_media)
    y_origen = int(y_origen + pos_y_media)
    x_dest = int(x_dest + pos_x_media)
    y_dest = int(y_dest + pos_y_media)
    ids_to_skip = [id_orig, id_dest, relacion.id]
    try:
        if (x_dest - x_origen) == 0 and y_origen < y_dest:  # ARRIBA
            pos_y = y_origen + int(abs((y_dest-y_origen) / 2))
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, x_origen, MARGIN_RELATION_ARRIBA,
                                                   MARGIN_RELATION_ARRIBA, ampliar=False, ids_to_skip=ids_to_skip)
            return is_empty, matrix, id_conflict

        if (x_dest - x_origen) == 0 and y_origen > y_dest:  # ABAJO
            pos_y = y_dest + int(abs((y_origen - y_dest) / 2))
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, x_origen, MARGIN_RELATION_ARRIBA,
                                                   MARGIN_RELATION_ARRIBA, ampliar=False, ids_to_skip=ids_to_skip)
            return is_empty, matrix, id_conflict

        if (y_dest - y_origen) == 0 and x_origen < x_dest:  # DCHA
            pos_x = x_origen + int(abs((x_dest-x_origen) / 2))
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, y_origen, pos_x, MARGIN_RELATION_DCHA, MARGIN_RELATION_DCHA,
                                                   ampliar=False, ids_to_skip=ids_to_skip)
            return is_empty, matrix, id_conflict

        if (y_dest - y_origen) == 0 and x_origen > x_dest:  # IZQ
            pos_x = x_dest + int(abs((x_origen - x_dest) / 2))
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, y_origen, pos_x, MARGIN_RELATION_DCHA, MARGIN_RELATION_DCHA,
                                                   ampliar=False, ids_to_skip=ids_to_skip)
            return is_empty, matrix, id_conflict

        # DCHA_ARRIBA
        if x_origen < x_dest and y_origen < y_dest:
            pos_y = y_origen + int(abs((y_dest-y_origen) / 2))
            pos_x = x_origen + int(abs((x_dest-x_origen) / 2))
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, pos_x, MARGIN_RELATION_DCHA_ARRIBA,
                                                   MARGIN_RELATION_DCHA_ARRIBA, ampliar=False, ids_to_skip=ids_to_skip)
            return is_empty, matrix, id_conflict

        # IZQ_ARRIBA
        if x_origen > x_dest and y_origen < y_dest:
            pos_y = y_origen + int(abs((y_dest - y_origen) / 2))
            pos_x = x_dest + int(abs((x_origen - x_dest) / 2))
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, pos_x, MARGIN_RELATION_DCHA_ARRIBA,
                                                   MARGIN_RELATION_DCHA_ARRIBA, ampliar=False, ids_to_skip=ids_to_skip)
            return is_empty, matrix, id_conflict

        # IZQ_ABAJO
        if x_origen > x_dest and y_origen > y_dest:
            pos_y = y_dest + int(abs((y_origen - y_dest) / 2))
            pos_x = x_dest + int(abs((x_origen - x_dest) / 2))
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, pos_x, MARGIN_RELATION_DCHA_ARRIBA,
                                                   MARGIN_RELATION_DCHA_ARRIBA, ampliar=False, ids_to_skip=ids_to_skip)
            return is_empty, matrix, id_conflict

        # DCHA_ABAJO
        if x_origen < x_dest and y_origen > y_dest:
            pos_y = y_dest + int(abs((y_origen - y_dest) / 2))
            pos_x = x_origen + int(abs((x_dest - x_origen) / 2))
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, pos_x, MARGIN_RELATION_DCHA_ARRIBA,
                                                   MARGIN_RELATION_DCHA_ARRIBA, ampliar=False, ids_to_skip=ids_to_skip)
            return is_empty, matrix, id_conflict


    except:
        pass

    if in_draw:
        return False, matrix, None
    else:
        return True, matrix, None



def _is_elipse_relation(matrix, relacion):
    pos_y_media, pos_x_media = get_pos_media_matrix(matrix)
    pal_origen = relacion.pal_origen
    pal_dest = relacion.pal_dest
    x_origen = pal_origen.pos_x
    y_origen = pal_origen.pos_y
    x_dest = pal_dest.pos_x
    y_dest = pal_dest.pos_y

    if x_origen is None or x_dest is None or y_origen is None or y_dest is None:
        return True

    try:
        if (x_dest - x_origen) == 0:  # ARRIBA O ABAJO
            pos_y = min(y_origen, y_dest) + int((abs(y_origen) + abs(y_dest))/2)
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, x_origen, MARGIN_RELATION_ARRIBA,
                                                   MARGIN_RELATION_ARRIBA, ampliar=False)
            return is_empty

        if (y_dest - y_origen) == 0:  # DCHA O IZQ
            pos_x = min(x_origen, x_dest) + int((abs(x_origen) + abs(x_dest)) / 2)
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, y_origen, pos_x, MARGIN_RELATION_DCHA, MARGIN_RELATION_DCHA,
                                                   ampliar=False)
            return is_empty

        # DCHA_ARRIBA
        if x_origen < x_dest and y_origen < y_dest:
            pos_y = y_origen + int((abs(y_origen) + abs(y_dest)) / 2)
            pos_x = x_origen + int((abs(x_origen) + abs(x_dest)) / 2)
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, pos_x, MARGIN_RELATION_DCHA_ARRIBA,
                                                   MARGIN_RELATION_DCHA_ARRIBA, ampliar=False)
            return is_empty

        # IZQ_ARRIBA
        if x_origen > x_dest and y_origen < y_dest:
            pos_y = y_origen + int((abs(y_origen) + abs(y_dest)) / 2)
            pos_x = x_dest + int((abs(x_origen) + abs(x_dest)) / 2)
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, pos_x, MARGIN_RELATION_DCHA_ARRIBA,
                                                   MARGIN_RELATION_DCHA_ARRIBA, ampliar=False)
            return is_empty

        # IZQ_ABAJO
        if x_origen > x_dest and y_origen > y_dest:
            pos_y = y_dest + int((abs(y_origen) + abs(y_dest)) / 2)
            pos_x = x_dest + int((abs(x_origen) + abs(x_dest)) / 2)
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, pos_x, MARGIN_RELATION_DCHA_ARRIBA,
                                                   MARGIN_RELATION_DCHA_ARRIBA, ampliar=False)
            return is_empty

        # DCHA_ABAJO
        if x_origen < x_dest and y_origen > y_dest:
            pos_y = y_dest + int((abs(y_origen) + abs(y_dest)) / 2)
            pos_x = x_origen + int((abs(x_origen) + abs(x_dest)) / 2)
            is_empty, matrix, id_conflict = is_empty_pos_matrix(matrix, pos_y, pos_x, MARGIN_RELATION_DCHA_ARRIBA,
                                                   MARGIN_RELATION_DCHA_ARRIBA, ampliar=False)
            return is_empty

        return False
    except:
        return False



MARGIN_X_DCHA = 4
MARGIN_X_IZQ = 3
MARGIN_Y_ARRIBA = 2
MARGIN_Y_ABAJO = 2

def is_empty_pos_matrix(matrix, pos_y, pos_x, dim_y, dim_x, margen_x=0, ampliar=True, ids_to_skip= []):
    ids_to_skip.append(0)
    # Acuerdate que es la posicion centrada, es decir, da igual si es yendo a la izq o derecha o arriba o abajo
    try:
        dim_x_bis = dim_x
        pox_x_bis = pos_x
        if margen_x < 0:
            pox_x_bis = pos_x + margen_x  # asi empieza en una posicion anterior.
        elif margen_x > 0:
            dim_x_bis = dim_x + margen_x

        for axis_x_loop in range(pox_x_bis-MARGIN_X_IZQ, pos_x + dim_x_bis+MARGIN_X_DCHA):
            axis_x = axis_x_loop - dim_x // 2
            for axis_y_loop in range(pos_y-MARGIN_Y_ABAJO, pos_y + dim_y+MARGIN_Y_ARRIBA):
                axis_y = axis_y_loop - dim_y // 2
                if matrix[axis_y][axis_x] not in ids_to_skip:
                    return False, matrix, matrix[axis_y][axis_x] # id
        return True, matrix, 0
    except:
        if ampliar:
            matrix = ampliar_matriz(matrix)
            # Si se amplia la matriz, es que cabe seguro
            # return is_empty_pos_matrix(matrix, pos_y, pos_x, dim_y, dim_x, margen_x)
            return True, matrix, 0
        else:
            return False, matrix, 0


def find_better_center_position(matrix_dim, palabra, pos_y_media, pos_x_media):
    # TODO esta va a ser simple. Si el 0,0 esta ocupado, pones el -500, 0. Luego el -1000,0. Y asi sucesivamente,
    # haces una funcion de apliar matriz y ale. Y luego, reduces la matrix y las posiciones y ya está.

    pos_x = pos_x_media
    pos_y = pos_y_media
    # Lo que hace es recorrer de 200 en 200 los elementos.
    for pos_y in range(pos_y_media, -4000, -20):
        is_empty, matrix_dim, id_conflict = is_empty_pos_matrix(matrix_dim, pos_y, pos_x, dim_y=5, dim_x=10)
        if is_empty:
            return pos_y, pos_x, matrix_dim

    return pos_y_media, pos_x_media, matrix_dim
