from docxtpl import DocxTemplate, InlineImage, RichText
import os
import smtplib
import ssl
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import docx.oxml
import docx.oxml.ns as ns


# Function to list all rank.txt files within the specified directory
def list_rank_files(directory):
    rank_files = []

    # Find all rank.txt files within the specified dictionary
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt') and 'rank' in file:
                rank_files.append(file)

    return rank_files


def extract_data(directory, rank_file, data_dict):
    # Build location
    location = f'{directory}{rank_file}'

    # Open the file and write contents to list
    papers_list = []
    with open(location, 'r') as file:
        for entry in file:
            entry = entry.rstrip()
            papers_list.append(entry)
    data_dict[rank_file] = papers_list

    return data_dict


# Simple function to fetch the correct template and project name
def import_template(directory):
    if directory == 'm3_data/':
        doc = DocxTemplate("m3_template.docx")
        project = 'NTCD-M3'
    elif directory == 'nasal_data/':
        doc = DocxTemplate("nasal_template.docx")
        project = 'XF-73 Nasal'
    elif directory == 'dermal_data/':
        doc = DocxTemplate("dermal_template.docx")
        project = 'XF-73 Dermal'
    return doc, project


def create_file(directory, template, data_dict, start_date):

    doc = template

    # Fetch the current date
    end_date = datetime.date.today()
    end_date = end_date.strftime('%d/%m/%Y')

    # Add context to the template
    context = {
        "start_date": start_date,
        "end_date": end_date
    }

    # Render and save the formatted document
    doc.render(context)
    doc.save(f'{directory}lit_review.docx')

    # Loop over the keys and corresponding variables in the dictionary
    new_dictionary = {}
    for key, data_list in data_dict.items():
        papers_list = []

        # Split the string into title and url
        for item in data_list:
            split_string = item.split('|')
            title = split_string[0]
            url = split_string[1]

            rt = RichText()
            rt.add(title, url_id=doc.build_url_id(url))  # Define text as rich text object and hyperlink the url

            # Append to a new list
            papers_list.append(rt)
        # Append to the correct key in a new dictionary
        new_dictionary[key] = papers_list

    # Loop over the new dictionary and input the data as context
    for key, rt_list in new_dictionary.items():
        context[key] = rt_list

    # Render the document and update table of contents
    doc.render(context)
    update_table_of_contents(doc)

    # Save the document in the given directory
    doc.save(f'{directory}lit_review.docx')

    return doc


def update_table_of_contents(doc):
    # Find the settings element in the document
    settings_element = doc.settings.element

    # Create an "updateFields" element and set its "val" attribute to "true"
    update_fields_element = docx.oxml.shared.OxmlElement('w:updateFields')
    update_fields_element.set(ns.qn('w:val'), 'true')

    # Add the "updateFields" element to the settings element
    settings_element.append(update_fields_element)


def send_email(directory, project):

    # Build the path of the file
    location = f'{directory}lit_review.docx'

    # Fetch the current date
    date = datetime.date.today()
    date = date.strftime('%d/%m/%Y')

    email_sender = 'automatedscrapingbot@gmail.com'
    email_password = 'mygx cllt nzsd stor'
    email_receiver = 'christopher.palmer32@gmail.com'

    subject = f'Literature review ({project} {date})'
    body = f'Please find attached the latest literature review for {project} ({date})'

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.attach(MIMEText(body))

    # Attach the lit review file to the email
    with open(location, 'rb') as attachment_file:
        attachment = MIMEApplication(attachment_file.read(), _subtype="docx")
        attachment.add_header('Content-Disposition', f'attachment; filename="lit_review.docx"')
        em.attach(attachment)

    context = ssl.create_default_context()

    # Send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def clear_ranks(directory, files_list):

    # Create temporary variable
    temp = 0

    # Delete all the rank files in the files list
    for file in files_list:
        file_path = f'{directory}{file}'
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"File '{file_path}' does not exist.")
            temp+=1

    # Check no errors occurred when deleting files and print outcome
    if temp > 0:
        print('Error in clearing all rank files')
    elif temp == 0:
        print('All rank files successfully cleared')


def review_log(project):
    # Create date and log string
    date = datetime.datetime.now()
    date = date.strftime("%H:%M %d/%m/%Y")
    changes_log = f'{date}, {project} review sent'

    # Write to file and print
    with open('review_log.txt', 'a') as log:
        log.write(changes_log + '\n')
    print('Changes logged')


if __name__ == '__main__':

    # State directories
    directories = ['nasal_data/', 'm3_data/', 'dermal_data/']

    # Fetch starting date of the literature reviews
    with open('start_date.txt', 'r') as file:
        start_date = file.readline().strip()

    # Begin loop over directories list
    for directory in directories:
        ranks = list_rank_files(directory)
        data_dict = {}

        # Loop over the listed ranks within each directory
        for rank in ranks:
            data_dict = extract_data(directory, rank, data_dict)

        # Remove the '.txt' extension from the key (not recognised by jinja2)
        new_dict = {}
        for key, value in data_dict.items():
            new_key = key.replace('.txt', '')
            new_dict[new_key] = value

        # Import the correct template
        doc, project = import_template(directory)
        print(f'Sourced {project} template')

        # Create the lit review
        final_doc = create_file(directory, doc, new_dict, start_date)
        print(f'Assembled {project} literature review')

        # Send email with literature review attached
        send_email(directory, project)
        print(f'{project} email delivered')

        # Clear all the rank files
        #clear_ranks(directory, ranks)

        # Log review sent
        #review_log(project)

    # Log start date for beginning new literature search
    date = datetime.date.today()
    date = date.strftime('%d/%m/%Y')
    with open('start_date.txt', 'w') as start_date_file:
        start_date_file.write(date)

    # Final print statement
    print('Queries complete, returning to sleep')



