from urllib.parse import urljoin
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


# Dictionary to save parsed robots.txt files
ROBOTS = dict()


def get_elements(url, domain=None):
    """ Retrieve all elemevts of pages urls(to continue crawling) and static elements
    for each page

    :param url:
    :param domain:
    :return:
    """
    text = get_page(url)
    soup = BeautifulSoup(text)

    # Get all links
    links = get_links(soup, domain)

    # Get all static elements
    assets = get_assets(soup, domain)

    return links, assets


def get_assets(soup, domain):
    """ Get all static elements

    :param soup:
    :return:
    """
    assets = set()

    # Find all external style sheet references / all internal styles
    for link in soup.findAll('link', rel="stylesheet") + soup.findAll('style', type="text/css") + soup.findAll('img'):

        new_url = url_check(domain, link)
        if new_url:
            assets.add(new_url)

    return assets


def url_check(domain, link):
    """ check if url is valid / add domain to relative urls

    :param link:
    :return:
    """
    if 'href' in link.attrs:
        newurl = link.attrs['href']

    elif 'src' in link.attrs:
        newurl = link.attrs['src']

    else:
        return None

    # resolve relative URLs
    if newurl.startswith('/'):
        newurl = urljoin(domain, newurl)

    # ignore any URL that doesn't now start with http
    if newurl.startswith('http'):
        return newurl


def get_links(soup, domain=None):
    """Scan the text for http URLs and return a set
    of URLs found, without duplicates"""

    # look for any http URL in the page
    links = set()

    for link in soup.find_all('a'):
        new_url = url_check(domain, link)
        if new_url:
            if domain:
                if not new_url.startswith(domain):
                    continue

        links.add(new_url)

    return links


def get_page(url):
    """Get the text of the web page at the given URL
    return a string containing the content

    :param url:
    :return: url content
    """

    if robot_check(url):
        fd = urlopen(url)
        content = fd.read()
        fd.close()

        return content.decode('utf8')
    else:
        return ''


def robot_check(url):
    """Check whether we're allowed to fetch this URL from this site

    :param url:
    :return:
    """

    netloc = urlparse(url).netloc

    if netloc not in ROBOTS:
        robotsurl = urljoin(url, '/robots.txt')
        ROBOTS[netloc] = RobotFileParser(robotsurl)
        ROBOTS[netloc].read()

    return ROBOTS[netloc].can_fetch('*', url)

if __name__ == '__main__':
    url = 'https://www.apple.com/uk/'
    dmn = 'https://www.apple.com'

    url = 'https://www.johnlewis.com/home-garden/pictures/c60000496?rdr=1'
    dmn = 'https://www.johnlewis.com'

    urls, statics = get_elements(url, domain=dmn)

    for url in urls:
        print(url)

    print(len(urls))

    for s in statics:
        print(s)

