#!/usr/bin/python

import TorUrlProcessor
import HTMLProcessor
import Persistency
import sys
import threading
import ConfigLoader
import datetime
import time

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
        linkCount = 0
        hs = Persistency.getNewHiddenService()
        print "%s: Thread %s just started processing a new hidden service: %s" % (datetime.datetime.now(), threadNum, hs)

        if hs is None:
            continue
        processor.domainId = hs
        while linkCount < 1:
            epochI = int (time.time())

            link = Persistency.getLink(hs)
            if link is None:
                break
            linkCount += 1 #MAX OF 100 LINKS PER DOMAIN
            processor.setLink(link[1])
            content = TorUrlProcessor.getContent(link[1])

            if content == 0: #In case there was a problem getting the link content
                Persistency.saveLink(link, None, None, 3)
                break
            if "content-type: text" not in str(content[0]).lower(): #In case we got content, but it's not readable text
                Persistency.saveLink(link, None, content, 4)
                continue
            try:
                processor.feed(content[1]) #Processing data
            except Exception:
                continue


            title = processor.title #Getting data
            for newLink in processor.links:
                Persistency.newLink(newLink) #Potential new links to process
            Persistency.saveLink(link, title, content, 2) #Saving this link's data.

            epochF = int(time.time())
            print "All done with URL %s. Took %s seconds"%(link[1], epochF-epochI)

def reportEveryHour():
    while 1:
        time.sleep(3600)
        Persistency.report()

threadCount = ConfigLoader.threadcount

#run()

Persistency.removeGarbage()

while i < threadCount:
    threading.Thread(target=run).start()
    i += 1

threading.Thread(target=reportEveryHour).start()