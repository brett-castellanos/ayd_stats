import requests
import pymongo
import json
import time
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup


def main():
    """Run the webscraper for https://ayd.yunguseng.com/rating.html"""
    
    ayd_url = 'https://ayd.yunguseng.com/rating.html'

    with open('log_file.txt', 'w') as log_file:
        scrape_ayd(ayd_url, log_file)
    return 0


def scrape_ayd(ayd_url, log_file):
    """Scrapes the AYD webpage for SGF files from players subpages."""

    ayd_website = requests.get(ayd_url)
    log_file.write('Retreived {} at {}.\n'.format(ayd_url, datetime.now()))

    soup = BeautifulSoup(ayd_website.text, 'html.parser')

    # Get all the the 'href' tags
    all_links = soup.findAll(lambda tag: tag.name == 'a'
                             and tag.has_attr('href'))

    # Get the elements that contains an url starting with the current season
    current_season = 'season24'
    profile_links = [link['href'] for link in all_links if link['href']
                     .startswith('/{}/profile'.format(current_season))]

    # Prepend https://ayd.yunguseng.com to the profile links
    prepend_address = 'https://ayd.yunguseng.com/'
    profile_links = [prepend_address+link for link in profile_links]

    # Scrape each subpage
    for link in profile_links:
        scrape_subpage(link, log_file)
        time.sleep(5)


def scrape_subpage(subpage_url, log_file):
    """Scrapes the subpage and downloads the game records."""

    log_file.write('Attempting to get {}\n'.format(subpage_url))
    ayd_subpage = requests.get(subpage_url)
    soup = BeautifulSoup(ayd_subpage.text, 'html.parser')

    # Get all the the 'href' tags
    all_links = soup.findAll(lambda tag: tag.name == 'a'
                             and tag.has_attr('href'))

    # Get the elements that contains an url starting with 'file'
    game_links = [link['href'] for link in all_links if link['href']
                  .startswith('file')]

    # Prepend https://ayd.yunguseng.com/<current-season> to the profile links
    prepend_address = 'https://ayd.yunguseng.com/season24/'
    game_links = [prepend_address+link for link in game_links]

    # Download each file.
    for game in game_links:
        download_game(game, log_file)
        time.sleep(3)

    return None


def download_game(game_url, log_file):
    log_file.write('Attempting to get {}\n'.format(game_url))
    game_record = requests.get(game_url)

    # Get the filename from the meta-data
    print(game_record.headers)
    filename = game_record.headers['Content-Disposition'].replace(
        'attachment; filename=', ''
    )

    # Open a new file and write the binary to that file
    with open('./game_records/'+filename, 'wb') as game_file:
        game_file.write(game_record.content)

    return None


if __name__ == "__main__":
    main()
