#!/bin/bash
PYTHON=python3.7
SCRIPT=insert_sentences.py

for file_pair in "pubmed19n0001.xml pubmed19n0139.xml" "pubmed19n0140.xml pubmed19n0278.xml" "pubmed19n0279.xml pubmed19n0417.xml" "pubmed19n0418.xml pubmed19n0556.xml" "pubmed19n0557.xml pubmed19n0695.xml" " pubmed19n0696.xml pubmed19n0834.xml" "pubmed19n0835.xml pubmed19n0972.xml";  do
  $PYTHON $SCRIPT $file_pair &
done