#!/usr/bin/python
import TorUrlProcessor
import HTMLProcessor
import Persistency
import sys
import threading
import ConfigLoader
import datetime
import time

crawlNewHiddenServicesThreadMax = 0
crawlNewHiddenServicesThreadCount = 0
checkOnlineThreadMax = 0
checkOnlineThreadCount = 0
continueCrawlingThreadMax = 0
continueCrawlingThreadCount = 0

def crawlNewHiddenServices(crawlCount):
    global crawlNewHiddenServicesThreadCount
    crawlNewHiddenServicesThreadCount += 1

    processor = HTMLProcessor.HTMLProcessor()
    hiddenService = Persistency.getNewHiddenService()
    if (hiddenService is None): # if no hidden service available in database, kill thread.
        crawlNewHiddenServicesThreadCount -= 1
        time.sleep(1)
        return

    isOnline = 0

    #Getting links for this hiddenservice.
    for i in range(crawlCount):
        link = Persistency.getLink(hiddenService)

        #In case there are no more links do display
        if link is None:
            break

        print "Crawling %s" % link[1]

        processor.setLink(link[1])
        content = TorUrlProcessor.getContent(link[1])

        #in case of broken link
        if content == 0 or content is None:
            Persistency.saveLink(link, None, None, 3)
            continue

        #Flags that a valid address was found.
        isOnline = 1

        if "content-type: text" not in str(content[0]).lower():  # In case we got content, but it's not readable text
            Persistency.saveLink(link, None, content, 4)
            continue
        try:
            processor.feed(content[1])  # Processing data
        except Exception:
            continue

        for newLink in processor.links:
            Persistency.newLink(newLink)

        Persistency.saveLink(link, processor.title, content, 2)

    if isOnline == 1:
        Persistency.releaseHiddenService(hiddenService, 2)
    else:
        Persistency.releaseHiddenService(hiddenService, 3)
    crawlNewHiddenServicesThreadCount -= 1

def checkOnline():
    global checkOnlineThreadCount
    checkOnlineThreadCount += 1
    hs = Persistency.getOldHiddenService()
    if hs is None:
        checkOnlineThreadCount -= 1
        return
    link = Persistency.getOldLink(hs[0])
    content = TorUrlProcessor.getContent(link[1])
    print "Checking link %s"% link[1]
    if content == 0:
        Persistency.releaseHiddenService(hs[0], 3)
        Persistency.saveLink(link, None, None, 3)
    else:
        Persistency.releaseHiddenService(hs[0], 2)

        #saving changes on link
        processor = HTMLProcessor.HTMLProcessor()
        try :
            processor.feed(content[1])
        except UnicodeDecodeError:
            Persistency.saveLink(link, None, None, 4, 0)
        for newLink in processor.links:
            Persistency.newLink(newLink)
        Persistency.saveLink(link, processor.title, content, 2, 0)

    checkOnlineThreadCount -= 1

def continueCrawling(crawlCount):
    global continueCrawlingThreadCount
    continueCrawlingThreadCount += 1

    processor = HTMLProcessor.HTMLProcessor()

    hs = Persistency.getOldHiddenService()
    hiddenService = hs[0]

    isOnline = 0

    for i in range(crawlCount):
        link = Persistency.getLink(hiddenService)

        # In case there are no more links do display
        if link is None:
            break

        print "Crawling %s"%link[1]

        processor.setLink(link[1])
        content = TorUrlProcessor.getContent(link[1])

        # in case of broken link
        if content == 0 or content is None:
            Persistency.saveLink(link, None, None, 3)
            continue

        # Flags that a valid address was found.
        isOnline = 1

        if "content-type: text" not in str(content[0]).lower():  # In case we got content, but it's not readable text
            Persistency.saveLink(link, None, content, 4)
            continue
        try:
            processor.feed(content[1])  # Processing data
        except Exception:
            continue

        for newLink in processor.links:
            Persistency.newLink(newLink)

        Persistency.saveLink(link, processor.title, content, 2)

    if isOnline == 1:
        Persistency.releaseHiddenService(hiddenService, 2)
    else:
        Persistency.releaseHiddenService(hiddenService, 3)

    continueCrawlingThreadCount -= 1


def manageThreadMax():
    global crawlNewHiddenServicesThreadMax
    global checkOnlineThreadMax
    global continueCrawlingThreadMax
    while 1:
        stat = Persistency.getCurrentStatistics()
        maxThread = ConfigLoader.threadcount
        if stat[0]/(stat[0]+stat[1]) > 0.8:
            crawlNewHiddenServicesThreadMax = maxThread
            checkOnlineThreadMax = 0
            continueCrawlingThreadMax = 0
        elif stat[0]/(stat[0]+stat[1]) > 0.4:
            crawlNewHiddenServicesThreadMax = round(maxThread/2)
            checkOnlineThreadMax = round(maxThread/4)
            continueCrawlingThreadMax = round(maxThread/4)
        elif stat[0] / (stat[0] + stat[1]) > 0.2:
            crawlNewHiddenServicesThreadMax = round(maxThread / 3)
            checkOnlineThreadMax = round(maxThread / 3)
            continueCrawlingThreadMax = round(maxThread / 3)
        else:
            crawlNewHiddenServicesThreadMax = round(maxThread / 5)
            checkOnlineThreadMax = round(2*maxThread / 5)
            continueCrawlingThreadMax = round(2*maxThread / 5)
        time.sleep(60)



def main():
    global crawlNewHiddenServicesThreadMax
    global checkOnlineThreadMax
    global continueCrawlingThreadMax
    global crawlNewHiddenServicesThreadCount
    global checkOnlineThreadCount
    global continueCrawlingThreadCount

    print "Initializing crawler"

    Persistency.removeGarbage()
    threading.Thread(target=manageThreadMax).start()

    while 1:
        time.sleep(0.2)
        counter = 0
        if crawlNewHiddenServicesThreadCount < crawlNewHiddenServicesThreadMax:
            threading.Thread(target=crawlNewHiddenServices, args=(2,)).start()
        else:
            counter +=1

        if checkOnlineThreadCount < checkOnlineThreadMax:
            threading.Thread(target=checkOnline).start()
        else:
            counter +=1

        if continueCrawlingThreadCount < continueCrawlingThreadMax:
            threading.Thread(target=continueCrawling, args=(5,)).start()
        else:
            counter +=1

        if counter == 3:
            time.sleep(1)
            sum = crawlNewHiddenServicesThreadCount + checkOnlineThreadCount + continueCrawlingThreadCount
            print "Total threads running: %s"%sum

    return

main()