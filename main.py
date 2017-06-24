#!/usr/bin/python

import TorUrlProcessor
import HTMLProcessor
import Persistency
import sys
import threading
import ConfigLoader


reload(sys)
sys.setdefaultencoding('utf8')

#processor = HTMLProcessor.HTMLProcessor()

#processor.feed(TorUrlProcessor.getContent("http://wiki5kauuihowqi5.onion/"))


def run():
    while 1:
        hs = Persistency.getNewHiddenService()
        if hs is None:
            continue
        link = Persistency.getLink(hs)
        processor = HTMLProcessor.HTMLProcessor()
        while link is not None:
            processor.setLink(link[1])
            content = TorUrlProcessor.getContent(link[1])
            if content == 0:
                Persistency.saveLink(link, "", "", 3)
                break
            processor.feed(content)
            title = processor.title
            for newLink in processor.links:
                Persistency.newLink(newLink)
            Persistency.saveLink(link, title, content, 2)
            link = Persistency.getLink(hs)

threadCount = ConfigLoader.threadcount

#run()


i = 0

while i < threadCount:
    threading.Thread(target=run).start()
    i += 1
