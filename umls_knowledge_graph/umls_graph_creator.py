import pandas as pd
import networkx as nx

class UMLSGraphCreator():
    def __init__(self, data_folder = "tempdata/", model_type = "model1"):
        self.umls_G = nx.DiGraph()
        self.data_folder = data_folder
        self.umls_reverse_lookup = {}

    def populate_labels(self):
        umls_terms = pd.read_csv(self.data_folder + 'selected_vocab_terms.tsv', sep='\t')
        alternate_labels = pd.read_csv(self.data_folder + 'alternate_labels.tsv', sep='\t')
        for k in umls_terms.values.tolist():
            if not umls_G.has_node(k[0]):
                self.umls_G.add_node(k[0], vocabcodes = set([]), preflabels = set([]), altlabels = set([]))
            self.umls_G.nodes[k[0]]['vocabcodes'].add(k[3] + ": " + k[4])
            if k[1] == 'P':
                self.umls_G.nodes[k[0]]['preflabels'].add(str(k[5]).lower())
            if k[1] == 'S':
                self.umls_G.nodes[k[0]]['altlabels'].add(str(k[5]).lower())
            if not k[2] in umls_reverse_lookup:
                self.umls_reverse_lookup[k[2]] = []
            self.umls_reverse_lookup[k[2]].append(k[0])

        for k in alternate_labels.values.tolist():
            if umls_G.has_node(k[0]):
                self.umls_G.nodes[k[0]]['altlabels'].add(str(k[2]).lower())

    def populate_hierarchy_edges(self):
        umls_hierarchy = pd.read_csv(self.data_folder + 'hierarchies.tsv', sep="\t")
        ap = umls_hierarchy.drop_duplicates(['CUI', 'AUI', 'PAUI', 'SAB'])
        for k in ap.values.tolist():
            cuis = self.umls_reverse_lookup[k[1]] if k[1] in self.umls_reverse_lookup else []
            pcuis = self.umls_reverse_lookup[k[2]] if k[2] in self.umls_reverse_lookup else []
            for m in cuis:
                for n in pcuis:
                    if not self.umls_G.has_edge(m, n):
                        self.umls_G.add_edge(m, n, edge_type = "IS_SUBCLASS_OF", vocab = set([]))
                    self.umls_G[m][n]['vocab'].add(k[3])

    def populate_relations_edges(self):
        umls_relations = pd.read_csv(self.data_folder + 'relations_selected.tsv', sep="\t")
