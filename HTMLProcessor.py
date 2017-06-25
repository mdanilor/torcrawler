#!/usr/bin/python

from HTMLParser import HTMLParser

class HTMLProcessor (HTMLParser):

    def __init__(self):
        self.links = []
        self.title = ""
        self.lastTag = ""
        self.baseLink = ""
        self.domainId = 0
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.lastTag = tag
        # print tag
        for attr in attrs:
            if attr[0] == "href":
                if "http://" not in attr[1] and "https://" not in attr[1]:
                    self.links.append([self.baseLink + attr[1], self.domainId])
                elif ".onion" in attr[1]:
                    self.links.append([attr[1], 0])

    # def handle_endtag(self, tag):
    #     if self.printData == 1:
    #         print "End tag:" + tag
    #
    #     if tag == 'title':
    #         self.printData = 0
    #
    #     if tag == 'a':
    #         self.printData = 0
    #         print "\n"

    def handle_data(self, data):
        if self.lastTag == "title" and len(data.strip()) > 0:
            self.title = data.decode().encode('utf-8', 'ignore').strip()

    def setLink(self, link):
        afterOnion = link.split(".onion", 1)

        splitted = afterOnion[1].split("/")

        joined = ""
        for part in splitted[:-1]:
            joined += (part + "/")
        joined = afterOnion[0] + ".onion" + joined
        if joined[-1] != '/':
            joined = joined + "/"
        self.baseLink = joined