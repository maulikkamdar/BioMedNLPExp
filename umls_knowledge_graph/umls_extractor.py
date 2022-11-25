import pandas as pd
import re
import pickle
import urllib
import json
import argparse

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from utilities import gtbtokenize
from utilities.utils import MatrixIO


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
        umls_concepts = pd.read_csv(self.umls_folder + 'MRCONSO.RRF', sep = "|", header=None, keep_default_na=False)
        umls_concepts.columns = ['CUI', 'LAT', 'TS', 'LUI', 'STT', 'SUI', 'ISPREF', 
                                 'AUI', 'SAUI', 'SCUI', 'SDUI', 'SAB', 
                                 'TTY', 'CODE', 'STR', 'SRL', 'SUPPRESS', 'CVF', '0']
        del umls_concepts['0']
        english_umls_terms = umls_concepts[umls_concepts['LAT'] == 'ENG']
        self.english_umls_terms = english_umls_terms[english_umls_terms['SUPPRESS'] == 'N']
        selected_vocab_terms = self.english_umls_terms[self.english_umls_terms['SAB'].apply(lambda x: x in self.allowed_vocabs)]
        self.selected_vocab_terms = selected_vocab_terms[['CUI', 'TS', 'AUI', 'SAB', 'CODE', 'STR']] 

    def extract_alternate_labels(self):
        self.cui_list = set(self.selected_vocab_terms['CUI'])
        selected_cui_list_alt = self.english_umls_terms[self.english_umls_terms['CUI'].apply(lambda x: x in cui_list)]
        selected_cui_list_alt = selected_cui_list_alt[selected_cui_list_alt['SAB'].apply(lambda x: x not in self.allowed_vocabs)]
        selected_cui_list_alt = selected_cui_list_alt[['CUI', 'TS', 'STR']]
        self.selected_cui_list_alt = selected_cui_list_alt.drop_duplicates(['CUI', 'STR'])

    def extract_semantic_types(self):
        semantic_types = pd.read_csv(self.umls_folder + 'MRSTY.RRF', sep = "|", header=None, keep_default_na=False)
        semantic_types.columns = ['CUI', 'STY', 'TUI', 'STYNAME', 'ATUI', 'CVF', '0']
        semantic_types = semantic_types[['CUI', 'STY', 'STYNAME']]
        self.selected_cui_list_types = semantic_types[semantic_types['CUI'].apply(lambda x: x in self.cui_list)]

    def extract_hierarchies(self):
        hierarchies = pd.read_csv(self.umls_folder + 'MRHIER.RRF', sep = "|", header=None, keep_default_na=False)
        hierarchies.columns = ['CUI', 'AUI', 'CXN', 'PAUI', 'SAB', 'RELA', 'PTR', 'HCD', 'CVF', '0']
        hierarchies = hierarchies[hierarchies['SAB'].apply(lambda x: x in self.allowed_vocabs)]
        self.hierarchies = hierarchies[['CUI', 'AUI', 'PAUI', 'SAB', 'RELA']]

    def extract_relations(self):
        relations = pd.read_csv(self.umls_folder + 'MRREL.RRF', sep = "|", header=None, keep_default_na=False)
        relations = relations[relations[10].apply(lambda x: x in self.allowed_vocabs)]
        relations = relations[relations[7].apply(lambda x: len(str(x)) > 0)]
        self.relations = relations_sel[[0,1,2,3,4,5,6,7,8,10,11]]

    def save_extracts(self):
        self.selected_vocab_terms.to_csv('selected_vocab_terms.tsv', sep="\t", index=None)
        self.selected_cui_list_alt.to_csv('alternate_labels.tsv', sep="\t", index=None)
        self.selected_cui_list_types.to_csv('semantic_types.tsv', sep="\t", index=None)
        self.hierarchies.to_csv('hierarchies.tsv', sep="\t", index=None)
        self.relations.to_csv('relations_selected.tsv', sep="\t", index=None)


parser = argparse.ArgumentParser()
parser.add_argument('--umlsfolder', type=str, required=True, help='Directory path where the UMLS Metathesaurus has been downloaded')
parser.add_argument('--outputfolder', type=str, required=True, help='Folder path to store the extracted files')
parser.add_argument('--vocabs', type=str, required=True, help='Comma-separated list of allowed vocabularies (e.g., SNOMEDCT_US,ICD10CM')
args = parser.parse_args()

umls_folder = args.umlsfolder if len(args.umlsfolder) > 0 else '2022AA/META/'
output_folder = args.outputfolder if len(args.outputfolder) > 0 else 'output/extract/'
#allowed_vocabs = ['SNOMEDCT_US', 'ICD10CM', 'ICD10PCS', 'CPT', 'LNC', 'RXNORM']
allowed_vocabs = [k.strip() for k in args.vocabs.split(",")] if len(args.vocabs) > 0 else ['SNOMEDCT_US']
umls_extractor = UMLSExtractor(umls_folder = umls_folder, output_folder = output_folder, allowed_vocabs = allowed_vocabs)
umls_extractor.extract_save_all()