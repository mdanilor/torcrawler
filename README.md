# torcrawler
A multi-thread hidden service crawler.

## Before you get started
###Install the required software
You must have three software installed and configured on your computer. They are:
Tor (duuh) - https://www.torproject.org/ ('apt-get install tor' on ubuntu)
Privoxy - https://www.privoxy.org/ (also apt-get install on ubuntu)
MySQL Server - https://www.mysql.com/ (apt-get install mysql-server on ubuntu)

###Configure Privoxy
Then you must alter Privoxy's config. Add the following line to the Privoxy config file (/etc/privoxy/config):

`forward-socks5 / localhost:9050 .`

Where 9050 is Tor's default port.

###Create database
Now you must add the MySQL database. The database is dumped on the file db.sql. After that, you must add an entry do the table HiddenServices and another to the table Links.
This entry must contain a darkweb seed: a link for the crawler to get started.

###Configure the crawler
Edit the file ConfigLoader.py with your data.

##Getting started

Simply use
`python main.py`