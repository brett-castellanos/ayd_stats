from bs4 import BeautifulSoup


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
            'html': stats_soup.prettify()
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