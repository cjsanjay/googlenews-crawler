import sys
import os
import csv
import urllib2, socket, time
import gzip, StringIO
import re, random, types
from bs4 import BeautifulSoup
from datetime import datetime
import json
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def extractData(url,title):
    data=""
    req=urllib2.Request(url)
    response=urllib2.urlopen(req)
    html_data=response.read()    
    soup=BeautifulSoup(html_data)
    [s.extract() for s in soup('script')]
    d=re.compile(r'.*%s.*' % title)
    last_elem=0
    for elem in soup(text=d):
        last_elem=elem
    if last_elem!=0:    
        p1=last_elem.parent 
        try1=1   
        while len(data)<1000:    
            parent=p1.parent
            p1=parent
            data=""        
            for each_child in parent.findChildren():
                data+=each_child.get_text().strip().replace('\n','') 
            print try1
            try1+=1             
    else:
        data=""  
        for each_child in soup.body.findChildren():
            data+=each_child.get_text().strip().replace('\n','')                    
    return data


def readData(input_file):
    data=json.loads(input_file.read())
    for each_r in data:
        if each_r['ID']>=1:
            s = MLStripper()
            s.feed(each_r['title'])
            title =s.get_data()            
            val=len(title)/2
            val=val/2
            print title[:-val]
            article_data=extractData(each_r['url'],title)
            print 'url',each_r['url']         
            print article_data
            print '##############################################'
            raw_input()      
if __name__=="__main__":
    if sys.argv>=2:
        input_file=open(sys.argv[1],"r")
        readData(input_file)
    else:
        print "Usage: python extractnew.py <data_file_location>"    
    
