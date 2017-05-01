**Note:** For Architecture and documentation please look at the doc folder.

**Requirements:**
  1) Fill mongodb connection info in configuration.py
  2) Fill Kafka broker IPs in configuration.py
  3) Create a topic in kafka with a large number of partitions / fill topic name in configuration.py


**How to install it:**
 1) clone repository

 2) go to clone folder

 3) install: `sudo pip/pip3 -e install .`


**How to run it:**
 1) Run consumer:
       `Python crawler/run.py`
 
 Note: For better response time, run the above on multiple instances of the consumer using different processes to increase parallelism.
 Alternatively Use docker swarm or marathon to start many containers.

 2) Start the web service:
        `Python crawler/webservice.py`


**Sumbit/query:**
 1) To submit a url use this API call example:
`curl 127.0.0.1:5000/api/v1/crawl/submit?url=https://www.apple.com/uk/iphone&domain=https://www.apple.com`

 2) To query the results:
 `curl 127.0.0.1:5000/api/v1/crawl/query?url=https://www.apple.com/uk/iphone`


**Note:** The code is tested with Python3.
