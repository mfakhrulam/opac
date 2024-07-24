#!/bin/bash

# Ganti dengan URL file Google Drive Anda
# FILE_ID="1VyBV3E7C7VlW9RtqNQEnBe0CVs7wiRsY" model
FILE_ID="1hkEyOA2gl4iPeXs5a4-hsk01CgBDXPYV"
DESTINATION="./we_model/idwiki_new_lower_word2vec_300.zip"

# Download file dari Google Drive
# curl -L -o $DESTINATION "https://drive.google.com/uc?export=download&id=${FILE_ID}"
gdown "https://drive.google.com/uc?id=$FILE_ID" 

# Make directory
mkdir we_model/idwiki_new_lower_word2vec_300
mv idwiki_new_lower_word2vec_300.zip we_model

# Unzip file
unzip $DESTINATION -d we_model/idwiki_new_lower_word2vec_300
