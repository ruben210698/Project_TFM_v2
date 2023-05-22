
import re

from utils.Palabra import Palabra
from constants.direcciones_relaciones import CENTRO
import matplotlib.pyplot as plt

from constants.type_sintax import *
from constants.type_morfologico import *



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


class Relacion:
    id_actual = -9
    relaciones_dict = {}
    relaciones_dict_id = {}
    # TODO que no coja el lugar sintactico de la relacion, sino que coja el lugar sintactico de la palabra 2

    def __init__(self, texto, pal_origen, pal_dest, position_doc=9999, lugar_sintactico="", importancia = None, id=None,
                 tipo_morf = None):
        self.delete = False
        self.texto = self.limpiar_texto(texto)
        self.texto_original = texto
        self.pal_origen = pal_origen
        self.pal_dest = pal_dest
        self.pal_tmp = None # esta es la palabra, u origen o destino, que queremos que lea
        # es decir, si buscamos la palabra de la que es origen nuestra relacion, la ponemos aqui y asi no tenemos
        # que estar comprobando si es la de origen o la de destino
        self.pal_tmp_opuesta = None
        self.lugar_sintactico = lugar_sintactico
        self.tam_text = self.get_tam_texto(texto)
        self.tam_text_real = self.get_tam_texto_real()
        self.cte_sum_x = 1
        self.cte_sum_y = 1
        self.id = id if id is not None else self.generar_id()
        self.importancia = importancia if importancia is not None else self.generar_importancia(pal_origen, pal_dest)
        self.position_doc = position_doc
        self.tipo_morf = tipo_morf
        self.direccion_actual = None
        self.has_been_plotted = False

        self.x_origen_draw = None
        self.y_origen_draw = None
        self.x_dest_draw = None
        self.y_dest_draw = None

        # TODO eliminar de todas partes, esto no sirve, puede estar super duplicado incluso con la pos en el docuemnto.
        Relacion.relaciones_dict[self.texto] = self # TODO añadir la posicion del documento

        Relacion.relaciones_dict_id[self.id] = self
        Palabra.relaciones_dict_origen[self.pal_origen].append(self)
        Palabra.relaciones_dict_origen[self.pal_origen] = \
            Palabra.reordenar_importancia_list(Palabra.relaciones_dict_origen[self.pal_origen])
        pal_origen.refresh_grafos_aproximados()
        if pal_dest is not None:
            Palabra.relaciones_dict_destino[self.pal_dest].append(self)
            pal_dest.refresh_grafos_aproximados()

        self.refresh_empty_text()

    def refresh_empty_text(self):
        if self.texto_original != "" or self.pal_dest is None or self.pal_origen is None:
            return
        #if self.pal_origen.lugar_sintactico == TYPE_SINTAX_ROOT:
        if self.pal_dest.lugar_sintactico in LIST_SINTAX_TYPES_CD:
            self.texto = self.limpiar_texto('¿qué?')
        elif self.pal_dest.lugar_sintactico in LIST_SINTAX_TYPES_CI:
            self.texto = self.limpiar_texto('¿a quien?')
        elif self.pal_dest.lugar_sintactico in LIST_SINTAX_TYPES_CCL:
            self.texto = self.limpiar_texto('¿dónde?')
        elif self.pal_dest.lugar_sintactico in LIST_SINTAX_TYPES_CCT:
            self.texto = self.limpiar_texto('¿cuando?')

    @classmethod
    def generar_id(cls):
        cls.id_actual -= 1
        return cls.id_actual

    @classmethod
    def generar_importancia(cls, relacion1, relacion2):
        if relacion2 is None:
            return 1000 + relacion1.importancia
        return relacion1.importancia + relacion2.importancia

    @staticmethod
    def limpiar_texto(texto):
        texto_limpio = texto.lower()
        #texto_limpio = re.sub(r'\W+', '', texto_limpio)
        return texto_limpio

    @staticmethod
    def get_tam_texto(texto):
        # Método que calcula la dimensión dependiendo del tamaño de la palabra
        return sum(ancho_caracter.get(c, 8) for c in texto) // 12
        #return len(texto) - len(texto) // 3 if len(texto) > 2 else 2
        #return len(texto)//2 if len(texto) > 2 else 2


    def get_tam_texto_real(self, ax = None):
        return self.get_tam_texto(self.texto)
        # if ax is None:
        #     return len(self.texto) / 3
        # else:
        #     texto = self.texto
        #     fontname = 'Times New Roman'
        #     fontsize = 15
        #     texto_obj = ax.text(0, 0, texto, fontname=fontname, fontsize=fontsize)
        #     bbox = texto_obj.get_window_extent()
        #     ancho = bbox.width / fontsize
        #     altura = bbox.height / fontsize
        #     return ancho + 1



    def add_rel_dest(self, palabra_dest):
        Palabra.relaciones_dict_destino[self.pal_dest].append(palabra_dest)
        self.pal_dest = palabra_dest
        self.importancia = \
            self.importancia if self.importancia != 99 else self.generar_importancia(self.pal_origen, self.pal_dest)
        palabra_dest.refresh_grafos_aproximados()

    def __str__(self):
        return self.texto

    def to_create_Relacion_str(self):
        if self.tipo_morf is not None:
            return "list_relaciones.append(Relacion('" + self.texto + "', " + f"Palabra.palabras_dict.get('{self.pal_origen.txt_lema}-{self.pal_origen.position_doc}') " + ", " +  f"Palabra.palabras_dict.get('{self.pal_dest.txt_lema}-{self.pal_dest.position_doc}')" + f", position_doc={self.position_doc} "+", lugar_sintactico='" + self.lugar_sintactico + f"', importancia = {self.importancia}" + ", id=" + str(self.id) + ", tipo_morf = '" + str(self.tipo_morf) + "'))"
        else:
            return "list_relaciones.append(Relacion('" + self.texto + "', " + f"Palabra.palabras_dict.get('{self.pal_origen.txt_lema}-{self.pal_origen.position_doc}') " + ", " +  f"Palabra.palabras_dict.get('{self.pal_dest.txt_lema}-{self.pal_dest.position_doc}')" + f", position_doc={self.position_doc} "+", lugar_sintactico='" + self.lugar_sintactico + f"', importancia = {self.importancia}" + ", id=" + str(self.id) + "))"
    def delete_relation(self):
        self.delete = True
        try:
            if Palabra.relaciones_dict_origen.get(self.pal_origen) is not None:
                Palabra.relaciones_dict_origen[self.pal_origen].remove(self)
        except Exception as _:
            pass
        try:
            if self.pal_dest is not None and Palabra.relaciones_dict_destino.get(self.pal_dest) is not None:
                Palabra.relaciones_dict_destino[self.pal_dest].remove(self)
        except Exception as _:
            pass
        try:
            if Relacion.relaciones_dict_id.get(self.id) is not None:
                del Relacion.relaciones_dict_id[self.id]
        except Exception as _:
            pass


    def change_pal_origen(self, pal_origen):
        Palabra.relaciones_dict_origen[self.pal_origen].remove(self)
        Palabra.relaciones_dict_origen[pal_origen].append(self)
        Palabra.relaciones_dict_origen[pal_origen] = \
            Palabra.reordenar_importancia_list(Palabra.relaciones_dict_origen[pal_origen])
        self.pal_origen = pal_origen
        pal_origen.refresh_grafos_aproximados()

    def change_pal_dest(self, pal_dest):
        Palabra.relaciones_dict_destino[self.pal_dest].remove(self)
        Palabra.relaciones_dict_destino[pal_dest].append(self)
        self.pal_dest = pal_dest
        pal_dest.refresh_grafos_aproximados()
