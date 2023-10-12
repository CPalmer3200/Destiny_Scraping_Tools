![Destiny_Pharma_PubMed-scraping_toolkit_v1](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/426c2d25-6702-4737-b7e6-6086801ffb29)

## Introduction
This project is designed and tailored towards Destiny Pharma PLC to assist scraping of scientific literature and the assembly of monthly literature reviews.

## Repo architecture
This repo is comprised of 4 scripts which provide 2 distinct functions. 
1. Dermal_main.py, m3_main.py, and nasal_main.py are web-scraping bots designed to extract relevant PubMed literature, rank the literature based on search category and importance, and send a push email if any high priority literature is identified. These scripts are automated to run daily, using GitHub actions.

2. review_main.py is a script run monthly which assembles all of the literature gathered in the previous month (for all 3 bots) and creates 3 seperate literature reviews. These are then emailed to the target recipients. This script is automated to run monthly, using GitHub actions.

## Usage
