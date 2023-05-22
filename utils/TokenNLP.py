

from constants.type_morfologico import *
from constants.type_sintax import *

TYPE_RELACION = "RELACION"
TYPE_PALABRA = "PALABRA"
TYPE_PUNTUACION = "PUNTUACION"
TYPE_FLAT = "FLAT"



class TokenNLP:
    """
    ¿Por qué esto?
    Porque es necesario para el módulo de NLP. De esta forma al recorrer los tokens de un texto, se puede crear un objeto
    de esta clase y así poder trabajar con él.
    Con todos y cada uno de los tokens voy a ir creando esto y diciendo si es tipo RELACION o PALABRA, pero juntos
    Y para cada uno le voy a ir poniendo las relaciones que tiene y demás.
    Una vez tengo eso, luego recorro de nuevo el bucle y voy diciendo si es relacion o palabra, voy juntand relaciones,
    juntando palabras...
    Incluso eso lo haré en el módulo de web para reutilizar las funciones de unir palabras y relaciones.

    """

    """
    Ideas:
    1. al generar estos elementos, si una palabra tiene más de 8 hijos, se duplica ( ver cómo hacerlo, pero sería en 
    ese punto).
    2. Que me diga si la palabra es root del sintagma (si está relacionada con el ROOT de la frase). En caso de serlo,
    todas las palabras relacionadas con esa son del mismo sintagma (CD, CI...) y debo copiarlo a sus hijos.
    3. Buscar un ejemplo con comas y controlarlo, a ver cómo sale.
    
    
    """

    nlp_token_dict = {}
    def __init__(self, token_actual, num_oracion=0, token_padre = None, children = None):
        self.representado = False
        self.palabra_que_representa = None
        self.list_rel_que_representa = []

        self.token_original = token_actual
        self.token_original_padre = token_padre
        self.palabra_padre_final = None
        self.tokens_relacion_padre_final = []

        self.text = token_actual.text
        self.tipo_morfol = token_actual.pos_
        self.lugar_sintact_original = token_actual.dep_
        self.lema = token_actual.lemma_
        self.position_doc = token_actual.idx
        self.ent_type = token_actual.ent_type_ # TODO sacar algo de aqui
        #if token_actual.ent_type_ in ['LOC', 'LUG']:
        #    self.lugar_sintact_original = TYPE_SINTAX_PATTERN_CCL
        #elif token_actual.ent_type_ in ['TIME', 'DATE']:
        #    self.lugar_sintact_original = TYPE_SINTAX_PATTERN_CCT

        self.token_tag = token_actual.tag_

        self.num_oracion = num_oracion
        self.tipo_sintagma = None # el tipo del root sintagma
        self.is_root_sintagma = False # esto será True si el padre es ROOT

        TokenNLP.nlp_token_dict[self.position_doc] = self

        if (self.tipo_morfol not in LIST_TYPES_CONNECTOR_RELATION or self.lugar_sintact_original == TYPE_SINTAX_ROOT)\
            or (self.lugar_sintact_original in TYPE_SINTAX_PALABRA):
            self.tipo_palabra = TYPE_PALABRA
        elif self.tipo_morfol == TYPE_MORF_PUNCT:
            self.tipo_palabra = TYPE_PUNTUACION
        else:
            self.tipo_palabra = TYPE_RELACION

        ## Padre
        self.token_nlp_padre = None
        self._refresh_parent()


        # Hijos
        self.list_children_nlp = []
        for child in token_actual.children:
            if child.pos_ == TYPE_MORF_PUNCT:
                continue
            child_nlp = TokenNLP.nlp_token_dict.get(child.idx, child)
            self.list_children_nlp.append(child_nlp)


    def _refresh_parent(self):
        self.tipo_sintagma = None  # el tipo del root sintagma
        self.is_root_sintagma = False  # esto será True si el padre es ROOT
        if self.token_original_padre is not None:
            if self.token_nlp_padre is None:
                self.token_nlp_padre = TokenNLP.nlp_token_dict.get(self.token_original_padre.idx, None)

        if self.token_nlp_padre is not None:
            if self.token_nlp_padre.lugar_sintact_original == TYPE_SINTAX_ROOT:
                #self.is_root_sintagma = True
                self.tipo_sintagma = self.lugar_sintact_original  # si es root sintagma, el tipo sintagma es el actual
                if self.lugar_sintact_original in LIST_TYPES_SINTAGMA_PREDOMINANTE:
                    self.is_root_sintagma = True
            elif self.token_nlp_padre.tipo_sintagma in LIST_TYPES_SINTAGMA_DESCARTAR:
                # Si el padre es, por ejemplo, det, no me interesa
                self.tipo_sintagma = self.lugar_sintact_original
            # Hay sintagmas que predominan sobre otros. Si tiene uno de estos, es que si es root
            elif self.lugar_sintact_original in LIST_TYPES_SINTAGMA_PREDOMINANTE and \
                    self.tipo_sintagma != self.lugar_sintact_original:
                self.is_root_sintagma = True
                self.tipo_sintagma = self.lugar_sintact_original

            elif self.token_nlp_padre.is_root_sintagma:  # si no es root sintagma, el tipo sintagma es el del padre
                self.tipo_sintagma = self.token_nlp_padre.tipo_sintagma

            else: # Si el padre no es root sintagma y el actual tampoco, es que el padre del padre es root sintagma,
                # tambien coge lo del padre, aunque esto igual hay que revisarlo
                self.tipo_sintagma = self.token_nlp_padre.tipo_sintagma




        if self.tipo_sintagma is None:
            self.tipo_sintagma = self.lugar_sintact_original



    def refresh_parents_children(self):
        # Si self.token_nlp_padre no es del tipo TokenNLP
        # Es decir, si en el momento en que se guardó se hizo con el token inicial y no con el objeto TokenNLP
        self._refresh_parent()

        # Hijos
        list_children_nlp_old = self.list_children_nlp.copy()
        list_children_nlp_new = []
        for child_nlp in list_children_nlp_old:
            if child_nlp is not None and not isinstance(child_nlp, TokenNLP):
                # sustituyo el elemento child_nlp de la lista self.list_children_nlp por el nuevo
                child_nlp_2 = TokenNLP.nlp_token_dict.get(child_nlp.idx, None)
                list_children_nlp_new.append(child_nlp_2)
            else:
                list_children_nlp_new.append(child_nlp)

        self.list_children_nlp = list_children_nlp_new

    def __str__(self):
        return self.text