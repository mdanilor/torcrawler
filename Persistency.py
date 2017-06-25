#!/usr/bin/python
import MySQLdb
import os
import hashlib
import time
import datetime
import threading
import ConfigLoader

def removeGarbage():
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()
    cursor.execute("UPDATE HiddenServices SET Status=0 WHERE Status=1")
    cursor.execute("UPDATE Links SET Status=0 WHERE Status=1")
    db.close()

def getNewHiddenService():
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password, db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()

    cursor.execute("UPDATE HiddenServices SET Status=1, FirstScan=%s, LatestScan=%s, ResponsibleThread=%s WHERE Status=0 ORDER BY Id LIMIT 1", (datetime.datetime.now(), datetime.datetime.now(), threading._get_ident()))
    db.commit()
    threadNumber = threading._get_ident()
    cursor.execute("SELECT Id, Url FROM HiddenServices WHERE Status=1 AND ResponsibleThread=%s", (threadNumber, ))
    result = cursor.fetchall()

    if cursor.rowcount == 0:
        db.close()
        time.sleep(1)
        return None

    id = int(result[0][0])
    db.close()
    return id

def getLink(hiddenServiceId):
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()

    cursor.execute("SELECT Id, Url, IsIndex, HiddenServiceId FROM Links WHERE Status=0 AND HiddenServiceId=%s ORDER BY Id LIMIT 1", (hiddenServiceId,))
    result = cursor.fetchall()
    if cursor.rowcount == 0:
        cursor.execute("SELECT Status FROM HiddenServices WHERE Id=%s", (hiddenServiceId, ))
        statusResult = cursor.fetchall()
        if statusResult[0][0] != 3:
            cursor.execute("UPDATE HiddenServices SET Status=2 WHERE Id=%s", (hiddenServiceId, ))
            db.commit()
        db.close();
        return None

    #print result

    link = []
    link.append(int(result[0][0]))
    link.append(result[0][1])
    link.append(int(result[0][2]))
    link.append(int(result[0][3]))

    cursor.execute ("UPDATE Links SET Status=1 WHERE Id=%s" , (link[0],))
    db.commit()
    db.close()

    return link



def saveLink(link, title, content, status, threadNum):
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()

    if status == 4: #In case it's not a text/html
        cursor.execute("UPDATE Links SET Status=4, Header=%s WHERE Id=%s", (content[0], link[0]))
        print "%s: Thread %s link is not text or html. Just saved this information." % (datetime.datetime.now(), threadNum)
        db.commit()
        db.close()
        return
    if status == 3: #In case of nothing found
        if (link[2] == 1):
            cursor.execute("UPDATE HiddenServices SET Status=%s WHERE Id=%s", (status, link[3]))
        print "%s: Thread %s link was broken. Just saved this information." % (datetime.datetime.now(), threadNum)
        cursor.execute("UPDATE Links SET Status=3 WHERE Id=%s", (link[0], ))
        db.commit()
        db.close()
        return
    #save content to file:
    filename = hashlib.md5(link[1]).hexdigest() + ".html"

    print "%s: Thread %s Starting hash process" % (datetime.datetime.now(), threadNum)
    contentHash = hashlib.md5(content[1]).hexdigest()
    print "%s: Thread %s Finished hash process" % (datetime.datetime.now(), threadNum)

    domain = link[1].replace("http://", "", 1)
    domain = domain.replace("https://", "", 1)
    splitted = domain.split("/")
    domain = splitted[0]
    path = ConfigLoader.resources + domain + "/" + filename

    if not os.path.exists(ConfigLoader.resources + domain):
        os.makedirs(ConfigLoader.resources + domain)

    print "%s: Thread %s Saving files..." % (datetime.datetime.now(), threadNum)
    with open(path, "w") as file:
        try:
            file.write(content[1].decode().encode('utf-8', 'ignore').strip())
        except UnicodeDecodeError:
            print  ("Unicode decode error while saving file. Moving on.")

    print "%s: Thread %s Files saved. Updating Link table." % (datetime.datetime.now(), threadNum)

    try:
        query = "UPDATE Links SET Title=%s, ResourcePath=%s, HTMLHash=%s, Status=%s, Header=%s WHERE Id=%s"
        cursor.execute(query, (title, path, contentHash, status, content[0], link[0]))
    except UnicodeDecodeError:
        print ("Unicode decode error while saving title. Moving on.")
        query = "UPDATE Links SET ResourcePath=%s, HTMLHash=%s, Status=%s, Header=%s WHERE Id=%s"
        cursor.execute(query, (path, contentHash, status, content[0], link[0]))

    print "%s: Thread %s Finished updating link table. Updating hidden services table." % (datetime.datetime.now(), threadNum)

    cursor.execute("UPDATE HiddenServices SET LatestScan=%s WHERE Id=%s", (datetime.datetime.now(), link[3]))

    if (link[2]  == 1):
        cursor.execute("UPDATE HiddenServices SET Status=%s, Name=%s WHERE Id=%s", (status, title, link[3]))
    if status == 2 :
        cursor.execute("UPDATE HiddenServices SET LastSeenOnline=%s WHERE Id=%s", (datetime.datetime.now(), link[3]))
    print "%s: Thread %s Finished saving." % (datetime.datetime.now(), threadNum)

    db.commit()
    db.close()

def newLink(url):
    if ".onion" not in url:
        return
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()
    if url[len(url)-1] == '/':
        url = url[:-1]

    cursor.execute("SELECT * FROM Links WHERE Url=%s", (url, ) )

    result = cursor.fetchall()
    if cursor.rowcount == 0:
        domainStringArray = url.lower().split(".onion")
        domainString = domainStringArray[0] + ".onion"
        if domainStringArray[1] is None or domainStringArray[1] == "/" or "index" in domainString[1] or domainStringArray[1] == "":
            isIndex = 1;
        else:
            isIndex = 0

        #checking if there is already a hs with that domain
        cursor.execute("SELECT Id FROM HiddenServices WHERE Url=%s", (domainString, ))
        hiddenService = cursor.fetchall()
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO HiddenServices (Url, Status) VALUES (%s, %s)",(domainString, 0))
            cursor.execute("SELECT Id FROM HiddenServices WHERE Url=%s", (domainString, ))
            result = cursor.fetchall()
            id = result[0][0]
        else:
            id = hiddenService[0][0]
        cursor.execute("INSERT INTO Links (Url, CreatedOn, HiddenServiceId, IsIndex, Status) \
                        VALUES (%s, %s, %s, %s, %s)", (url, datetime.datetime.now(), id, isIndex, 0))
    db.commit()
    db.close()
