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
import tweepy
from Bio import Entrez


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


def publish_twitter(tweet_string):
    api_key = 'QWVm3trwlXYaZzC1zdy2w8nx6'
    api_secret = 'sNWFUkhxURDrthUF3cLvaNejZFODi7rh3GxEibtl4INDdRqHi5'
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAAEuapgEAAAAA%2BW7Cq8SxcYZ49zO3h4%2Fy%2BWTIiw4%3DIPejMMNVrgff9oYnhkRdY7NFx4C01fBuM3vbAvDQBUNDZ47Xtd'
    access_token = '1696227369508315136-dWK5NSFd5wjW4RFsD5YxtZgibFmkeM'
    secret_access = 'j2xAH1STgFGnSrUvLDwxD6uIQl7ODsCSdFhBDQIN4ArkU'

    client = tweepy.Client(bearer_token, api_key, api_secret, access_token, secret_access)
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, secret_access)
    api = tweepy.API(auth)
    tweet = client.create_tweet(text=tweet_string)
    return tweet


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
    prelim_tweet = f'{title} ({url})'
    if len(prelim_tweet) > 260:
        short_title = f'{title[:151]}...'
        tweet = f'{short_title} ({url})'
        if len(tweet) > 260 and len(url) > 110:
            url_replace = 'URL too long to tweet'
            tweet = f'{short_title} ({url_replace})'
        else:
            tweet = f'{short_title} ({url})'
    else:
        tweet = prelim_tweet
    return tweet


if __name__ == '__main__':
    doi_db, topic_list = get_args()
    t_list = []
    new_tweets = 0

    with open(topic_list, 'r') as topic_list:
        for line in topic_list:
            line = line.rstrip()
            t_list.append(line)
    print(f'Topic list: {t_list}')

    for t in t_list:
        print(f'Performing Pubmed search for "{t}"...')
        bot_search = pubmed_scrape(t, 'pubmedbot4@gmail.com', 15)

        for doi, info in bot_search.items():
            status, doi = doi_checker(doi, doi_db)

            if not status:
                print(f'{doi} not found in database - preparing to tweet')
                title = info['Title']  # Access the title from the info dictionary
                to_tweet = string_formatter(title, doi)
                publish_twitter(to_tweet)
                print('Published to Twitter')
                new_tweets += 1
                time.sleep(10)
            else:
                print(f'{doi} already in database')
                time.sleep(0.5)
    print(f'Query complete, {new_tweets} new tweets published - returning to sleep')