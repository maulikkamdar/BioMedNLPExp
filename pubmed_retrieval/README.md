## Extract content from PubMed Medline FTP

---

This folder contains a script to extract content from [PubMed MEDLINE FTP](https://www.nlm.nih.gov/databases/download/pubmed_medline.html). 

PubMed is used as a corpora to train a GLOVE model to generate biomedical word embedding vectors. These GLOVE vectors are used in the following publications.
- Kamdar, M. R., & Musen, M. A. (2021). [An empirical meta-analysis of the life sciences linked open data on the web](https://www.nature.com/articles/s41597-021-00797-y). Scientific data, 8(1), 1-21.
- Kamdar, M. R., Stanley, C. E., Carroll, M., Wogulis, L., Dowling, W., Deus, H. F., & Samarasinghe, M. (2020). [Text snippets to corroborate medical relations: An unsupervised approach using a knowledge graph and embeddings.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7233036/) AMIA Summits on Translational Science Proceedings, 2020, 288.
- Gonçalves, R. S., Kamdar, M. R., & Musen, M. A. (2019, June). [Aligning biomedical metadata with ontologies using clustering and embeddings.](https://link.springer.com/chapter/10.1007/978-3-030-21348-0_10) In European Semantic Web Conference (pp. 146-161). Springer, Cham.

The biomedical word embedding vectors trained in 2019 are publicly available here:
- Kamdar, M. (2019). Biomedical Word Vectors (Version 1). figshare. https://doi.org/10.6084/m9.figshare.9598760.v1 

---

### Code Execution

Before starting, remember to set up a virtual environment and install the required modules. 

The commands are executed from the parent folder since the Python requirements are common across the whole research project, but you can easily execute this from this specific folder.
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the data folder to extract different fields from PubMed MedLine abstracts.
```
cd pubmed_retrieval
mkdir data_folder
mkdir data_folder/pubmed
```

The script extracts the title and abstract fields from the different abstracts submitted to PubMed MEDLINE and stored in the FTP server. Using an internal parameter (@TODO expose this parameter to be invoked through the script execution), the Python script can also be used to extract the MeSH (medical subject heading) descriptor IDs and terms for each abstract. 

You can use the Python script over a single XML document and downloaded from the [FTP server](https://ftp.ncbi.nlm.nih.gov/pubmed/baseline) and unzipped locally using the following command (assuming your virtual environment is activated):

```
python pubmed_parser.py --file <XML_FILE_PATH> --mode parse
```

To execute the Python script to retrieve and extract these fields across all the XML files stored in the FTP server (without having to download each file locally), execute the following commands using the shell script (assuming your virtual environment is activated):
```
./get_pubmed_data.sh
```

NLM provides PubMed Data through an annual baseline and update files for the remaining year. These baseline and update files are stored at slightly different FTP URLs. You can use the above script to download and process the update files automatically by passing the parameter `update` to the shell script. By default, only the baseline files are downloaded.

The shell script will automatically pull XML files from the FTP URL (`baseline` or `update`), parse the XML to extract the relevant fields (title, abstract, MeSH headings) and generate a TSV formatted file with those columns. The TSV files are stored in the `data_folder/pubmed/baseline/` or `data_folder/pubmed/update/` folder for further use. The actual XML files are not stored locally and are instantaneously deleted during the script execution. During execution, you should see the following output (along with the `curl` requests)

```
-----------------------------
Parsing data_folder/pubmed/baseline/pubmed21n0051.xml
Found abstracts 30000
Extracted abstracts 21918
-----------------------------
```

This is printed for each file. It should be noted that the abstracts from which relevant fields are extracted might be less than the number of abstracts in each XML file. A possible justification is the requirement of `ArticleTitle` and `AbstractText` to be present in each abstract, and in some cases this might not be true. Or there might be a possible bug in the script!

** PS: The shell script takes a while to execute due to the size and number of XML files. You can slightly modify the script to only use a few XML files or terminate using `Ctrl+Z` or `Ctrl+C`**