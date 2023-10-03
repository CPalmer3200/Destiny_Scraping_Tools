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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import datetime


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
    url = 'https://dx.doi.org/' + str(doi)
    paper = f'{title} ({url})'
    return paper


# Write to the correct database
def write_to_rank(rank, text):
    with open(f'rank{rank}.txt', 'a') as file:
        file.write(text + '\n')


def body_format(email_body):
    # Splits the email_body variable into a list
    email_body_list = email_body.split('\n')

    # Formats email body into a numbered list
    email_body_html = '<ol style="color: black; font-size: 16px;">'
    for item in email_body_list:
        if item.strip():
            email_body_html += f'<li>{item.strip()}</li>'
    email_body_html += '</ol>'
    return email_body_html


def html_formatting(email_body):
    date = datetime.date.today()
    date = date.strftime('%d/%m/%Y')

    search_queries = 'This search was performed using the terms "nasal decolonisation/decolonization"' \
                ' AND "Staphylococcus aureus/S. aureus/Staph/MSSA/MRSA/methicillin resistant staphylococcus aureus"'
    destiny_url = 'https://www.destinypharma.com/'

    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    h1 {{
                        font-size: 22px;
                        color: white;
                        text-align: center;
                        font-family: 'Tw Cen MT', sans-serif; /* Use Tw Cen MT font */
                        text-decoration: underline; /* Underline the text */
                        margin: 0; /* Remove margin from the h1 element */
                    }}
                    .container {{
                        display: flex;
                        flex-direction: column;
                        justify-content: center; /* Center vertically */
                        align-items: center; /* Center horizontally */
                        background-color: #ff7d1d; /* Banner background color */
                        padding: 10px; /* Add padding to the banner */
                        height: auto;
                    }}
                    body {{
                        font-size: 16px;
                        color: black;
                        font-family: 'Tw Cen MT', sans-serif; /* Use Tw Cen MT font */
                        margin: 0; /* Remove default body margin */
                        padding: 0; /* Remove default body padding */
                    }}
                    img {{display: block; margin: 0 auto;
                    }}
                    hr {{
                        background-color: black; /* Black line */
                        height: 1px; /* Line thickness */
                        border: none;
                    }}
                    .small-text {{
                        font-size: 12px;
                        color: black;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <img src="cid:image">
                <div class="container">
                    <h1 style="text-align: center;">New high priority papers are available on PubMed (XF-73 Nasal {date})</h1>
                </div>
                {email_body}
                <hr> <!-- Black line -->
                <p class="small-text">
                    {search_queries}<br><br>
                    {destiny_url}
                </p>
            </body>
            </html>
            """
    return html


# Define email function where a message is sent to the recipient
def send_email(email_text):

    date = datetime.date.today()
    date = date.strftime('%d/%m/%Y')

    email_sender = 'automatedscrapingbot@gmail.com'
    email_password = ''
    email_receiver = 'christopher.palmer32@gmail.com'

    subject = f'New high priority literature (XF-73 Nasal {date})'
    body = email_text

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.attach(MIMEText(body, 'html'))

    with open('image.JPG', 'rb') as image_file:
        image = MIMEImage(image_file.read())
        image.add_header('Content-ID', '<image>')
        em.attach(image)

    # em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


if __name__ == '__main__':

    # Parse args and create empty variables
    doi_db, topic_list = get_args()
    queries = []
    email_body = ""
    rank = 1

    # Extract search queries to a list
    with open('queries.txt', 'r') as search_queries:
        for line in search_queries:
            line = line.rstrip()
            queries.append(line)

    # Iterate over search queries and perform scrape
    for query in queries:
        print(f'Performing Pubmed search for "rank {rank}" topics...')
        bot_search = pubmed_scrape(query, 'automatedscrapingbot@gmail.com', 20)

        # Check DOI for duplicate or non-dupe
        for doi, info in bot_search.items():
            status, doi = doi_checker(doi, doi_db)

            if not status:
                # Format paper string
                print(f'{doi} not found in database - recognised as new paper')
                title = info['Title']
                paper = string_formatter(title, doi)

                # Write to rank database
                write_to_rank(rank, paper)

                if rank == 1:
                    # Append to email_body text if rank == 1
                    email_body += paper
                    email_body += "\n"
            elif status:
                print(f'{doi} already in database')

            else:
                print('Logic error please check bot configuration')

        # Add 1 to the rank variable
        rank +=1

    # Send email if any high priority papers are recorded
    if email_body != "":

        # HTML format the email body into a numbered list
        formatted_body = body_format(email_body)
        # Format the email with the html template
        formatted_email = html_formatting(formatted_body)
        # Send the email and print confirmation
        send_email(formatted_email)
        print('High priority papers found - push email sent')

    # Print closing message
    print('Query complete - returning to sleep')