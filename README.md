How to install it:
 1) clone repository

 2) go to clone folder

 3) install: `sudo pip/pip3 -e install .`

How to run it:
 1) Run consumer:
       `Python wikirace/run.py`
 
 Note: For better response time, run the above on multiple instances of the consumer on different processes to increase parallelism.
 Use docker swarm or marathon to start many containers.

 2) Start the web service:
        `Python webservice.py`


Note: For Architecture and documentation look at the doc folder.
