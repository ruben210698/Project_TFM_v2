class Grafo:
    id_actual = 0

    def __init__(self, palabra_new):
        self.palabras_list = []
        self.palabras_list_ordered_num_rel = []
        self.palabras_list_ordered_num_rel_pending = []
        self.has_been_plotted = False
        self.num_grados = 0

        self.id = self.generar_id()
        self.palabras_list.append(palabra_new)
        self.palabras_list_ordered_num_rel.append(palabra_new)
        self.palabras_list_ordered_num_rel_pending.append(palabra_new)
        self.palabras_list_ordered_num_rel.sort(key=lambda x: x.numero_grafos, reverse=True)
        self.palabras_list_ordered_num_rel_pending.sort(key=lambda x: x.numero_grafos, reverse=True)
        self.palabras_drawn = []

    def add_node(self, palabra):
        self.palabras_list.append(palabra)
        self.palabras_list_ordered_num_rel.append(palabra)
        self.palabras_list_ordered_num_rel_pending.append(palabra)
        self.palabras_list_ordered_num_rel.sort(key=lambda x: x.numero_grafos, reverse=True)
        self.palabras_list_ordered_num_rel_pending.sort(key=lambda x: x.numero_grafos, reverse=True)

    @classmethod
    def generar_id(cls, autoincremental=True):
        if autoincremental:
            cls.id_actual += 1
            return cls.id_actual

    def is_all_drawn(self):
        for palabra in self.palabras_list:
            if not palabra.has_been_plotted:
                return False
        return True

    def reordenar_pal_pending(self):
        # todos los elementos que no esten representados y que no tengan relaciones pendientes
        self.palabras_list_ordered_num_rel_pending = \
            [elem for elem in self.palabras_list_ordered_num_rel_pending
             if not elem.has_been_plotted or not elem.has_been_plotted_relations]
        self.palabras_list_ordered_num_rel_pending.sort(key=lambda x: x.numero_grafos, reverse=True)
