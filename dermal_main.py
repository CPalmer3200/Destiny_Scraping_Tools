import os
import time
import argparse
from Bio import Entrez
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import datetime


# Function for passing arguments to the bot - currently not used
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


# PubMed scraping function
def pubmed_scrape(query, bot_email, max_scrapes):

    # Create empty variables
    article_list = {}
    Entrez.email = bot_email

    # Perform scrape with the parsed query term
    ncbi_scrape = Entrez.esearch(db='pubmed', term=query, retmax=max_scrapes)

    # Save the scraped articles in a list
    scrape_list = Entrez.read(ncbi_scrape)
    list_format = scrape_list['IdList']

    # Loop over scrapes, fetch DOI, title, and publication date
    for scrape in list_format:
        id_num = scrape
        summary = Entrez.esummary(db='pubmed', id=id_num)
        read_summary_list = Entrez.read(summary)
        read_summary = read_summary_list[0]  # Access the dictionary within the list
        doi = read_summary.get('DOI', 'Unknown DOI')  # Unknown DOI if unable to access
        title = read_summary.get('Title', 'Unknown Title')  # Unknown title if unable to access
        pub_date = read_summary.get('PubDate', 'Unknown PubDate')

        # Append article information to dictionary
        article_list[doi] = {'Title': title, 'PubDate': pub_date}
        time.sleep(5)
    return article_list


def doi_checker(doi_to_check, doi_db_filename):

    temp_dois = []

    # Open the doi database, import and strip the entries
    with open(doi_db_filename, 'r') as doi_database:
        for entry in doi_database:
            entry = entry.rstrip()
            temp_dois.append(entry)

    # Check if the doi is already known and return boolean value
    if doi_to_check in temp_dois:
        return True, doi_to_check
    elif doi_to_check not in temp_dois:
        with open(doi_db_filename, 'a') as doi_database:
            doi_database.write(doi_to_check + '\n')
        return False, doi_to_check


def string_formatter(title, doi):
    url = 'https://dx.doi.org/' + str(doi)
    internal_str = f'{title}|{url}'  # Internal string used for splitting title and url in review_main.py
    external_str = f'{title} ({url})'  # External string used for push emails
    return internal_str, external_str


def write_to_rank(rank, text):
    # Write the text to the correct rank file
    with open(f'dermal_data/rank{rank}.txt', 'a', encoding='utf-8') as file:
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
    # Fetch the current date for email titling
    date = datetime.date.today()
    date = date.strftime('%d/%m/%Y')

    # Explanation of the search queries used to perform this search
    search_queries = 'This search was performed using the terms "burn wound infection/burn wound/burns" and' \
                     '"Staphylococcus aureus/S. aureus/Staph/MSSA/MRSA/methicillin resistant staphylococcus aureus"'
    destiny_url = 'https://www.destinypharma.com/'

    # html formatting of the push email
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
                    <h1 style="text-align: center;">New high priority papers are available on PubMed (XF-73 Dermal {date})</h1>
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
    email_password = os.environ["SECRET_TOKEN"]
    email_receiver = 'wrw@destinypharma.com'

    subject = f'New high priority literature (XF-73 Dermal {date})'  # Title of the email
    body = email_text

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.attach(MIMEText(body, 'html'))  # Instruct python to expect html content

    # Open and attach the logo (image.jpg) to the file
    with open('image.JPG', 'rb') as image_file:
        image = MIMEImage(image_file.read())
        image.add_header('Content-ID', '<image>')
        em.attach(image)

    # em.set_content(body)

    context = ssl.create_default_context()

    # Use SMTP to log in to the sender email and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


if __name__ == '__main__':

    # Create blank variables
    queries = []
    email_body = ""
    rank = 1
    new_paper_count = 0
    changes = {}

    # Extract search queries to a list
    with open('dermal_data/dermal_queries.txt', 'r') as search_queries:
        for line in search_queries:
            line = line.rstrip()
            queries.append(line)

    # Iterate over search queries and perform scrape
    for query in queries:
        print(f'Performing Pubmed search for "rank {rank}" topics...')
        bot_search = pubmed_scrape(query, 'automatedscrapingbot@gmail.com', 20)

        # Check DOI for duplicate or non-dupe
        for doi, info in bot_search.items():
            status, doi = doi_checker(doi, 'dermal_data/doi_db.txt')

            if not status:
                # Add 1 to new paper count
                new_paper_count +=1

                # Format paper string
                print(f'{doi} not found in database - recognised as new paper')
                title = info['Title']
                int_string, ext_string = string_formatter(title, doi)

                # Write to rank database
                write_to_rank(rank, int_string)

                if rank == 1:
                    # Append to email_body text if rank == 1
                    email_body += ext_string
                    email_body += "\n"
            elif status:
                print(f'{doi} already in database')

            else:
                print('Logic error please check bot configuration')

        # Log the changes of new papers for this rank
        changes[rank] = new_paper_count

        # Add 1 to the rank variable and reset new paper count
        rank += 1
        new_paper_count = 0

        # Sleep to prevent spam
        time.sleep(10)

    # Send email if any high priority papers are recorded
    if email_body != "":

        # HTML format the email body into a numbered list
        formatted_body = body_format(email_body)
        # Format the email with the html template
        formatted_email = html_formatting(formatted_body)
        # Send the email and print confirmation
        send_email(formatted_email)
        print('High priority papers found - push email sent')
    else:
        print('No new high priority papers identified')

    # Format Rank and New paper values
    formatted_string = f''
    for key, value in changes.items():
        temp_string = f'Rank {key}: {value}, '
        formatted_string += temp_string
    formatted_string = formatted_string[:-2]

    # Format final log string
    date = datetime.datetime.now()
    date = date.strftime("%H:%M %d/%m/%Y")
    changes_log = f'{date}, {formatted_string}'

    # Write to file and print
    with open('dermal_data/log.txt', 'a') as log:
        log.write(changes_log + '\n')
    print(changes_log)

    # Print closing message
    print('Query complete - returning to sleep')
