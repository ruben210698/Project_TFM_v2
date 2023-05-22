TYPE_SINTAX_ACL = 'acl'
TYPE_SINTAX_ADVCL = 'advcl'
TYPE_SINTAX_ADVMOD = 'advmod'
TYPE_SINTAX_AMOD = 'amod'
TYPE_SINTAX_APPOS = 'appos'
TYPE_SINTAX_AUX = 'aux'
TYPE_SINTAX_CASE = 'case'
TYPE_SINTAX_CC = 'cc'
TYPE_SINTAX_CCOMP = 'ccomp'
TYPE_SINTAX_CONJ = 'conj'
TYPE_SINTAX_COP = 'cop'
TYPE_SINTAX_CSUBJ = 'csubj'
TYPE_SINTAX_CSUBJPASS = 'csubjpass'
TYPE_SINTAX_DATIVE = 'dative'
TYPE_SINTAX_DEP = 'dep'
TYPE_SINTAX_DET = 'det'
TYPE_SINTAX_DOBJ = 'dobj'
TYPE_SINTAX_OBJ = 'obj'
TYPE_SINTAX_IOBJ = 'iobj'
TYPE_SINTAX_OBL = 'obl' # Complemento Circunstancial

TYPE_SINTAX_EXPL = 'expl'
TYPE_SINTAX_INTJ = 'intj'
TYPE_SINTAX_MARK = 'mark'
TYPE_SINTAX_META = 'meta'
TYPE_SINTAX_NEG = 'neg'
TYPE_SINTAX_NOUN_CHUNK = 'noun_chunk'
TYPE_SINTAX_NPADVMOD = 'npadvmod'
TYPE_SINTAX_NSUBJ = 'nsubj'
TYPE_SINTAX_NSUBJPASS = 'nsubjpass'
TYPE_SINTAX_NUMMOD = 'nummod'
TYPE_SINTAX_OPRED = 'opred'
TYPE_SINTAX_PARATAXIS = 'parataxis'
TYPE_SINTAX_PCOMP = 'pcomp'
TYPE_SINTAX_POBJ = 'pobj'
TYPE_SINTAX_POSS = 'poss'
TYPE_SINTAX_PRECONJ = 'preconj'
TYPE_SINTAX_PREDET = 'predet'
TYPE_SINTAX_PREF = 'pref'
TYPE_SINTAX_PREP = 'prep'
TYPE_SINTAX_PRONL = 'pronl'
TYPE_SINTAX_PRT = 'prt'
TYPE_SINTAX_PUNCT = 'punct'
TYPE_SINTAX_QUANTMOD = 'quantmod'
TYPE_SINTAX_ROOT = 'ROOT'
TYPE_SINTAX_XCOMP = 'xcomp'
TYPE_SINTAX_NMOD = 'nmod'  # Nmod es una cualidad, modifica al sustantivo. No debe ir con ningun texto la flecha
TYPE_SINTAX_FLAT = 'flat'

# Patrones propios que yo le doy
TYPE_SINTAX_PATTERN_CCL = 'PAT_CCL'
TYPE_SINTAX_PATTERN_CCT = 'PAT_CCT'
LIST_SINTAX_PATTERN_MODIFY = [TYPE_SINTAX_MARK, TYPE_SINTAX_CONJ, TYPE_SINTAX_OBL, TYPE_SINTAX_ADVMOD]


compound = 'compound'

TYPE_SINTAX_PALABRA = [TYPE_SINTAX_FLAT, TYPE_SINTAX_NMOD]
LIST_TYPES_SINTAGMA_PREDOMINANTE = [TYPE_SINTAX_NSUBJ, TYPE_SINTAX_PATTERN_CCL, TYPE_SINTAX_PATTERN_CCT]
# CD, CI, CCL... son los que voy a poner de diferentes colores
LIST_TYPES_SINTAGMA_DESCARTAR = [TYPE_SINTAX_PUNCT, TYPE_SINTAX_PRT, TYPE_SINTAX_PREP, TYPE_SINTAX_PRECONJ, TYPE_SINTAX_DET]

LIST_SINTAX_TYPES_CD = [TYPE_SINTAX_DOBJ, TYPE_SINTAX_OBJ]
LIST_SINTAX_TYPES_CI = [TYPE_SINTAX_IOBJ]

LIST_SINTAX_ADVERBIOS = [TYPE_SINTAX_ADVCL]
LIST_SINTAX_TYPES_CCL = [TYPE_SINTAX_PATTERN_CCL]
LIST_SINTAX_TYPES_CCT = [TYPE_SINTAX_PATTERN_CCT]

LIST_SINTAX_TYPES_ROOT_VB_OK = [TYPE_SINTAX_PATTERN_CCL, TYPE_SINTAX_PATTERN_CCT, TYPE_SINTAX_NSUBJ]


"""
ACL: Cláusula adjetiva
ADVCL: Cláusula adverbial
ADVMOD: Modificador adverbial
AMOD: Modificador adjetival
APPOS: Sintagma nominal en aposición
AUX: Auxiliar
CASE: Marcador de caso
CC: Conjunción coordinada
CCOMP: Cláusula complementaria
CONJ: Conjunción
COP: Verbo copulativo
CSUBJ: Cláusula subordinada sujeto
CSUBJPASS: Cláusula subordinada sujeto pasiva
DATIVE: Complemento dativo
DEP: Elemento dependiente
DET: Determinante
DOBJ: Objeto directo
EXPL: Elemento explícito
INTJ: Interjección
MARK: Marcador
META: Elemento metalingüístico
NEG: Negación
NOUN_CHUNK: Sintagma nominal
NPADVMOD: Modificador adverbial de un sintagma nominal
NSUBJ: Sujeto nominal
NSUBJPASS: Sujeto nominal pasivo
NUMMOD: Modificador numérico
OPRED: Objeto predicativo
PARATAXIS: Parataxis
PCOMP: Complemento predicativo
POBJ: Objeto preposicional
POSS: Posesivo
PRECONJ: Conjunción previa
PREDET: Determinante previo
PREF: Prefijo
PREP: Preposición
PRONL: Pronombre relativo
PRT: Partícula
PUNCT: Signo de puntuación
QUANTMOD: Modificador cuantificador
ROOT: Raíz sintáctica
XCOMP: Complemento no marcado

"""