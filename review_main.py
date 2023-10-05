from docxtpl import DocxTemplate
import os
import smtplib
import ssl
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import docx.oxml
import docx.oxml.ns as ns


# Function to list all rank.txt files within the specified directory
def list_rank_files(directory):
    rank_files = []

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


def import_template(directory):
    if directory == 'm3_data/':
        doc = DocxTemplate("m3_template.docx")
        project = 'NTCD-M3'
    elif directory == 'nasal_data/':
        doc = DocxTemplate("nasal_template.docx")
        project = 'XF-73 Nasal'
    elif directory == 'dermal_data/':
        doc = DocxTemplate("dermal_template.docx")
        project = 'XF-73 Nasal'
    return doc, project


def create_file(directory, template, data_dict):

    doc = template

    end_date = datetime.date.today()
    end_date = end_date.strftime('%d/%m/%Y')

    # Add context to the template
    context = {
        "start_date": 'Start date',
        "end_date": end_date
    }

    # Render and save the formatted document
    doc.render(context)
    doc.save(f'{directory}lit_review.docx')

    for key, data_list in data_dict.items():
        context[key] = data_list
    doc.render(context)
    update_table_of_contents(doc)

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


def send_email(project, file_name):

    date = datetime.date.today()
    date = date.strftime('%d/%m/%Y')

    email_sender = 'automatedscrapingbot@gmail.com'
    email_password = 'mygx cllt nzsd stor'
    email_receiver = 'christopher.palmer32@gmail.com'

    subject = f'Literature review ({project} {date})'
    body = 'Please find attached the latest literature review'

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.attach(MIMEText(body))

    with open(file_name, 'rb') as attachment_file:
        attachment = MIMEApplication(attachment_file.read(), _subtype="docx")
        attachment.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
        em.attach(attachment)

    context = ssl.create_default_context()

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
            print(f"File '{file_path}' has been deleted.")
        else:
            print(f"File '{file_path}' does not exist.")
            temp+=1

    # Check no errors occurred when deleting files and print outcome
    if temp > 0:
        print('Error in clearing all rank files')
    elif temp == 0:
        print('All rank files successfully cleared')


if __name__ == '__main__':

    # State directories
    directories = ['m3_data/']

    # Begin loop over directories list
    for directory in directories:
        ranks = list_rank_files(directory)
        print(ranks)
        data_dict = {}

        # Loop over the listed ranks within each directory
        for rank in ranks:
            data_dict = extract_data(directory, rank, data_dict)
        print(data_dict)
        # Import the correct template
        doc, project = import_template(directory)
        print('Sourced template')


        new_dict = {}
        for key, value in data_dict.items():
            new_key = key.replace('.txt', '')  # Remove the '.txt' extension from the key
            new_dict[new_key] = value
        print(new_dict)


        # Create the lit reviews
        final_doc = create_file(directory, doc, new_dict)

        # Send email with literature review attached
        # send_email(project, final_doc)

        # Clear all the rank files
        # clear_ranks(directory, ranks)



