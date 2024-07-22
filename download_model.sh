#!/bin/bash

# Ganti dengan URL file Google Drive Anda
FILE_ID="1VyBV3E7C7VlW9RtqNQEnBe0CVs7wiRsY"
DESTINATION="/app/we_model/idwiki_new_lower_word2vec_300.zip"

# Download file dari Google Drive
curl -L -o $DESTINATION "https://drive.google.com/uc?export=download&id=${FILE_ID}"

# Unzip file
unzip $DESTINATION -d /app/we_model/idwiki_new_lower_word2vec_300
