import concurrent.futures as ft
import copy

import logging

from crawler.configuration import INGESTION_TOPIC, OUTPUT_COLNM, MAX_DEPTH
from crawler.utils.bfilter import BloomFilter
from crawler.utils.kfkpywrapper import KfkConsumer, KfkProducer
from crawler.utils.mongo import mongo_connect
from crawler.utils.string import hash_str
from crawler.utils.url import get_elements

cons = KfkConsumer(INGESTION_TOPIC, 'con', set_offset_to_end=True)

# cons = KfkConsumer(INGESTION_TOPIC, 'con')
prod = KfkProducer(INGESTION_TOPIC)
dbcon_oput = mongo_connect(col_nm=OUTPUT_COLNM)


def make_tmplt(url, src=None, parent=None, domain=None):
    """ make template for json that pushed to kafka

    :param url: url
    :param title: title
    :param parent: a list of dictionary(url and title) used to save the history of links
    :param dst: to link
    :param src: from link
    :return:
    """
    tmpl = {
        'url': url,
        'parent': parent if parent else list(),
        'domain': domain,
    }

    tmpl['src'] = src if src else tmpl['url']
    return tmpl


def add_parents(old_prnts, url):
    """ append one more parents(url, title) to current list of parents

    :param old_prnts: current list of parents
    :param url: new url
    :param title: title url
    :return:
    """
    new_prnts = copy.deepcopy(old_prnts)
    new_prnts.append(url)

    return new_prnts


def push_en(entry):
    """ push entry to kafka

    :param entry: entry
    """
    prod.produce(entry)


def push(entries):
    """ push the entries to kafka using multiple threads

    :param entries: list of entries to push to kafka
    """
    with ft.ThreadPoolExecutor(max_workers=500) as executor:
        future_to_entry = {
            executor.submit(push_en, entry): entry
            for entry in entries}

        for no, future in enumerate(ft.as_completed(future_to_entry.keys())):
            # print('finish pushing. {}'.format(no))
            pass


def exists(bf, url):
    """ using bloom filter to check if we already have records in memory
     save round trip time to db by avoiding call

    :param bf: bloom filter object
    :param url: url
    :return:
    """
    id = hash_str(url)
    if bf.lookup(id):
        print('bf check')
        return True
    else:
        if dbcon_oput.find_one({'_id': id}):
            bf.add_one(id)
            print('added to bf')
            return True
        else:
            return False


def persist_assets_db(url, src, domain, assets):
    """ insert the assets for given url to db

    :param entry: entry
    :param prs: parents list
    """
    # Hash the src as key for db
    id = hash_str(url)

    ins = {
        '_id': id,
        'src': src,
        'domain': domain,
        'assets': list(assets),
        'url': url
    }

    dbcon_oput.insert_one(ins)


def run():
    """ consume from kafka / retrieve links / persists assets / push new links back to kafka

    """
    # In memory bloom filter to prevent querying the database
    bf = BloomFilter()

    for msg in cons.consume():
        try:
            print('Depth level:{}'.format(len(msg['parent'])))

            # Check if this url is already processed
            if exists(bf, msg['url']):
                continue

            # add current url as parent/ we keep the history of the parents
            # of urls to be able to define a depth for crawling
            prs = add_parents(msg.get('parent'), msg.get('url'))

            # get all links in a page
            links, assets = get_elements(msg.get('url'), msg.get('domain'))

            # Persist the assets for a link to database
            persist_assets_db(url=msg.get('url'), src=msg.get('src'), domain=msg.get('domain'), assets=assets)

            entries = []
            for link in links:
                entry = make_tmplt(link, src=msg.get('src'), domain=msg.get('domain'), parent=prs)

                entries.append(entry)

                # check if reached the defined max depth
                if len(msg['parent']) == MAX_DEPTH:
                    break

            # Push entries(urls founds in page) to kafka to crawl
            if entries:
                push(entries)

        except Exception as e:
            logging.error(e)

if __name__ == '__main__':
    run()
