![Destiny_Pharma_PubMed-scraping_toolkit_v1](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/426c2d25-6702-4737-b7e6-6086801ffb29)

## Introduction
This project is designed and tailored towards Destiny Pharma PLC to assist scraping of scientific literature and the assembly of monthly literature reviews.

## Repo architecture
This repo is comprised of 6 scripts which provide 2 distinct functions. 
1. X_main.py are web-scraping bots designed to extract relevant PubMed literature, rank the literature based on search category and importance, and send a push email if any high priority literature is identified. These scripts are automated to run daily, using GitHub actions.

2. review_X.py are scripts run monthly which assembles all of the literature gathered in the previous month (for a target bot) and creates a literature reviews. These are then emailed to the target recipients. This script is automated to run monthly, using GitHub actions.

## Usage

### Using the web scraping bots (dermal_main.py, m3_main.py, and nasal_main.py)
The bots rely on their respective _data folders which contain doi_db.txt, log.txt, rank.txt and queries.txt files:
1. doi_db.txt: Database containing all the DOIs the bot has identified - this prevent duplicates
2. log.txt: Simple log file recording when the bot was run and a breakdown of the papers per rank found
3. rank.txt: Files containing strings ready for inclusion in the monthly literature review
4. queries.txt: PubMed queries syntax run in order line by line

*The bot also uses the image.JPG in the main repo and attaches it to the email

### Using the monthly review script (review_main.py)
The review script does not have it's own respective folder but requires _template.docx(s), start_date.txt, review_log.txt files
1. template.docx: Formatted .docx file which is the template for the respective literature review that is generated
2. start_date.txt: Accessed by the script to record the start date of the literature scraping
3. review_log.txt: Simple log file that documents the searches run and their respective date

*The review script will automatically update the start_date and clear the rank.txt files once run

### Automation
This repo is designed to be automated using GitHub actions - please see the workflows folder and ensure the actions bot has permission to commit to the repo

![image](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/fe8d34bf-6401-4e91-bbc8-8e296277e229)

### Altering the daily scraping bot ('X_main.py')
Although this bot network has been tailored for specific use, it can be adapted by any user using the following steps:

Please clear any log, database, rank files and then create your own queries.txt, image.JPG, and template.docx files

1. Within the html_formatting() function change the search_queries variable to be a readable string of the rank 1 queries. Also change the 'url' variable

![image](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/54d5fa1f-8f60-41f6-b204-fb7c235cec70)

2. Alter the bot_email, project name and directory under main() function

![image](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/50c2c380-51f4-4ae4-8d34-ccfc6ba16953)

3. Change the email_password, and email_receiver variables in main()

![image](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/3995d000-2464-4846-ae31-c399c928103d)


### Altering the literature review script (review_x.py)

1. Alter the bot_email, project name and directory under main() function

2. Change the email_password, and email_receiver variables in main()



