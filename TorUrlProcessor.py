#!/usr/bin/python
import urllib2
import datetime
import sys

def getContent(url):
    opener = urllib2.build_opener(
        urllib2.ProxyHandler({"http": "localhost:8118"}),
        urllib2.ProxyHandler({"https": "localhost:8118"}),
    )
    urllib2.install_opener(opener)

    try:
        result = []
        response = urllib2.urlopen(url)
        result.append(response.info())
        result.append(response.read())
        return result
    except Exception:
        print "Erro na url " + url.encode('utf-8')
        return None

