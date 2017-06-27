#!/usr/bin/python
import MySQLdb
import os
import hashlib
import time
import datetime
import threading
import ConfigLoader

def createNewReport(cursor):
    # creating new report
    cursor.execute("INSERT INTO Report (StartTime) VALUES (%s)", (datetime.datetime.now(),))
    cursor.execute("SELECT Id FROM Report ORDER BY Id DESC")  # getting latest report Id
    res = cursor.fetchall()
    reportId = res[0][0]
    return reportId

def createNewDataGroup(cursor, reportId, label):
    cursor.execute("INSERT INTO DataGroup (ReportId, Label) VALUES (%s, %s)", (reportId, label))
    cursor.execute("SELECT Id FROM DataGroup ORDER BY Id DESC")
    res = cursor.fetchall()
    dgId = res[0][0]
    return dgId

def createNewData(cursor, label, data, dgId):
    cursor.execute("INSERT INTO Data (Label, Data, DataGroupId) VALUES (%s, %s, %s)", (label, data, dgId))

def report():
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()

    #Creating new report
    reportId = createNewReport(cursor)

    #getting how many hidden services were found
    dgId = createNewDataGroup(cursor, reportId, "Hidden Services Found")

    cursor.execute("SELECT COUNT(*) FROM Links INNER JOIN HiddenServices ON Links.HiddenServiceId=HiddenServices.Id WHERE HiddenServices.Status = 2 AND Links.Status = 2 AND Links.IsIndex=1")
    res = cursor.fetchall()
    createNewData(cursor, "Online", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links INNER JOIN HiddenServices ON Links.HiddenServiceId=HiddenServices.Id WHERE HiddenServices.Status = 3 AND Links.Status = 3 AND Links.IsIndex=1")
    res = cursor.fetchall()
    createNewData(cursor, "Offline", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM HiddenServices WHERE Status=1")
    res = cursor.fetchall()
    createNewData(cursor, "Under analysis", res[0][0], dgId)

    #Getting which webserver is running
    dgId = createNewDataGroup(cursor, reportId, "WebServer")

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%apache%'")
    res = cursor.fetchall()
    createNewData(cursor, "Apache", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%nginx%'")
    res = cursor.fetchall()
    createNewData(cursor, "Nginx", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%lighttpd%'")
    res = cursor.fetchall()
    createNewData(cursor, "Lighttpd", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%twistedweb%'")
    res = cursor.fetchall()
    createNewData(cursor, "TwistedWeb", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%iis%'")
    res = cursor.fetchall()
    createNewData(cursor, "IIS", res[0][0], dgId)

    #Getting which operating system is running
    dgId = createNewDataGroup(cursor, reportId, "Operating System")

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%Debian%'")
    res = cursor.fetchall()
    createNewData(cursor, "Debian", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%Ubuntu%'")
    res = cursor.fetchall()
    createNewData(cursor, "Ubuntu", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%CentOs%'")
    res = cursor.fetchall()
    createNewData(cursor, "CentOs", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%FreeBSD%'")
    res = cursor.fetchall()
    createNewData(cursor, "FreeBSD", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%Fedora%'")
    res = cursor.fetchall()
    createNewData(cursor, "Fedora", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%Suse%'")
    res = cursor.fetchall()
    createNewData(cursor, "Suse", res[0][0], dgId)

    cursor.execute("SELECT COUNT(*) FROM Links WHERE (Status=2 OR Status=5) AND IsIndex=1 AND Header LIKE '%Windows%'")
    res = cursor.fetchall()
    createNewData(cursor, "Windows", res[0][0], dgId)

    #Getting mirror data
    dgId = createNewDataGroup(cursor, reportId, "Mirrors")

    cursor.execute("SELECT COUNT(*) AS UniqueCount, SUM(Mirrors.Count) AS MirrorCount FROM (SELECT COUNT(*) AS Count FROM Links WHERE IsIndex=1 AND (Status=2 OR Status=5) GROUP BY HTMLHash) Mirrors WHERE Mirrors.Count > 1")
    res = cursor.fetchall()
    createNewData(cursor, "Total mirrored", res[0][0], dgId)
    createNewData(cursor, "Total mirrors", res[0][1], dgId)

    dgId = createNewDataGroup(cursor, reportId, "TOP 10 Mirrored")
    cursor.execute("SELECT Mirrors.Count AS Count, Mirrors.Hash AS Hash, Mirrors.Title AS Title FROM (SELECT COUNT(*) AS Count, HTMLHash as Hash, Title FROM Links WHERE IsIndex=1 AND (Status=2 OR Status=5) GROUP BY HTMLHash) Mirrors ORDER BY Mirrors.Count DESC LIMIT 10")
    res = cursor.fetchall()
    for result in res:
        createNewData(cursor, result[2], result[0], dgId)

    cursor.execute("UPDATE Report SET FinishTime=%s WHERE Id=%s", (datetime.datetime.now(), reportId))

    db.commit()
    db.close()

def removeGarbage():
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()
    cursor.execute("UPDATE HiddenServices SET Status=0 WHERE Status=1")
    cursor.execute("UPDATE Links SET Status=0 WHERE Status=1")
    db.commit()
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

def getOldHiddenService(desc = 0):
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()
    if desc == 0:
        cursor.execute(
            "UPDATE HiddenServices SET Status=1, LatestScan=%s, ResponsibleThread=%s WHERE Status=2 OR Status=3 ORDER BY LatestScan LIMIT 1",
            (datetime.datetime.now(), threading._get_ident()))
    else:
        cursor.execute(
            "UPDATE HiddenServices SET Status=1, LatestScan=%s, ResponsibleThread=%s WHERE Status=2 OR Status=3 ORDER BY LatestScan DESC LIMIT 1",
            (datetime.datetime.now(), threading._get_ident()))
    db.commit()
    threadNumber = threading._get_ident()
    cursor.execute("SELECT Id, Url FROM HiddenServices WHERE Status=1 AND ResponsibleThread=%s", (threadNumber,))
    if cursor.rowcount == 0:
        db.close()
        time.sleep(1)
        return None
    res = cursor.fetchall()
    db.close()
    return res[0]

def releaseHiddenService(hiddenServiceId, status):
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()
    now = datetime.datetime.now()
    if status == 2:
        cursor.execute("UPDATE HiddenServices SET Status=%s, LatestScan=%s, LastSeenOnline=%s WHERE Id=%s",
                       (status, now, now, hiddenServiceId))
        cursor.execute("UPDATE Links SET Status=2 WHERE HiddenServiceId=%s AND IsIndex=1", (hiddenServiceId))
    else:
        cursor.execute("UPDATE HiddenServices SET Status=%s, LatestScan=%s WHERE Id=%s",
                       (status, now, hiddenServiceId))
    db.commit()
    db.close()

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



def saveLink(link, title, content, status, isNew = 1):
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()

    if status == 4: #In case it's not a text/html
        cursor.execute("UPDATE Links SET Status=4, Header=%s WHERE Id=%s", (content[0], link[0]))
        db.commit()
        db.close()
        return
    if status == 3: #In case of nothing found
        cursor.execute("UPDATE HiddenServices SET Status=%s WHERE Id=%s", (status, link[3]))
        cursor.execute("UPDATE Links SET Status=3 WHERE Id=%s", (link[0], ))
        db.commit()
        db.close()
        return
    #save content to file:
    filename = hashlib.md5(link[1]).hexdigest() + ".html"

    contentHash = hashlib.md5(content[1]).hexdigest()

    domain = link[1].replace("http://", "", 1)
    domain = domain.replace("https://", "", 1)
    splitted = domain.split("/")
    domain = splitted[0]
    path = ConfigLoader.resources + domain + "/" + filename

    if not os.path.exists(ConfigLoader.resources + domain):
        os.makedirs(ConfigLoader.resources + domain)

    with open(path, "w") as file:
        try:
            file.write(content[1].decode().encode('utf-8', 'ignore').strip())
        except UnicodeDecodeError:
            print  ("Unicode decode error while saving file. Moving on.")


    try:
        query = "UPDATE Links SET Title=%s, ResourcePath=%s, HTMLHash=%s, Status=%s, Header=%s WHERE Id=%s"
        cursor.execute(query, (title, path, contentHash, status, content[0], link[0]))
    except UnicodeDecodeError:
        print ("Unicode decode error while saving title. Moving on.")
        query = "UPDATE Links SET ResourcePath=%s, HTMLHash=%s, Status=%s, Header=%s WHERE Id=%s"
        cursor.execute(query, (path, contentHash, status, content[0], link[0]))


    cursor.execute("UPDATE HiddenServices SET LatestScan=%s WHERE Id=%s", (datetime.datetime.now(), link[3]))

    if isNew == 1:
        if (link[2]  == 1):
            cursor.execute("UPDATE HiddenServices SET Status=%s, Name=%s WHERE Id=%s", (status, title, link[3]))
        if status == 2 :
            cursor.execute("UPDATE HiddenServices SET LastSeenOnline=%s WHERE Id=%s", (datetime.datetime.now(), link[3]))

    db.commit()
    db.close()

def newLink(link):
    url = link[0]
    domainId = link[1]

    if ".onion" not in url:
        return
    if ".com/" in url or ".org/" in url:
        return
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()
    if url[len(url)-1] == '/':
        url = url[:-1]
    if domainId == 0:
        cursor.execute("SELECT * FROM Links WHERE Url=%s", (url, ) )
    else:
        cursor.execute("SELECT * FROM Links WHERE HiddenServiceId=%s AND Url=%s", (domainId, url ) )

    result = cursor.fetchall()
    if cursor.rowcount == 0:
        domainStringArray = url.lower().split(".onion")
        domainString = domainStringArray[0] + ".onion"
        if domainStringArray[1] is None or domainStringArray[1] == "/" or "index" in domainString[1] or domainStringArray[1] == "":
            isIndex = 1;
        else:
            isIndex = 0

        if domainId == 0:
            #checking if there is already a hs with that domain
            cursor.execute("SELECT Id FROM HiddenServices WHERE Url=%s", (domainString, ))
            hiddenService = cursor.fetchall()
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO HiddenServices (Url, Status) VALUES (%s, %s)",(domainString, 0))
                cursor.execute("SELECT Id FROM HiddenServices WHERE Url=%s AND Status=0", (domainString, ))
                result = cursor.fetchall()
                domainId = result[0][0]
            else:
                domainId = hiddenService[0][0]
        cursor.execute("INSERT INTO Links (Url, CreatedOn, HiddenServiceId, IsIndex, Status) \
                            VALUES (%s, %s, %s, %s, %s)", (url, datetime.datetime.now(), domainId, isIndex, 0))
    db.commit()
    db.close()

def getDomainFromUrl(domainUrl, linkUrl):
    db = MySQLdb.connect(host=ConfigLoader.host, user=ConfigLoader.user, passwd=ConfigLoader.password,
                         db=ConfigLoader.db, use_unicode=True,
                         charset="utf8")
    cursor = db.cursor()

    cursor.execute("SELECT Id FROM HiddenServices WHERE Url=%s", (domainUrl,))

    res = cursor.fetchall()

    now = datetime.datetime.now()

    if cursor.rowcount == 0: #new hidden service case
        cursor.execute("INSERT INTO HiddenServices (Url, Status, FirstScan, LatestScan) VALUES (%s, %s, %s, %s)", (domainUrl, 1, now, now))
        cursor.execute("SELECT Id FROM HiddenServices WHERE Status=1, Url=%s", (domainUrl,))
        res = cursor.fetchall()
        id = res[0][0]
    else: #in case it already exists
        id = res[0][0]
        cursor.execute("UPDATE HiddenServices SET Status=1 WHERE Id=%s", (id, ))

    cursor.execute("SELECT Id, Status FROM Links WHERE HiddenServiceId=%s AND Url=%s", (id, linkUrl))

    isIndex = 0
    if linkUrl == domainUrl:
        isIndex = 1

    if cursor.rowcount == 0:
        cursor.execute("INSERT INTO Links (Url, CreatedOn, HiddenServiceId, IsIndex, Status) VALUES (%s, %s, %s, %s, %s)",
                       (linkUrl, datetime.datetime.now(), id, isIndex, 0))
    else:
        res = cursor.fetchall()
        if res[0][1] != 0:
            cursor.execute("UPDATE Links SET Status=0 WHERE Id=%s", (res[0][0], ))

    db.commit()
    db.close()
    return id