"""
Clase Palabra:
texto: Una cadena de caracteres que representan una palabra.
tipo: Una cadena de caracteres que indica el tipo de palabra (sustantivo, verbo, adjetivo, etc.).
syntactic_place: Una cadena de caracteres que indica la posición sintáctica de una palabra (sujeto, objeto directo, objeto indirecto, etc.).
relaciones: un diccionario que contiene palabras y tipos de relaciones relacionadas con la palabra actual (por ejemplo, si la palabra actual es un verbo, la palabra relacionada puede ser un sujeto directo y un objeto, con una etiqueta que indica cuál es cuál).
id: Un identificador numérico generado automáticamente para cada palabra.
Importancia: un valor numérico que indica la importancia de la palabra en el texto (por ejemplo, la cantidad de veces que aparece la palabra en el texto).

"""
import re
from constants.direcciones_relaciones import CENTRO

from constants.direcciones_relaciones import DIR_DCHA, DIR_DCHA_ABAJO, DIR_DCHA_ARRIBA, DIR_ABAJO, DIR_ARRIBA, \
    DIR_IZQ, DIR_IZQ_ARRIBA, DIR_IZQ_ABAJO, FIND_DIR_CENTRO, FIND_DIR_DCHA, FIND_DIR_DCHA_ABAJO, FIND_DIR_DCHA_ARRIBA, \
    FIND_DIR_ABAJO, FIND_DIR_ARRIBA, FIND_DIR_IZQ, FIND_DIR_IZQ_ARRIBA, FIND_DIR_IZQ_ABAJO, DICT_DIR_BY_ORIGEN, CENTRO
from constants.type_sintax import *
from constants.type_morfologico import *

from constants import colores_figura, colores_figura_letra, colores, figuras

"""
¿Por qué hay un id_actual que a veces es autoincremental y a veces no?
Pues porque hay palabras como verbos, adjetivos o sustantivos que se van a repetir en la oración pero
no son lo mismo.
Sin embargo, si hay palabras iguales como nombres propios, nombres de ciudades...
De esta forma, palabras que se repiten y no queremos que sean iguales en el grafo, serán autoimcrementales
y palabras que se repitan y queramos que se relacionen, se guardarán con el id como su hash y serán iguales.
"""

ancho_caracter = {
    "A": 6,
    "B": 7,
    "C": 6,
    "D": 7,
    "E": 6,
    "F": 5,
    "G": 7,
    "H": 7,
    "I": 3,
    "J": 4,
    "K": 7,
    "L": 6,
    "M": 8,
    "N": 7,
    "O": 7,
    "P": 6,
    "Q": 7,
    "R": 7,
    "S": 6,
    "T": 6,
    "U": 7,
    "V": 6,
    "W": 9,
    "X": 6,
    "Y": 6,
    "Z": 6,
    "a": 5,
    "b": 5,
    "c": 4,
    "d": 5,
    "e": 5,
    "f": 4,
    "g": 5,
    "h": 5,
    "i": 2,
    "j": 2,
    "k": 5,
    "l": 2,
    "m": 8,
    "n": 5,
    "o": 5,
    "p": 5,
    "q": 5,
    "r": 4,
    "s": 4,
    "t": 4,
    "u": 5,
    "v": 5,
    "w": 7,
    "x": 5,
    "y": 5,
    "z": 4,
}

class Palabra:
    id_actual = 9
    palabras_dict = {}
    palabras_dict_id = {}
    relaciones_dict_origen = {}
    relaciones_dict_destino = {}

    @staticmethod
    def constructor_alternativo(token_nlp):
        instancia = Palabra(texto=token_nlp.text,
                            tipo_morf=token_nlp.tipo_morfol,
                            lugar_sintactico=token_nlp.tipo_sintagma,
                            txt_lema=token_nlp.lema,
                            position_doc=token_nlp.position_doc,
                            num_oracion=token_nlp.num_oracion,
                            token_nlp=token_nlp,
                            token_tag=token_nlp.token_tag
                            )
        return instancia

    def __init__(self, texto, tipo_morf, lugar_sintactico, id=None, importancia=None, num_relaciones=0,
                 autoincremental=True, txt_lema=None, position_doc=9999, num_oracion=0, token_nlp=None,
                 token_tag=None):
        self.token_nlp = token_nlp
        self.texto = texto
        self.txt_lema = txt_lema if txt_lema is not None else self.limpiar_texto(texto)
        self.tipo_morf = tipo_morf
        self.lugar_sintactico = lugar_sintactico
        self.token_tag = token_tag
        self.id = id if id is not None else self.generar_id(texto, autoincremental)
        # A menor valor de imporancia, mayor importancia tiene. Valor max=1
        if importancia is None:
            self.importancia = 1000 + int(position_doc)
        else:
            self.importancia = importancia

        self.num_relaciones = num_relaciones

        self.dimension_x = self.get_dimension(texto)
        self.dimension_y = 1
        self.cte_sum_x = 1
        if self.dimension_x < 4 and self.cte_sum_x < 2:
            self.cte_sum_x += 1
        self.cte_sum_y = 1

        self.has_been_plotted = False
        self.has_been_plotted_relations = False
        self.position_doc = position_doc
        self.num_oracion = num_oracion
        self.tipo_figura = None
        self.tam_eje_x_figura = self.dimension_x
        self.tam_eje_y_figura = self.dimension_y
        self.pos_x = None
        self.pos_y = None
        self.color_figura = colores.default

        self.list_texto_enumeracion = []
        self.is_enumeracion = False

        self.grafo = None
        self.numero_grafos = -1
        self.grafos_aproximados = []
        self.direccion_origen_tmp = CENTRO
        self.direccion_origen_final = CENTRO
        self.lista_direcciones_orden = []
        self.list_palabras_relacionadas_1er_grado = []
        self.list_palabras_relacionadas_2o_grado = []
        self.list_palabras_relacionadas_dest_1er_grado = []
        self.list_palabras_relacionadas_dest_2o_grado = []
        self.list_all_pal_subgrafo = []

        self.subgrafo_completado = False
        self.pal_raiz = None  # es la palabra de la que ha venido la relacion que ha formado este subgrafo.
        self.relations_pending = []
        self.relations_origen_and_dest = []
        self.palabras_relaciones_proximas = []
        self.dict_posiciones = {
            DIR_DCHA: None,
            DIR_DCHA_ARRIBA: None,
            DIR_DCHA_ABAJO: None,
            DIR_IZQ: None,
            DIR_IZQ_ARRIBA: None,
            DIR_IZQ_ABAJO: None,
            DIR_ARRIBA: None,
            DIR_ABAJO: None
        }

        self.determinantes_text = {}
        self.text_original = texto


        Palabra.palabras_dict[self.txt_lema + "-" + str(self.position_doc)] = self
        Palabra.relaciones_dict_origen[self] = []
        Palabra.relaciones_dict_destino[self] = []
        Palabra.palabras_dict_id[self.id] = self

        self.aciones_especificas_tipo_palabra()



    def aciones_especificas_tipo_palabra(self):
        if self.lugar_sintactico == TYPE_SINTAX_NSUBJ:
            self.importancia = 1
            self.color_figura = colores_figura.COLOR_SINTAX_NSUBJ
            self.tipo_figura = figuras.FIGURA_RECTANGULO
        elif self.lugar_sintactico == TYPE_SINTAX_ROOT:
            self.importancia = 2
            self.color_figura = colores_figura.COLOR_SINTAX_ROOT
            self.tipo_figura = figuras.FIGURA_CIRCULO

        elif self.tipo_morf == TYPE_MORF_VERB:
            self.color_figura = colores_figura.COLOR_MORF_VERB
            self.tipo_figura = figuras.FIGURA_ELIPSE
        elif self.tipo_morf == TYPE_SINTAX_PATTERN_CCL:
            self.color_figura = colores_figura.COLOR_SINTAX_CCL
            self.tipo_figura = figuras.FIGURA_RECTANGULO
        elif self.tipo_morf == TYPE_SINTAX_PATTERN_CCT:
            self.color_figura = colores_figura.COLOR_SINTAX_CCT
            self.tipo_figura = figuras.FIGURA_RECTANGULO
        else:
            self.color_figura = colores_figura.DEFAULT
            self.tipo_figura = figuras.FIGURA_RECTANGULO




    # get palabra by lema si existe
    @classmethod
    def get_palabra_by_lema(cls, txt_lema, position_doc):
        if Palabra.palabras_dict.get(txt_lema, None) is not None and \
                Palabra.palabras_dict[txt_lema].position_doc == position_doc:
            return Palabra.palabras_dict[txt_lema]
        else:
            return None

    @classmethod
    def generar_id(cls, texto, autoincremental=True):
        if autoincremental:
            cls.id_actual += 1
            return cls.id_actual
        else:
            texto_limpio = cls.limpiar_texto(texto)
            return hash(texto_limpio)

    @classmethod
    def reordenar_importancia_list(cls, lista):
        return sorted(lista, key=lambda x: x.importancia, reverse=False)

    @staticmethod
    def limpiar_texto(texto):
        texto_limpio = texto.lower()
        texto_limpio = re.sub(r'\W+', '', texto_limpio)
        return texto_limpio

    @staticmethod
    def get_dimension(texto):
        # Método que calcula la dimensión dependiendo del tamaño de la palabra
        len_txt = sum(ancho_caracter.get(c, 8) for c in texto) // 12
        return len_txt
        #return len(texto) - len(texto) // 4

    def __str__(self):
        return self.texto

    def change_lema(self, new_txt_lema):
        del Palabra.palabras_dict[self.txt_lema + "-" + str(self.position_doc)]
        self.txt_lema = new_txt_lema
        Palabra.palabras_dict[new_txt_lema + "-" + str(self.position_doc)] = self

    def delete_palabra(self):
        try:
            del Palabra.palabras_dict[self.txt_lema + "-" + str(self.position_doc)]
        except Exception as _:
            pass
        try:
            del Palabra.relaciones_dict_origen[self]
        except Exception as _:
            pass
        try:
            del Palabra.relaciones_dict_destino[self]
        except Exception as _:
            pass

    @staticmethod
    def refresh_dict_palabras():
        # eliminar duplicados y relaciones de palabras que no tengan posicion
        for key in Palabra.relaciones_dict_destino.keys():
            values = Palabra.relaciones_dict_destino[key].copy()
            for rel in values:
                if rel.position_doc == '':
                    rel.delete_relation()

    def append_enumeracion(self, new_texto):
        # FIXME de momento esto esta parado
        if not self.is_enumeracion:
            self.list_texto_enumeracion.append(self.texto)
        self.list_texto_enumeracion.append(new_texto)
        self.is_enumeracion = True
        # FIXME
        # self.dimension_y = len(self.list_texto_enumeracion) * 3 + 2
        self.dimension_y = 1
        self.tam_eje_y_figura = 1

    @staticmethod
    def _get_dim_relation_tree(relation):
        try:
            return relation.pal_dest.grafos_aproximados[0]  # cogemos el grafo mayor, que es la 1a posicion
        except Exception as _:
            return 0

    @staticmethod
    def refresh_relaciones_dict(list_relaciones):
        for key in Palabra.relaciones_dict_origen.keys():
            relaciones_dict_origen = Palabra.relaciones_dict_origen[key].copy()
            for rel in relaciones_dict_origen:
                if rel not in list_relaciones:
                    rel.delete_relation()

    def refresh_grafos_aproximados(self):
        try:
            self.grafos_aproximados = []
            lista_relaciones_directas = Palabra.relaciones_dict_origen[self]
            self.numero_grafos = len(lista_relaciones_directas)
            for rel in lista_relaciones_directas:
                self.grafos_aproximados.append(self._get_dim_relation_tree(rel) + 1)  # +1 porque es la relacion actual
            # ordenar de mayor a menor
            self.grafos_aproximados = sorted(self.grafos_aproximados, key=lambda x: x, reverse=True)
        except Exception as _:
            pass

    def refresh_relaciones_proximas_2o_grado(self):
        list_pal_to_check = [a for a in self.list_palabras_relacionadas_1er_grado if a != self]

        pal_to_check_2 = []
        self.palabras_relaciones_proximas = []

        for pal in list_pal_to_check:
            list_to_check = [a for a in pal.list_palabras_relacionadas_dest_2o_grado if a != self and a != pal] + \
                            [a for a in pal.list_palabras_relacionadas_1er_grado if a != self and a != pal]
            for pal2 in list_to_check:
                if pal2 in list_pal_to_check and pal2 not in pal_to_check_2:
                    pal_to_check_2.append(pal2)
        # que cree listas diferentes para los elementos que estan relacionados entre si:

        pal_to_check_2_copy = pal_to_check_2.copy()
        new_rel_origin = []
        while pal_to_check_2 != []:
            pal = pal_to_check_2.pop(0)
            new_rel = []
            for pal2 in [a for a in pal.list_palabras_relacionadas_1er_grado if a != self and a != pal]:
                if pal2 in pal_to_check_2_copy and pal2 not in new_rel:
                    new_rel.append(pal2)
            if new_rel == []:
                pass
                # new_rel_origin.append(pal)
            else:
                new_rel.append(pal)
                self.palabras_relaciones_proximas.append(new_rel)

        # aqui tengo que quitar todos los duplicados y todas las que son de 2 pero hay otra lista mayor de 3 con lo mismo
        # FIXME: quito esta parte, no quiero que se quiten los duplicados, asi lo haré mejor.
        # if len(self.palabras_relaciones_proximas)>=2:
        #     i = 1
        #     new_palabras_relaciones_proximas = self.palabras_relaciones_proximas.copy()
        #     for elem in self.palabras_relaciones_proximas:
        #         for elem2 in self.palabras_relaciones_proximas[i:]:
        #             same_elem = False
        #             if len(elem) == len(elem2):
        #                 # toda palabra dentro de elem esta en elem2
        #                 # [True for pal1 in elem if pal1 in elem2 else False]
        #                 same_elem = all([True if pal1 in elem2 else False for pal1 in elem])
        #                 same_elem = same_elem and all([True if pal2 in elem else False for pal2 in elem2])
        #                 if same_elem and elem2 in new_palabras_relaciones_proximas:
        #                     new_palabras_relaciones_proximas.remove(elem2)
        #             if len(elem) > len(elem2):
        #                 same_elem = all([True if pal2 in elem else False for pal2 in elem2])
        #                 if same_elem and elem2 in new_palabras_relaciones_proximas:
        #                     new_palabras_relaciones_proximas.remove(elem2)
        #         i += 1
        #     self.palabras_relaciones_proximas = new_palabras_relaciones_proximas
        # if len(self.palabras_relaciones_proximas) >= 2:
        #     i = 1
        #     new_palabras_relaciones_proximas = self.palabras_relaciones_proximas.copy()
        #     #recorrer la lista al reves:
        #     for elem in self.palabras_relaciones_proximas[::-1]:
        #         list_reverse = self.palabras_relaciones_proximas[::-1]
        #         for elem2 in list_reverse[i:]:
        #             same_elem = False
        #             if len(elem) == len(elem2):
        #                 # toda palabra dentro de elem esta en elem2
        #                 same_elem = all([True if pal1 in elem2 else False for pal1 in elem])
        #                 same_elem = same_elem and all([True if pal2 in elem else False for pal2 in elem2])
        #                 if same_elem and elem2 in new_palabras_relaciones_proximas:
        #                     new_palabras_relaciones_proximas.remove(elem2)
        #             if len(elem) > len(elem2):
        #                 same_elem = all([True if pal2 in elem else False for pal2 in elem2])
        #                 if same_elem and elem2 in new_palabras_relaciones_proximas:
        #                     new_palabras_relaciones_proximas.remove(elem2)
        #         i += 1
        #     self.palabras_relaciones_proximas = new_palabras_relaciones_proximas

        self.list_palabras_relacionadas_1er_grado = [pal for pal in self.list_palabras_relacionadas_1er_grado if
                                                     pal != self]
        self.list_palabras_relacionadas_1er_grado = list(set(self.list_palabras_relacionadas_1er_grado))
        self.list_palabras_relacionadas_2o_grado = [pal for pal in self.list_palabras_relacionadas_2o_grado if
                                                    pal != self]
        self.list_palabras_relacionadas_2o_grado = list(set(self.list_palabras_relacionadas_2o_grado))
        self.list_palabras_relacionadas_dest_1er_grado = [pal for pal in self.list_palabras_relacionadas_dest_1er_grado
                                                          if
                                                          pal != self]
        self.list_palabras_relacionadas_dest_1er_grado = list(set(self.list_palabras_relacionadas_dest_1er_grado))
        self.list_palabras_relacionadas_dest_2o_grado = [pal for pal in self.list_palabras_relacionadas_dest_2o_grado if
                                                         pal != self]
        self.list_palabras_relacionadas_dest_2o_grado = list(set(self.list_palabras_relacionadas_dest_2o_grado))
        self.list_all_pal_subgrafo += self.list_palabras_relacionadas_1er_grado
        self.list_all_pal_subgrafo = [pal for pal in list(set(self.list_all_pal_subgrafo)) if pal != self.pal_raiz]

    def refresh_palabras_relacionadas_2o_grado(self):
        try:
            list_pal_to_check = [a.pal_dest for a in self.relations_origen_and_dest if a != self] + \
                                [a.pal_origen for a in self.relations_origen_and_dest if a != self]
            if self in list_pal_to_check:
                list_pal_to_check.remove(self)
            self.list_palabras_relacionadas_1er_grado = list_pal_to_check.copy()
            self.list_palabras_relacionadas_2o_grado = list_pal_to_check.copy()
            for pal_2 in list_pal_to_check:
                list_pal_2 = [a.pal_dest for a in pal_2.relations_origen_and_dest] + \
                             [a.pal_origen for a in pal_2.relations_origen_and_dest]
                for pal_3 in list_pal_2:
                    if pal_3 not in self.list_palabras_relacionadas_2o_grado and pal_3 != self:
                        self.list_palabras_relacionadas_2o_grado.append(pal_3)
            if self in self.list_palabras_relacionadas_2o_grado:
                self.list_palabras_relacionadas_2o_grado.remove(self)
            if self in self.list_palabras_relacionadas_1er_grado:
                self.list_palabras_relacionadas_1er_grado.remove(self)
            self.list_palabras_relacionadas_1er_grado = [pal for pal in self.list_palabras_relacionadas_1er_grado if
                                                         pal != self]
        except Exception as _:
            pass

        try:
            list_pal_to_check = [a.pal_dest for a in Palabra.relaciones_dict_origen.get(self, []) if a != self]

            self.list_palabras_relacionadas_dest_1er_grado = list_pal_to_check.copy()
            self.list_palabras_relacionadas_dest_2o_grado = list_pal_to_check.copy()
            for pal_2 in list_pal_to_check:
                list_pal_2 = [a.pal_dest for a in Palabra.relaciones_dict_origen.get(pal_2, [])]
                for pal_3 in list_pal_2:
                    if pal_3 not in self.list_palabras_relacionadas_dest_2o_grado:
                        self.list_palabras_relacionadas_dest_2o_grado.append(pal_3)
            if self in self.list_palabras_relacionadas_dest_2o_grado:
                self.list_palabras_relacionadas_dest_2o_grado.remove(self)
            if self in self.list_palabras_relacionadas_dest_1er_grado:
                self.list_palabras_relacionadas_dest_1er_grado.remove(self)
        except Exception as _:
            pass
        self.list_palabras_relacionadas_1er_grado = [pal for pal in self.list_palabras_relacionadas_1er_grado if
                                                     pal != self]
        self.list_palabras_relacionadas_1er_grado = list(set(self.list_palabras_relacionadas_1er_grado))
        self.list_palabras_relacionadas_2o_grado = [pal for pal in self.list_palabras_relacionadas_2o_grado if
                                                    pal != self]
        self.list_palabras_relacionadas_2o_grado = list(set(self.list_palabras_relacionadas_2o_grado))
        self.list_palabras_relacionadas_dest_1er_grado = [pal for pal in self.list_palabras_relacionadas_dest_1er_grado
                                                          if
                                                          pal != self]
        self.list_palabras_relacionadas_dest_1er_grado = list(set(self.list_palabras_relacionadas_dest_1er_grado))
        self.list_palabras_relacionadas_dest_2o_grado = [pal for pal in self.list_palabras_relacionadas_dest_2o_grado if
                                                         pal != self]
        self.list_palabras_relacionadas_dest_2o_grado = list(set(self.list_palabras_relacionadas_dest_2o_grado))
        self.list_all_pal_subgrafo += self.list_palabras_relacionadas_1er_grado
        self.list_all_pal_subgrafo = [pal for pal in list(set(self.list_all_pal_subgrafo)) if pal != self.pal_raiz]

    def refresh_pal_relations(self):
        try:
            list_relaciones_pal_origen = Palabra.relaciones_dict_origen.get(self, [])
            for rel in list_relaciones_pal_origen:
                rel.pal_tmp = rel.pal_dest
                rel.pal_tmp_opuesta = rel.pal_origen
            list_relaciones_pal_dest = Palabra.relaciones_dict_destino.get(self, [])
            for rel in list_relaciones_pal_dest:
                rel.pal_tmp = rel.pal_origen
                rel.pal_tmp_opuesta = rel.pal_dest
            list_relaciones_pal = list(set(list_relaciones_pal_origen + list_relaciones_pal_dest))
            # ordenar por el numero de grado de aproximacion
            list_relaciones_pal.sort(key=lambda x: x.pal_tmp.numero_grafos, reverse=True)
            self.relations_origen_and_dest = list_relaciones_pal
            self.relations_pending = list_relaciones_pal

        except Exception as _:
            self.relations_origen_and_dest = []
            self.relations_pending = []

    def refresh_list_all_pal_subgrafo(self):
        # self.list_all_pal_subgrafo = []
        list_palabras_dest = [pal.pal_dest for pal in Palabra.relaciones_dict_origen.get(self, [])]
        list_palabras_origen = [pal.pal_origen for pal in Palabra.relaciones_dict_destino.get(self, [])]
        list_all_pal_subgrafo = list_palabras_dest + list_palabras_origen
        # quitar la palabra self
        list_all_pal_subgrafo = [pal for pal in list(set(list_all_pal_subgrafo)) if pal != self]
        if self.pal_raiz is not None:
            list_all_pal_subgrafo = [pal for pal in list(set(list_all_pal_subgrafo)) if pal != self.pal_raiz]
        # un bucle en el que recorra todas las palabras y saque sus list_all_pal_subgrafo pero de forma recursiva
        for pal in list_all_pal_subgrafo:
            list_all_pal_subgrafo += pal.list_all_pal_subgrafo

    # Funcion recursiva que devuelve el subgrafo completo de una palabra
    def get_subgrafo_completo(self, pal_origen=None):
        # lo hace por medio de la lista list_palabras_relacionadas_1er_grado pero entrando en cada una de ellas
        # y sacando su lista de list_palabras_relacionadas_1er_grado
        # si la palabra ya esta en la lista no la añade

        # if self.list_palabras_relacionadas_dest_1er_grado == []:
        #     self.list_all_pal_subgrafo = []
        #     self.subgrafo_completado = True
        #     return []

        list_total_palabras = []
        list_palabras_relacionadas_1er_grado_copy = self.list_palabras_relacionadas_1er_grado.copy()
        if pal_origen is not None and pal_origen in list_palabras_relacionadas_1er_grado_copy:
            list_palabras_relacionadas_1er_grado_copy.remove(pal_origen)
        if self.pal_raiz is not None and self.pal_raiz in list_palabras_relacionadas_1er_grado_copy:
            list_palabras_relacionadas_1er_grado_copy.remove(self.pal_raiz)
        if self in list_palabras_relacionadas_1er_grado_copy:
            list_palabras_relacionadas_1er_grado_copy.remove(self)

        if list_palabras_relacionadas_1er_grado_copy == []:
            self.list_all_pal_subgrafo = []
            return []

        for pal in list_palabras_relacionadas_1er_grado_copy:
            self.list_all_pal_subgrafo.append(pal)
            list_total_palabras += [pal]
            list_total_palabras += pal.list_palabras_relacionadas_1er_grado

        if self.pal_raiz is not None and self.pal_raiz in list_total_palabras:
            list_total_palabras.remove(self.pal_raiz)
        if self in list_total_palabras:
            list_total_palabras.remove(self)
        if pal_origen is not None and pal_origen in list_total_palabras:
            list_total_palabras.remove(pal_origen)

        self.list_all_pal_subgrafo = list_total_palabras
        return list_total_palabras

    def refresh_subgrafo_completado(self):
        self.is_subgrafo_completado()

    def is_subgrafo_completado(self):
        list_all_pal_subgrafo = self.get_subgrafo_completo()

        for pal in list_all_pal_subgrafo:
            if not pal.has_been_plotted:
                self.subgrafo_completado = False
                return False
        if not self.has_been_plotted:
            self.subgrafo_completado = False
            return False
        self.subgrafo_completado = True
        return True

    def to_create_Palabra_str(self):
        return "list_palabras.append(Palabra('" + self.texto + "', '" + self.tipo_morf + "', '" + self.lugar_sintactico + "', " + str(
            self.id) + ", " + str(self.importancia) + ", " + str(
            self.num_relaciones) + ", False, '" + self.txt_lema + "', " + str(self.position_doc) + "))"



    def add_aux_text(self, new_det_text, position_new_text):
        from utils.utils_text import son_pal_rel_contiguas
        self.determinantes_text.update({new_det_text: position_new_text})
        # ordenar el diccionario por el valor de la posicion
        determinantes_text_copy = self.determinantes_text.copy()
        determinantes_text_copy.update({self.text_original: self.position_doc})
        determinantes_text_copy = dict(sorted(determinantes_text_copy.items(), key=lambda item: item[1]))
        det_prev = None
        pos_prev = None
        new_text = ''
        for det, pos in determinantes_text_copy.items():
            if det_prev is None:
                det_prev = det
                pos_prev = pos
                new_text = det
                continue
            if son_pal_rel_contiguas(text1=det_prev, pos1 = pos_prev, text2=det, pos2=pos):
                sep = ' '
            else:
                sep = ' / '

            # Esta ordenado de menor a mayor asi queno hay que preocuparse si es anterior o posterior
            new_text = new_text + sep + det
            det_prev = det
            pos_prev = pos

        self.texto = new_text
        self.dimension_x = self.get_dimension(self.texto)

        # Obtener la sintaxis predominante
        from utils.TokenNLP import TokenNLP
        new_token_added = TokenNLP.nlp_token_dict.get(position_new_text, None)
        if new_token_added is not None and new_token_added.is_root_sintagma and \
            new_token_added.tipo_sintagma in LIST_TYPES_SINTAGMA_PREDOMINANTE and \
            self.lugar_sintactico not in LIST_TYPES_SINTAGMA_PREDOMINANTE:
            self.lugar_sintactico = new_token_added.tipo_sintagma

