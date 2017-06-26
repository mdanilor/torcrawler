#!/bin/usr/python
import sys
import Persistency
import TorUrlProcessor
import HTMLProcessor
import time
import threading

#Crawl a hidden service



#functions:

def getDomain(url):
    domainSplitted = url.split(".onion")
    domain = domainSplitted[0] + ".onion"
    return domain

def crawl():
    global domainId
    link = 1
    processor = HTMLProcessor.HTMLProcessor()
    while 1:
        epochI = int(time.time())

        link = Persistency.getLink(domainId)
        if link is None:
            break
        processor.setLink(link[1])
        content = TorUrlProcessor.getContent(link[1])

        if content == 0:  # In case there was a problem getting the link content
            Persistency.saveLink(link, None, None, 3)
            break


        if "content-type: text" not in str(content[0]).lower():  # In case we got content, but it's not readable text
            Persistency.saveLink(link, None, content, 4)
            continue
        try:
            processor.feed(content[1])  # Processing data
        except Exception:
            continue

        title = processor.title  # Getting data
        for newLink in processor.links:
            Persistency.newLink(newLink)  # Potential new links to process
        Persistency.saveLink(link, title, content, 2)  # Saving this link's data.

        epochF = int(time.time())
        print "All done with URL %s. Took %s seconds" % (link[1], epochF - epochI)

#getting started

if len(sys.argv) == 1:
    print "usage: python %s url"%sys.argv[0]
    exit()

if ".onion" not in sys.argv[1]:
    print "Not an onion address"
    exit()

url = sys.argv[1]
if url[-1] == "/":
    url = url[0:-1]

domainUrl = getDomain(url)
domainId = Persistency.getDomainFromUrl(domainUrl, url)


i = 0
while i < 50:
    i+= 1
    threading.Thread(target=crawl).start()