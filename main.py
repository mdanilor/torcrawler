#!/usr/bin/python
import TorUrlProcessor
import HTMLProcessor
import Persistency
import sys
import threading
import ConfigLoader
import datetime
import time


def crawlNewHiddenServices(threadId):
    processor = HTMLProcessor.HTMLProcessor()
    hiddenService = Persistency.getNewHiddenService()
    if (hiddenService is None):
        print "No new hidden service available"
        return