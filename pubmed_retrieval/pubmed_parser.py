import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import os
import re
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from utilities import gtbtokenize
from utilities.utils import MatrixIO

TRUE_VALUES = set(["true", "on"])

def f(x):
    return re.sub(r'[^a-z]', " ", x)


def normalize(phrase):
    try:
        ap = f(gtbtokenize.tokenize(phrase).lower())
        ap = re.sub('\s+', ' ', ap).strip()
    except:
        ap = ""
    return ap

def str_to_bool(string):
    """ Takes a string and returns a boolean value interpreted
    from that string"""
    return str(string).strip().lower() in TRUE_VALUES

def parse_mesh(meshheading, is_qualifier=False):
    meshheading_name = meshheading.text
    meshheading_id = meshheading.attrib['UI']
    meshheading_topicm = meshheading.attrib['MajorTopicYN']
    qcode = 'Q' if is_qualifier else 'D'
    info = "|".join([qcode, meshheading_name, meshheading_id, meshheading_topicm])
    return info        


def parse(file_arg, include_mesh=True, include_abstract=True, verbose=False):
    print("-----------------------------")
    print("Parsing", file_arg, "with mesh", include_mesh, "and abstract", include_abstract)
    abstracts = {}
    tree = ET.parse(file_arg)
    root = tree.getroot()
    pubmed_articles = root.findall('PubmedArticle')
    print("Found abstracts", len(pubmed_articles))
    for act in pubmed_articles:
        try:
            cit = act.find('MedlineCitation')
            pmid = cit.find('PMID').text
            title = cit.find('Article').find('ArticleTitle').text
            if include_abstract:
                abstract = cit.find('Article').find(
                    'Abstract').find('AbstractText').text
            if include_mesh:
                mesh_list = cit.find('MeshHeadingList').findall('MeshHeading')
                mesh_formatted_list = []
                if verbose:
                    print("Mesh Headings found", len(mesh_list))
                for k in mesh_list:
                    mesh_fm = []
                    descriptors = k.findall('DescriptorName')
                    for descriptor in descriptors:
                        info = parse_mesh(descriptor)
                        mesh_fm.append(info)
                    qualifiers = k.findall('QualifierName')
                    for qualifier in qualifiers:
                        info = parse_mesh(qualifier, is_qualifier=True)
                        mesh_fm.append(info)
                    mesh_formatted_list.append("||".join(mesh_fm))
            if not pmid:
                continue
            if len(str(pmid)) > 0:
                abstracts[pmid] = {"title": title}
                if include_abstract:
                    abstracts[pmid]['abstract'] = abstract
                if include_mesh:
                    abstracts[pmid]['mesh'] = ":-:".join(mesh_formatted_list)
                if verbose: 
                    print("Parsed", pmid)
        except:
            if verbose:
                print('Parsing error')
            continue
    abstracts_df = pd.DataFrame.from_dict(abstracts, orient="index")
    abstracts_df = abstracts_df.reset_index()
    abstracts_df.to_csv(file_arg + ".tsv", sep="\t", index=None)
    print("Extracted abstracts", abstracts_df.shape[0])
    print("-----------------------------")


def save_file(tfdict, folder):
    mfio = MatrixIO()
    mfio.save_matrix(tfdict, folder + "word_freq.dict")
    tfdict_df = pd.DataFrame.from_dict(tfdict, orient="index")
    tfdict_df = tfdict_df.reset_index()
    tfdict_df.columns = ["word", "freq"]
    tfdict_df = tfdict_df.sort_values("freq", ascending=False)
    tfdict_df = tfdict_df[tfdict_df["freq"] >= 50]
    tfdict_df.to_csv(folder + "word_freq.tsv", sep="\t", index=None)


def get_freq_dict(folder):
    # This needs to be filled out for later in an automated run when dictionary exists in the folder
    return {}


def generate_dict(folder):
    tsv_files = [a for a in os.listdir(folder) if "pubmed" in a.lower()]
    tfdict = get_freq_dict(folder)
    tcount = 0
    print("-----------------------------")
    print("Found", len(tsv_files), "in", folder)
    for k in tsv_files:
        a = pd.read_csv(folder + k, sep="\t")
        print("Abstracts found", a.shape[0], "in", k)
        a = a.set_index("index").to_dict(orient="index")
        for pmid in a:
            text = "{} {}".format(
                normalize(a[pmid]["title"]), normalize(a[pmid]["abstract"]))
            text_parts = text.split()
            for d in text_parts:
                if not d in tfdict:
                    tfdict[d] = 0
                tfdict[d] += 1
        print("Words found so far", len(tfdict), ", Completed file", tcount)
        tcount += 1
        print("----------------------------")
        if tcount % 10 == 0:
            save_file(tfdict, folder)
    save_file(tfdict, folder)


def init_main(args):
    if args.mode == "parse":
        if not args.file:
            print("Please provide the XML file to parse as input")
            return None
        parse(args.file, include_abstract=str_to_bool(args.abstract), include_mesh=str_to_bool(args.mesh))
    elif args.mode == "generate":
        if not args.folder:
            print("Please provide the folder from which to generate the dictionary")
            return None
        generate_dict(args.folder)
    else:
        print("Please provide parse or generate mode")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        # don't want to reformat the description message, use file's doc_string
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__
    )
    parser.add_argument("--file", help="pubmed XML file")
    parser.add_argument("--mode", help="parse or generate")
    parser.add_argument("--mesh", help="include Mesh headers", default="true")
    parser.add_argument("--abstract", help="include Abstract", default="true")
    parser.add_argument(
        "--folder", help="If mode is generate, please provide the folder from which to generate dictionary")
    args = parser.parse_args()
    init_main(args)
