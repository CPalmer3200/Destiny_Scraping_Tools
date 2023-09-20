import importlib
import subprocess

packages_to_check = ['bio', 'tweepy', 'argparse', 'time']

for package in packages_to_check:
    try:
        importlib.import_module(package)
        print(f"{package} is already installed.")
    except ImportError:
        print(f"{package} is not installed. Installing...")
        subprocess.run(['pip', 'install', package])

import time
import argparse
from Bio import Entrez
from email.message import EmailMessage
import ssl
import smtplib


def get_args():
    parser = argparse.ArgumentParser(
        description='PubMed scraping bot',
        prog='pubmed_bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,)

    parser.add_argument(
        '-doi',
        dest='doi_db',
        default='doi_db.txt',
        help='DOI database location')
    parser.add_argument(
        '-topic',
        dest='topic',
        default='topics.txt',
        help='Topic .txt file location')
    args = parser.parse_args()

    doi_db_loc = args.doi_db
    topic = args.topic

    return doi_db_loc, topic


def pubmed_scrape(query, bot_email, max_scrapes):
    article_list = {}
    Entrez.email = bot_email

    ncbi_scrape = Entrez.esearch(db='pubmed', term=query, retmax=max_scrapes)
    scrape_list = Entrez.read(ncbi_scrape)
    list_format = scrape_list['IdList']
    for scrape in list_format:
        id_num = scrape
        summary = Entrez.esummary(db='pubmed', id=id_num)
        read_summary_list = Entrez.read(summary)
        read_summary = read_summary_list[0]  # Access the dictionary within the list
        doi = read_summary.get('DOI', 'Unknown DOI')
        title = read_summary.get('Title', 'Unknown Title')
        pub_date = read_summary.get('PubDate', 'Unknown PubDate')

        article_list[doi] = {'Title': title, 'PubDate': pub_date}
        time.sleep(3)
    return article_list


def doi_checker(doi_to_check, doi_db_filename):
    temp_dois = []
    with open(doi_db_filename, 'r') as doi_database:
        for entry in doi_database:
            entry = entry.rstrip()
            temp_dois.append(entry)
    if doi_to_check in temp_dois:
        return True, doi_to_check
    elif doi_to_check not in temp_dois:
        with open(doi_db_filename, 'a') as doi_database:
            doi_database.write(doi_to_check + '\n')
        return False, doi_to_check


def string_formatter(title, doi):
    url = 'http://dx.doi.org/' + str(doi)
    paper = f'{title} ({url})'
    return paper


# Define email function where a message is sent to the recipient
def send_email(email_text):

    email_sender = 'automatedscrapingbot@gmail.com'
    email_password = 'mygx cllt nzsd stor'
    email_receiver = 'christopher.palmer32@gmail.com'

    subject = 'Recently released high-priority papers'
    body = email_text

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


if __name__ == '__main__':
    doi_db, topic_list = get_args()
    t_list = []
    email_body = ""

    with open(topic_list, 'r') as topic_list:
        for line in topic_list:
            line = line.rstrip()
            t_list.append(line)
    print(f'Topic list: {t_list}')

    for t in t_list:
        print(f'Performing Pubmed search for "{t}"...')
        bot_search = pubmed_scrape(t, 'pubmedbot4@gmail.com', 20)

        for doi, info in bot_search.items():
            status, doi = doi_checker(doi, doi_db)

            if not status:
                print(f'{doi} not found in database - recognised as new paper')
                title = info['Title']  # Access the title from the info dictionary
                paper = string_formatter(title, doi)

                email_body += "\n"
                email_body += paper
            else:
                print(f'{doi} already in database')

    if email_body != "":
        send_email(email_body)

    print(f'Query complete - returning to sleep')