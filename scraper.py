import requests, pymongo, json, time, os
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
    log_file.write('Retreived {} at {}.'.format(ayd_url, datetime.now()))
    
    soup = BeautifulSoup(ayd_website.text, 'html.parser')
    
    # Get the table to get the links to the subpages
    all_links = soup.findAll(lambda tag: tag.name=='a' and tag.has_attr('href'))
    
    # Get the element that contains the url '/season24'
    profile_links = [link['href'] for link in all_links if link['href'].startswith('/season24/profile')]
    
    # Prepend https://ayd.yunguseng.com to the profile links
    prepend_address = 'https://ayd.yunguseng.com/'
    profile_links = [prepend_address+link for link in profile_links]

    # Scrape each subpage
    for link in profile_links:
        scrape_subpage(link, log_file)

def scrape_subpage(subpage_url, log_file):
    print(subpage_url)




# table = bs.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="Table1")
# rows = table.findAll(lambda tag: tag.name=='tr')
    

if __name__ == "__main__":
    main()