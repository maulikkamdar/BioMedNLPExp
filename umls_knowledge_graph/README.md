## Generate a Knowledge Graph of concepts and relations using UMLS MetaThesaurus

---

This folder contains Python scripts to generate a knowledge graph of biomedical concepts and relations using specific terminologies and taxonomies in the UMLS MetaThesaurus. 

**Note:** No UMLS data or any underlying terminologies are shared through this Github repository. The repository only contains scripts that enable you to convert the different UMLS metathesaurus files into a unified NetworkX GPickle data representation, that can be used for other purposes (tagging, concept similarities, etc.). Please ensure that you adhere to the correct license terms of UMLS and underlying terminologies when sharing and reusing the original data and the transformed data representations.

To generate the unified NetworkX GPickle representation, follow the steps outlined below:
- Download the UMLS Metathesaurus Full Subset from the [NIH-NLM website](https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html), after signing in using a specific identity provider and accepting the license terms.

- Save and unzing the downloaded UMLS Metathesaurus Zipped file, and note the folder path (referred henceforth as `UMLS_RAW_FOLDER`). *Ensure that this folder path is included in the .gitignore or resides outside of the Github repository to not accidentally commit the raw data files!!!*

- Remember to set up a virtual environment and install the required Python modules. The commands are executed from the parent folder since the Python requirements are common across the whole research project, but you can easily execute this from this specific folder.
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Set up the temporary and output data folders.
```
cd umls_knowledge_graph
mkdir tempdata
mkdir data_folder
```

- Run the following commands:
```
python umls_extractor.py --umlsfolder  <UMLS_RAW_FOLDER_PATH> --outputfolder tempdata/ --terminologies SNOMEDCT_US,ICD10CM
```
