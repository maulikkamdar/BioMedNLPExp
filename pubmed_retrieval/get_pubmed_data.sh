DATA_FOLDER=data_folder/pubmed/
UINPUT=$1

echo $UINPUT

if [ $UINPUT  ==  "update" ]
then
    echo "You are downloading the PubMed Update files"
    FNAME=update.txt
    FFOLDER="update/"
    # update URL ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/
    PUBMED_URL=ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/
else
    echo "You are downloading the PubMed Baseline files"
    FNAME=baseline.txt
    FFOLDER="baseline/"
    # baseline URL ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/
    PUBMED_URL=ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/
fi

INPUT_FOLDER=$DATA_FOLDER$FFOLDER
INPUT=$INPUT_FOLDER$FNAME

mkdir $INPUT_FOLDER
curl $PUBMED_URL > $INPUT
IFS=' '
XMLS='xml.gz'
MD5='md5'
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
i=1
while read mode mode_n ftp user size month date time fname
do
    test $i -lt 1 && ((i=i+1)) && continue
    if [[ "$fname" == *"$XMLS"* ]]; then
        if [[ "$fname" != *"$MD5"* ]]; then
            echo $PUBMED_URL$fname
            curl $PUBMED_URL$fname > $fname
            mv $fname $INPUT_FOLDER
            gzip -d $INPUT_FOLDER$fname
            zipfile=$(echo $INPUT_FOLDER$fname | sed 's/.\{3\}$//')
            python pubmed_parser.py --file $zipfile --mode parse --abstract true --mesh true
            rm $INPUT_FOLDER$fname
            rm $zipfile
        fi
    fi
    ((i=i+1))
done < $INPUT