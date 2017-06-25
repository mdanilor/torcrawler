#!/usr/bin/python

import TorUrlProcessor
import HTMLProcessor
import Persistency
import sys
import threading
import ConfigLoader
import datetime

reload(sys)
sys.setdefaultencoding('utf8')

#processor = HTMLProcessor.HTMLProcessor()

#processor.feed(TorUrlProcessor.getContent("http://wiki5kauuihowqi5.onion/"))

i = 0

def run():
    global i
    threadNum = i
    print "Starting thread %d"%threadNum
    processor = HTMLProcessor.HTMLProcessor()
    while 1:
        print "%s: Thread %s is scanning a new hidden service."%(datetime.datetime.now(), threadNum)
        linkCount = 0
        hs = Persistency.getNewHiddenService()
        if hs is None:
            continue
        link = 0 #Just a random initial value.
        while linkCount < 1:
            link = Persistency.getLink(hs)
            print "%s: Thread %s just got a new link" % (datetime.datetime.now(), threadNum)
            if link is None:
                break
            linkCount += 1 #MAX OF 100 LINKS PER DOMAIN
            processor.setLink(link[1])
            content = TorUrlProcessor.getContent(link[1])
            print "%s: Thread %s just got content" % (datetime.datetime.now(), threadNum)

            if content == 0: #In case there was a problem getting the link content
                Persistency.saveLink(link, None, None, 3)
                print "%s: Thread %s link was broken" % (datetime.datetime.now(), threadNum)
                break
            if "content-type: text" not in str(content[0]).lower(): #In case we got content, but it's not readable text
                Persistency.saveLink(link, None, content, 4)
                continue
            try:
                processor.feed(content[1]) #Processing data
            except Exception:
                continue

            print "%s: Thread %s just processed content" % (datetime.datetime.now(), threadNum)

            title = processor.title #Getting data
            for newLink in processor.links:
                Persistency.newLink(newLink) #Potential new links to process
            Persistency.saveLink(link, title, content, 2) #Saving this link's data.
            print "%s: Thread %s just saved everything" % (datetime.datetime.now(), threadNum)

threadCount = ConfigLoader.threadcount

#run()

Persistency.removeGarbage()

while i < threadCount:
    threading.Thread(target=run).start()
    i += 1
