![Destiny_Pharma_PubMed-scraping_toolkit_v1](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/426c2d25-6702-4737-b7e6-6086801ffb29)

## Introduction
This project is designed and tailored towards Destiny Pharma PLC to assist scraping of scientific literature and the assembly of monthly literature reviews.

## Repo architecture
This repo is comprised of 4 scripts which provide 2 distinct functions. 
1. dermal_main.py, m3_main.py, and nasal_main.py are web-scraping bots designed to extract relevant PubMed literature, rank the literature based on search category and importance, and send a push email if any high priority literature is identified. These scripts are automated to run daily, using GitHub actions.

2. review_main.py is a script run monthly which assembles all of the literature gathered in the previous month (for all 3 bots) and creates 3 seperate literature reviews. These are then emailed to the target recipients. This script is automated to run monthly, using GitHub actions.

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
1. _template.docx: Formatted .docx file which is the template for the respective literature review that is generated
2. start_date.txt: Accessed by the script to record the start date of the literature scraping
3. review_log.txt: Simple log file that documents the searches run and their respective date

## Adapting this repository
Although this bot network has been tailored for Destiny Pharma's specific use, it can be adapted by any user using the following steps:

IN THE FUTURE THIS REPO WILL BE UPDATED WITH A STREAMLINED VERSION ALLOWING EASIER ADAPTATION

Please clear any log, database, rank files and then format your own _queries.txt file

1. Within the write_to_rank() function in the bot scripts change the directory to a new one of your choice (example change m3_data/)

![image](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/8840b1c4-8b5a-404c-9208-e69cf6f906df)

2. Within the html_formatting() function change the search_queries variable to be a readable string of the rank 1 queries. Also change the destiny_url

![image](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/ad4b9fd8-c6f1-4cd0-abc4-5db266783a04)

3. Change the email_sender, email_password, and email_receiver variables in send_email() - THIS MUST BE DONE FOR review_main.py TOO. Optional changes also include replacing image.JPG with your chosen logo and rewriting the email subject.

![image](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/684c0c48-f46a-401e-a673-32ddd960d603)

4. Instances of the path (example: m3_data/) and email address must also be changed within if __name__ == '__main__':

5. A new _template.docx file must be created, formatted and stored in the directory

6. Within review_main.py alter the project names and document name under import_template() function

![image](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/d9b988ed-7498-484b-8ef4-a3a13b57a2b1)

7. Alter the directories list:

![image](https://github.com/CPalmer3200/Destiny_Scraping_Tools/assets/145576128/1a80c182-e183-485d-8d50-8927284ebeb3)

