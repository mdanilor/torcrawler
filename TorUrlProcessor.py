#!/usr/bin/python
import urllib2
import datetime

def getContent(url):
    opener = urllib2.build_opener(
        urllib2.ProxyHandler({"http": "localhost:8118"}),
        urllib2.ProxyHandler({"https": "localhost:8118"}),
    )
    urllib2.install_opener(opener)

    try:
        response = urllib2.urlopen(url)
        return response.read()
    except urllib2.HTTPError, err:
        print "Erro na url " + url
        return 0
    except URLError:
	print "Erro na url " + url
	return 0

