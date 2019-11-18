#!/bin/bash
PYTHON=python3
SCRIPT=collect_sentences.py

for file_pair in "pubmed19n0001.xml.gz pubmed19n0139.xml.gz" "pubmed19n0140.xml.gz pubmed19n0278.xml.gz" "pubmed19n0279.xml.gz pubmed19n0417.xml.gz" "pubmed19n0418.xml.gz pubmed19n0556.xml.gz" "pubmed19n0557.xml.gz pubmed19n0695.xml.gz" " pubmed19n0696.xml.gz pubmed19n0834.xml.gz" "pubmed19n0835.xml.gz pubmed19n0972.xml.gz";  do
  $PYTHON $SCRIPT $file_pair &
done