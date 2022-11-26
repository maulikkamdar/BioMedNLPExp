import pandas as pd
import argparse


class UMLSExtractor():

    def __init__(self, umls_folder="2022AA/META/", output_folder="output/", allowed_vocabs=["SNOMEDCT_US"]):
        self.umls_folder = umls_folder
        self.output_folder = output_folder
        self.allowed_vocabs = allowed_vocabs

    def extract_save_all(self):
        self.extract_umls_concepts()
        self.extract_alternate_labels()
        self.extract_semantic_types()
        self.extract_hierarchies()
        self.extract_relations()
        self.save_extracts()

    def extract_umls_concepts(self):
        print ("Extracting relevant UMLS concepts from the terminologies", self.allowed_vocabs)
        umls_concepts = pd.read_csv(self.umls_folder + 'MRCONSO.RRF', sep = "|", header=None, keep_default_na=False)
        umls_concepts.columns = ['CUI', 'LAT', 'TS', 'LUI', 'STT', 'SUI', 'ISPREF', 
                                 'AUI', 'SAUI', 'SCUI', 'SDUI', 'SAB', 
                                 'TTY', 'CODE', 'STR', 'SRL', 'SUPPRESS', 'CVF', '0']
        del umls_concepts['0']
        english_umls_terms = umls_concepts[umls_concepts['LAT'] == 'ENG']
        self.english_umls_terms = english_umls_terms[english_umls_terms['SUPPRESS'] == 'N']

        self.determine_relevant_vocabs()
        selected_vocab_terms = self.english_umls_terms[self.english_umls_terms['SAB'].apply(lambda x: x in self.allowed_vocabs)]
        self.selected_vocab_terms = selected_vocab_terms[['CUI', 'TS', 'AUI', 'SAB', 'CODE', 'STR']]
        self.cui_list = set(self.selected_vocab_terms['CUI'])
        print ("Relevant UMLS concepts in selected terminologies found:", self.selected_vocab_terms.shape[0])
        print ("--------------------")

    def determine_relevant_vocabs(self):
        print ("Determining relevant terminologies")
        unique_vocabs = set(self.english_umls_terms['SAB'])
        relevant_vocabs = set(self.allowed_vocabs).intersection(unique_vocabs)
        if len(relevant_vocabs) == 0:
            print ("No relevant terminologies found, reverting to SNOMEDCT_US")
            self.allowed_vocabs = ['SNOMEDCT_US']
        else:
            print ("Following relevant terminologies found:", list(relevant_vocabs))
            self.allowed_vocabs = list(relevant_vocabs)
        print ("--------------------")

    def extract_alternate_labels(self):
        print ("Extracting alternate labels")
        selected_cui_list_alt = self.english_umls_terms[self.english_umls_terms['CUI'].apply(lambda x: x in self.cui_list)]
        selected_cui_list_alt = selected_cui_list_alt[selected_cui_list_alt['SAB'].apply(lambda x: x not in self.allowed_vocabs)]
        selected_cui_list_alt = selected_cui_list_alt[['CUI', 'TS', 'STR']]
        self.alternate_labels = selected_cui_list_alt.drop_duplicates(['CUI', 'STR'])
        print ("Alternate labels in other terminologies found:", self.alternate_labels.shape[0])
        print ("--------------------")

    def extract_semantic_types(self):
        print ("Extracting semantic types")
        semantic_types = pd.read_csv(self.umls_folder + 'MRSTY.RRF', sep = "|", header=None, keep_default_na=False)
        semantic_types.columns = ['CUI', 'STY', 'TUI', 'STYNAME', 'ATUI', 'CVF', '0']
        semantic_types = semantic_types[['CUI', 'STY', 'STYNAME']]
        self.semantic_types = semantic_types[semantic_types['CUI'].apply(lambda x: x in self.cui_list)]
        print ("Semantic types found:", self.semantic_types.shape[0])
        print ("--------------------")

    def extract_hierarchies(self):
        print ("Extracting hierarchical relations")
        hierarchies = pd.read_csv(self.umls_folder + 'MRHIER.RRF', sep = "|", header=None, keep_default_na=False)
        hierarchies.columns = ['CUI', 'AUI', 'CXN', 'PAUI', 'SAB', 'RELA', 'PTR', 'HCD', 'CVF', '0']
        hierarchies = hierarchies[hierarchies['SAB'].apply(lambda x: x in self.allowed_vocabs)]
        self.hierarchies = hierarchies[['CUI', 'AUI', 'PAUI', 'SAB', 'RELA']]
        print ("Hierarchical relations found:", self.hierarchies.shape[0])
        print ("--------------------")

    def extract_relations(self):
        print ("Extracting associative relations")
        relations = pd.read_csv(self.umls_folder + 'MRREL.RRF', sep = "|", header=None, keep_default_na=False)
        relations = relations[relations[10].apply(lambda x: x in self.allowed_vocabs)]
        relations = relations[relations[7].apply(lambda x: len(str(x)) > 0)]
        relations = relations[[0,1,2,3,4,5,6,7,8,10,11]]
        relations.columns = ['CUI1', 'AUI1', 'STYPE1', 'REL', 'CUI2', 'AUI2', 'STYPE2', 'RELA', 'RUI', 'SAB', 'SL']
        self.relations = relations
        print ("Associative relations found:", self.relations.shape[0])
        print ("--------------------")

    def save_extracts(self):
        print ("Saving extracted files")
        self.selected_vocab_terms.to_csv(self.output_folder + 'selected_vocab_terms.tsv', sep="\t", index=None)
        self.alternate_labels.to_csv(self.output_folder + 'alternate_labels.tsv', sep="\t", index=None)
        self.semantic_types.to_csv(self.output_folder + 'semantic_types.tsv', sep="\t", index=None)
        self.hierarchies.to_csv(self.output_folder + 'hierarchies.tsv', sep="\t", index=None)
        self.relations.to_csv(self.output_folder + 'relations_selected.tsv', sep="\t", index=None)


parser = argparse.ArgumentParser()
parser.add_argument('--umlsfolder', type=str, required=True, help='Directory path where the UMLS Metathesaurus has been downloaded')
parser.add_argument('--outputfolder', type=str, required=True, help='Folder path to store the extracted files')
parser.add_argument('--terminologies', type=str, required=True, help='Comma-separated list of allowed terminologies (e.g., SNOMEDCT_US,ICD10CM)')
args = parser.parse_args()

umls_folder = args.umlsfolder if len(args.umlsfolder) > 0 else '2022AA/META/'
output_folder = args.outputfolder if len(args.outputfolder) > 0 else 'output/extract/'
allowed_vocabs = [k.strip().upper() for k in args.terminologies.split(",")] if len(args.terminologies) > 0 else ['SNOMEDCT_US']
umls_extractor = UMLSExtractor(umls_folder = umls_folder, output_folder = output_folder, allowed_vocabs = allowed_vocabs)
umls_extractor.extract_save_all()