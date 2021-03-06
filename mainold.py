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

def initialCheck():
    global i
    threadNum = i
    print "Starting thread %d"%threadNum
    processor = HTMLProcessor.HTMLProcessor()
    while 1:
        linkCount = 0
        hs = Persistency.getNewHiddenService()

        if hs is None:
            continue

        print "%s: Thread %s just started processing a new hidden service: %s" % (
            datetime.datetime.now(), threadNum, hs)

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

            #Persistency.releaseHiddenService(hs, 2)

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

def secondaryCheck():
    global i
    threadNum = i
    print "Starting thread %d" % threadNum
    processor = HTMLProcessor.HTMLProcessor()
    while 1:
        linkCount = 0
        hidd = Persistency.getOldHiddenService(1)

        if hidd is None:
            continue

        hs = hidd[0]

        print "%s: Thread %s just started processing a new hidden service: %s" % (
            datetime.datetime.now(), threadNum, hs)

        processor.domainId = hs
        while linkCount < 10:
            epochI = int(time.time())

            link = Persistency.getLink(hs)
            if link is None:
                break
            linkCount += 1  # MAX OF 100 LINKS PER DOMAIN
            processor.setLink(link[1])
            content = TorUrlProcessor.getContent(link[1])

            if content == 0:  # In case there was a problem getting the link content
                Persistency.saveLink(link, None, None, 3)
                break

            #Persistency.releaseHiddenService(hs, 2)

            if "content-type: text" not in str(
                    content[0]).lower():  # In case we got content, but it's not readable text
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

def recheckOnline():
    global i
    threadNum = i
    print "Starting thread %d" % threadNum
    while 1:
        hs = Persistency.getOldHiddenService()
        if hs is None:
            continue
        content = TorUrlProcessor.getContent(hs[1])
        if content == 0:
            print "Broken link found on recheck"
            Persistency.releaseHiddenService(hs[0], 3)
        else:
            print "Ok link found on recheck"
            Persistency.releaseHiddenService(hs[0], 2)

def reportEveryHour():
    while 1:
        Persistency.report()
        time.sleep(3600)


activeThreads = 0
def fixStuff():

    global activeThreads
    activeThreads += 1

    processor = HTMLProcessor.HTMLProcessor()
    link = Persistency.getBuggedLink()
    if link is None:
        activeThreads -= 1
        return
    processor.setLink(link[1])
    content = TorUrlProcessor.getContent(link[1])

    if content == 0:  # In case there was a problem getting the link content
        Persistency.saveLink(link, None, None, 3)
        activeThreads -= 1
        return
    if "content-type: text" not in str(
            content[0]).lower():  # In case we got content, but it's not readable text
        Persistency.saveLink(link, None, content, 4)
        activeThreads -= 1
        return
    try:
        processor.feed(content[1])  # Processing data
    except Exception:
        activeThreads -= 1
        return
    try:
        processor.feed(content[1])  # Processing data
    except Exception:
        activeThreads -= 1
        return
    Persistency.saveLink(link, processor.title, content, 2)  # Saving this link's data.
    print "Corrected link " + link[1]

    activeThreads -=1

    return

def doFixing():
    global activeThreads
    while 1:
        if activeThreads < 80:

            threading.Thread(target=fixStuff()).start()

doFixing()

#
# threadCount = ConfigLoader.threadcount
#
# #run()
#
# Persistency.removeGarbage()
#
# while i < threadCount:
#     if (i % 5 == 0):
#         threading.Thread(target=initialCheck).start()
#     elif (i % 5 < 4 ):
#         threading.Thread(target=recheckOnline).start()
#     else:
#         threading.Thread(target = secondaryCheck).start()
#     i +=1
#
# threading.Thread(target=reportEveryHour).start()