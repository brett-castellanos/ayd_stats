from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
import time
import requests as req


def get_mongo_connection(database, collections):
    """
    Connects to the local MongoDB.

    Parameters
    database: str
      The name of the MongoDB
    collections: list
      A list of strings naming the collections

    Returns
    -------
    client:
      The MongoDB client
    database:
      The MongoDB database
    collections: dict
      A dictionary with the passed strings as keys
      and the Mongo Collections as values
    """

    client = MongoClient()
    db = client[database]
    col_dict = {name: db[name] for name in collections}

    return (client, db, col_dict)


def insert_html_to_mongo(url, soup, collection):
    """
    Given a BeautifulSoup object and a MongoDB collection,
    inserts the html into the collection.

    Parameters
    ----------
    url: str
      The URL for the soup object
    soup: BeauitifulSoup
      The html to be inserted into the collection
    collection: MongoDB Collection
      The collection into which the soup is inserted

    Returns
    -------
    None
    """
    collection.insert_one(
        {
            'url': url,
            'date_scraped': datetime.datetime.now(),
            'html': soup.prettify()
        }
    )


def soupify(url):
    """
    Given an url retreive the website and soupify the text.

    Parameters
    ----------
    url: str
      The full address of the website.
    logfile: str, default=None
      A file object for logging the attempt

    Returns
    -------
    soup: BeautifulSoup object
      Containins the html of the website.
    """
    try:
        webpage = req.get(url)
    except Exception as e:
        print('Failed to retrieve {}.'.format(url),
              'Error message: {}'.format(e))
        return None

    if webpage.status_code == 200:
        print('Retrieved {} at {}'
              .format(url, datetime.datetime.now()))
    else:
        print('Attempted to retreive {} at {}.'
              .format(url, datetime.datetime.now()),
              'Status Code: {}'.format(webpage.status_code))

    return BeautifulSoup(webpage.text, 'html.parser')


def scrape_ayd_html():
    """
    Loads the html for https://ayd.yunguseng.com/rating.html
    and the relevant subpages into MongoDB.

    Parameters
    ---------
    None

    Return
    ------
    None
    """

    rating_url = 'https://ayd.yunguseng.com/rating.html'
    prepend_address = 'https://ayd.yunguseng.com/'
    current_season = 'season24'

    client, ayd_db, col_dict = get_mongo_connection('ayd', ['html'])
    html_col = col_dict['html']

    soup = soupify(rating_url)
    insert_html_to_mongo(rating_url, soup, html_col)

    # Get all the the 'href' tags
    all_links = soup.findAll(lambda tag: tag.name == 'a'
                             and tag.has_attr('href'))

    # Get the elements that contains an url starting with the current season
    profile_links = [link['href'] for link in all_links if link['href']
                     .startswith('/{}/profile'.format(current_season))]

    # Prepend https://ayd.yunguseng.com to the profile links
    profile_links = [prepend_address+link for link in profile_links]

    # Scrape each subpage
    for link in profile_links:
        soup = soupify(link)
        insert_html_to_mongo(link, soup, html_col)
        time.sleep(5)


def scrape_eyd_html():
    """
    Scrapes the member pages of the form:
    https://eyd.yunguseng.com/season24/profile.php?id=564 from id=1 ... 850

    Parameters
    ---------
    None

    Return
    ------
    None
    """
    # Connect to local MongoDB
    client, ayd_db, col_dict = get_mongo_connection('eyd', ['html'])
    html_col = col_dict['html']

    # Scrape each link
    for link in generate_eyd_urls():
        soup = soupify(link)
        insert_html_to_mongo(link, soup, html_col)
        time.sleep(5)


def generate_eyd_urls():
    """
    Generates urls for scraping the EYD member pages.

    Parameters
    ----------
    None

    Return
    ------
    None
    """
    prepend_address = 'https://eyd.yunguseng.com/season24/profile.php?id='
    for id in range(1, 851):
        yield prepend_address + str(id)


def scrape_yd_profiles():
    """Scrapes all game records from the collected pages."""

    # Connect to AYD MongoDB
    client, ayd_db, col_dict = get_mongo_connection('ayd', ['html'])
    html_col = col_dict['html']

    # Iterate through html send to soup to scrape_subpage
    for link in html_col.find():
        profile_soup = BeautifulSoup(link['html'], 'html.parser')
        print("Now scraping {}".format(link['url']))
        scrape_subpage(profile_soup, 'ayd')

    # Connect to EYD MongoDB
    client, ayd_db, col_dict = get_mongo_connection('eyd', ['html'])
    html_col = col_dict['html']
    # Iterate through html and send soup to scrape subpage
    for link in html_col.find():
        profile_soup = BeautifulSoup(link['html'], 'html.parser')
        print("Now scraping {}".format(link['url']))
        scrape_subpage(profile_soup, 'eyd')


def scrape_subpage(profile_soup, yd):
    """Scrapes the subpage and downloads the game records."""

    # Get all the the 'href' tags
    all_links = profile_soup.findAll(lambda tag: tag.name == 'a'
                                     and tag.has_attr('href'))

    # Get the elements that contains an url starting with 'file'
    game_links = [link['href'] for link in all_links if link['href']
                  .startswith('file')]

    # Prepend https://ayd.yunguseng.com/<current-season> to the profile links
    prepend_address = 'https://{}.yunguseng.com/season24/'.format(yd)
    game_links = [prepend_address+link for link in game_links]

    # Download each file.
    for game in game_links:
        download_game(game, yd)
        time.sleep(5)

    return None


def download_game(game_url, yd):
    """Downloads the game at the provided URL."""

    try:
        game_record = req.get(game_url)
    except Exception as e:
        print('Failed to retrieve {}.'.format(game_url),
              'Error message: {}'.format(e))
        return None

    print('Now downloading {}'.format(game_url))

    # Get the filename from the meta-data
    filename = game_record.headers['Content-Disposition'].replace(
        'attachment; filename=', ''
    )

    # Open a new file and write the binary to that file
    with open('./{}_game_records/'.format(yd)+filename, 'wb') as game_file:
        game_file.write(game_record.content)

    return None
