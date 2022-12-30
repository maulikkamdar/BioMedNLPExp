import pandas as pd
import networkx as nx
import argparse


class UMLSGraphCreator():
    def __init__(self, data_folder="tempdata/", model_type="model1"):
        self.umls_G = nx.DiGraph()
        self.data_folder = data_folder
        self.umls_reverse_lookup = {}
        self.model_type = model_type

    def main(self):
        self.populate_labels()
        self.populate_hierarchy_edges()
        # self.populate_relations_edges()

    def save_temp_files(self):
        print ('Size of the knowledge graph: Nodes -', len(self.umls_G.nodes()), ", Edges -", len(self.umls_G.edges()))
        print ('Saving temporary files ...')
        nx.write_gpickle(self.umls_G, self.data_folder +
                         self.model_type + "_umls_G.gpickle")

    def populate_labels(self):
        print ('Populating labels in the UMLS Knowledge Graph')
        umls_terms = pd.read_csv(
            self.data_folder + 'selected_vocab_terms.tsv', sep='\t')
        alternate_labels = pd.read_csv(
            self.data_folder + 'alternate_labels.tsv', sep='\t')

        print ("Read in", umls_terms.shape[0], "UMLS concept labels")

        # Model 1 does not create individual nodes for codes/concepts in terminologies
        if self.model_type == 'model1':
            for k in umls_terms.values.tolist():
                if not self.umls_G.has_node(k[0]):
                    self.umls_G.add_node(k[0], node_type='UMLS_CUI', vocabcodes=set([]),
                                         preflabels=set([]), altlabels=set([]))
                self.umls_G.nodes[k[0]]['vocabcodes'].add(k[3] + ": " + k[4])
                if k[1] == 'P':
                    self.umls_G.nodes[k[0]]['preflabels'].add(
                        str(k[5]).lower())
                if k[1] == 'S':
                    self.umls_G.nodes[k[0]]['altlabels'].add(str(k[5]).lower())
                if not k[2] in self.umls_reverse_lookup:
                    self.umls_reverse_lookup[k[2]] = []
                self.umls_reverse_lookup[k[2]].append(k[0])

            for k in alternate_labels.values.tolist():
                if self.umls_G.has_node(k[0]):
                    self.umls_G.nodes[k[0]]['altlabels'].add(str(k[2]).lower())

        # Model 2 creates individual nodes for codes/concepts in terminologies.
        # Labels are not associated to CUIs and alternate labels from non-included terminologies are not used
        else:
            for k in umls_terms.values.tolist():
                if not self.umls_G.has_node(k[0]):
                    self.umls_G.add_node(k[0], node_type='UMLS_CUI')
                if not self.umls_G.has_node(k[4]):
                    self.umls_G.add_node(k[4], node_type=k[3],
                                         preflabels=set([]), altlabels=set([]))
                self.umls_G.add_edge(k[4], k[0], edge_type='HAS_CUI')

                if k[1] == 'P':
                    self.umls_G.nodes[k[4]]['preflabels'].add(
                        str(k[5]).lower())
                if k[1] == 'S':
                    self.umls_G.nodes[k[4]]['altlabels'].add(str(k[5]).lower())
                if not k[2] in self.umls_reverse_lookup:
                    self.umls_reverse_lookup[k[2]] = []
                self.umls_reverse_lookup[k[2]].append(k[4])

        print ('Labels populated in the UMLS Knowledge Graph')
        self.save_temp_files()
        print("--------------------")

    def populate_hierarchy_edges(self):
        print ('Populating hierarchical relations in the UMLS Knowledge Graph')
        umls_hierarchy = pd.read_csv(
            self.data_folder + 'hierarchies.tsv', sep="\t")
        ap = umls_hierarchy.drop_duplicates(['CUI', 'AUI', 'PAUI', 'SAB'])

        # Model 1 creates hierarchical edges between CUIs instead of terminology codes
        # Model 2 creates hierarchical edges between terminology codes
        for k in ap.values.tolist():
            cids = self.umls_reverse_lookup[k[1]
                                            ] if k[1] in self.umls_reverse_lookup else []
            pids = self.umls_reverse_lookup[k[2]
                                            ] if k[2] in self.umls_reverse_lookup else []
            for m in cids:
                for n in pids:
                    if not self.umls_G.has_edge(m, n):
                        if self.model_type == 'model1':
                            self.umls_G.add_edge(
                                m, n, edge_type="IS_SUBCLASS_OF", vocab=set([]))
                        else:
                            self.umls_G.add_edge(
                                m, n, edge_type="IS_SUBCLASS_OF")
                    if self.model_type == 'model1':
                        self.umls_G[m][n]['vocab'].add(k[3])

        print ('Hierarchical relations populated in the UMLS Knowledge Graph')
        self.save_temp_files()
        print("--------------------")

    def populate_relations_edges(self):
        umls_relations = pd.read_csv(
            self.data_folder + 'relations_selected.tsv', sep="\t")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--datafolder', type=str, required=False,
                        help='Folder path to where the temporary input/output files are saved')
    parser.add_argument('--modeltype', type=str, required=False,
                        help='Representation model for the UMLS knowledge graph (See README for for more information)')
    args = parser.parse_args()

    data_folder = args.datafolder if args.datafolder and len(
        args.datafolder) > 0 else 'tempdata/'
    model_type = args.modeltype if args.modeltype and len(
        args.modeltype) > 0 else 'model1'
    umls_graph_creator = UMLSGraphCreator(
        data_folder=data_folder, model_type=model_type)
    umls_graph_creator.main()


if __name__ == "__main__":
    main()
