import logging
from time import sleep

from flask import Flask
from flask_restful import reqparse, Api, Resource

from crawler.configuration import OUTPUT_COLNM, INGESTION_TOPIC
from crawler.run import make_tmplt
from crawler.utils.kfkpywrapper import KfkProducer
from crawler.utils.mongo import mongo_connect
from crawler.utils.string import hash_str

app = Flask(__name__)
api = Api(app)

# set up request parser
parser = reqparse.RequestParser()
prod = KfkProducer(INGESTION_TOPIC)


class CrawlerServiceInfo(Resource):
    def get(self):
        return 'Webservice Version 1.0'


class CrawlerService(Resource):
    def query_db(self, url):
        """ query db for result / wait if it does not exists

        :param fr: from
        :param to: to
        :return:
        """
        q = {'src': url}
        p = {'url': 1, 'assets': 1, '_id': 0}

        return list(dbcon_oput.find(q, p).limit(0))

    def get(self, ops=None):

        if ops is None:
            return 'Please pass either submit or query operation. example: ' \
                   'curl IP:5000/api/v1/crawl/submit or query?...'

        args = parser.parse_args()
        parser.add_argument('url', default=None, type=str)
        parser.add_argument('domain', default=None, type=str)

        print(ops, args)
        if ops == 'submit':
            if not args.url or not args.domain:
                return 'Please pass both url and domain. example: ' \
                       'curl IP:5000/api/v1/crawl/submit?url=https://www.apple.com/uk/iphone&domain=https://www.apple.com'
            else:
                # submit the request
                entry = make_tmplt(url=args.url, domain=args.domain)
                prod.produce(entry)
                return entry

        if ops == 'query':
            if not args.url:
                return 'Please pass url. example: curl IP:5000/api/v1/crawl/query?url=https://www.apple.com/uk/iphone'
            else:
                # query result collection
                return self.query_db(args.url)


# route resource here
api_base_url = '/api/v1'
api.add_resource(CrawlerServiceInfo, '/')
api.add_resource(CrawlerService, api_base_url + '/crawl/<ops>')


# ######### EXAMPLES: #################
# curl 127.0.0.1:5000/api/v1/crawl\?model=MODEL2


if __name__ == '__main__':
    dbcon_oput = mongo_connect(col_nm=OUTPUT_COLNM)

    logging.info('Successfully loaded the app')
    app.run(host='0.0.0.0', debug=True)
