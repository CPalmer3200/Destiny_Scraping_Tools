![Destiny_Pharma_PubMed-scraping_toolkit_v1](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/426c2d25-6702-4737-b7e6-6086801ffb29)

Please note this project is currently WIP and requires automation before completion.

This project is comprised of 4 scripts which provide 2 distinct functions. Dermal_main.py,
m3_main.py, and nasal_main.py are web-scraping bots designed to extract relevant PubMed
literature, rank the literature based on search category and importance, and send a push
email if any high priority literature is identified. These scripts are designed to be run
daily, using GitHub actions.

review_main.py is a script run monthly which assembles all of the literature gathered in the
previous month (for all 3 bots) and creates 3 seperate literature reviews. These are then
emailed to the target recipients.

FULL AND DETAILED DOCUMENTATION ALONG WITH FURTHER SUPPORT WILL BE MADE AVAILABLE UPON THE
COMPLETION OF THE PROJECT
