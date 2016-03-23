# google search results crawler 

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import shutil
from urllib import urlopen  
import csv
import urllib2, socket, time
import gzip, StringIO
import re, random, types
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
import json

browser = webdriver.Firefox()  


base_url = 'https://www.google.com'
results_per_page = 10
expect_num = 30
key=""
user_agents = list()

    
# results from the search engine
# basically include url, title,content
class SearchResult:
    def __init__(self):
        self.url= '' 
        self.title = '' 
        self.content = ''
        self.date='' 
        self.source=''
        self.id1=''
    
    def serialize(self):        
        return {
            'ID':self.id1,
            'url': self.url, 
            'title': self.title,
            'content': self.content,
            'date': self.date,
            'source': self.source
        }
    def getSource(self):
        return self.source

    def setSource(self, source):
        self.source = source
        
    def getURL(self):
        return self.url

    def setURL(self, url):
        self.url = url 

    def getTitle(self):
        return self.title
    
    def setId(self, id1):
        self.id1 = id1
        
    def setTitle(self, title):
        self.title = title
        
    def setDate(self, date):
        self.date = date
    
    def getDate(self):
        return self.date
        
    def getContent(self):
        return self.content

    def setContent(self, content):
        self.content = content

    def printIt(self, prefix = ''):
        print 'ASDFSDVSADF'
        print 'url\t->', self.url
        print 'title\t->', self.title
        print 'content\t->', self.content
        print 

    def writeFile(self, filename):
        file = open(filename, 'a')
        try:
            file.write('url:' + self.url+ '\n')
            file.write('title:' + self.title + '\n')
            file.write('content:' + self.content + '\n\n')
        except IOError, e:
            print 'file error:', e
        finally:
            file.close()



def getName(each_site):    
    pos=each_site.find('www.');
    if pos==-1:
        pos=each_site.find('.');
        each_site=each_site[pos+len('.'):]
    else:
        each_site=each_site[pos+len('www.'):]
    pos_end=each_site.find('.')
    each_site=each_site[:pos_end]
    return each_site
    
    
class GoogleAPI:
    def __init__(self):
        timeout = 50
        socket.setdefaulttimeout(timeout)

    def randomSleep(self):
        sleeptime =  random.randint(37, 67)
        print "Sleeping for :",sleeptime
        time.sleep(sleeptime)

    #extract the domain of a url
    def extractDomain(self, url):
        domain = ''
        pattern = re.compile(r'http[s]?://([^/]+)/', re.U | re.M)
        url_match = pattern.search(url)
        if(url_match and url_match.lastindex > 0):
            domain = url_match.group(1)
        return domain

    #extract a url from a link
    def extractUrl(self, href):
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]+)&', re.U | re.M)
        url_match = pattern.search(href)
        if(url_match and url_match.lastindex > 0):
            url = url_match.group(1)
        return url 

    # extract serach results list from downloaded html file
    def extractSearchResults(self, html,p, query,id1):
        number=0
        results = list()
        soup = BeautifulSoup(html)        
        div = soup.find('div', id  = 'search')        
        if (type(div) != types.NoneType):
            lis = div.findAll('div', {'class': 'g'})                    
            if(len(lis) > 0):               
                for li in lis:
                    result = SearchResult()
                    h3 = li.find('h3', {'class': 'r'})
                    if(type(h3) == types.NoneType):
                        continue
                    # extract domain and title from h3 object
                    link = h3.find('a')
                    if (type(link) == types.NoneType):
                        continue
                    url = link['href']                    
                    if(cmp(url, '') == 0):
                        continue
                    title = link.renderContents()
                    result.setURL(url)
                    try:                                             
                        number=number+1
                    except Exception, e:
                        print 'error in download:', e
                        self.randomSleep()
                        number=number+1
                        continue
                    result.setTitle(title)
                    span = li.find('div', {'class': 'st'})
                    if (type(span) != types.NoneType):
                        content = span.renderContents()
                        result.setContent(content)
                    date_span=li.find('span',{'class':'f'})  
                    if (type(date_span) != types.NoneType):
                        result.setDate(date_span.renderContents())
                    source_span=li.find('span',{'class':'_tQb'})  
                    if (type(source_span) != types.NoneType):
                        result.setSource(source_span.renderContents()) 
                    result.setId(id1)
                    id1=id1+1
                    print result.serialize()                          
                    results.append(result.serialize())
        return results,id1

    def search(self, query, pages,start_year,end_year):
        lang='en'
        search_results = list()
        squery=query
        query = urllib2.quote(query)        
        results_per_page=10     
        id1=1            
        for p in range(0, pages):
            start = p * results_per_page 
            url='https://www.google.com/search?cf=all&hl=en&pz=1&ned=us&tbm=nws&gl=us&as_q=solar%20energy&as_occt=any&as_drrb=b&as_mindate=01/01/'+start_year+'&as_maxdate=01/01/'+end_year+'&tbs=cdr:1,cd_min:01/01/'+start_year+',cd_max:01/01/'+end_year+'&authuser=0&start='+str(p)                  
            print url
            retry = 2
            while(retry > 0):
                try:                   
                    browser.get(url) 
                    html= browser.page_source
                    self.randomSleep()                   
                    results,id1 = self.extractSearchResults(html,p,query,id1)                    
                    search_results.extend(results)
                    break;                    
                except urllib2.URLError,e:                   
                    print 'url error:', e                    
                    retry = retry - 1
                    print "Retry value:",retry
                    self.randomSleep()                    
                    continue 
                except Exception, e:
                    print 'error:', e
                    retry = retry - 1
                    self.randomSleep()
                    continue
            if retry<=0:
                break
        return search_results  
    

def crawler(key,start_year,end_year):                     
    # Create a GoogleAPI instance
    api = GoogleAPI()        
    query=key
    if len(sys.argv)>3:
        tot_page=int(sys.argv[3])
    else:
        tot_page=10
    results1 = api.search(query,tot_page,start_year,end_year)    
    outputfile=open("data2.txt","w")
    json.dump(results1, outputfile,indent=4, sort_keys=True)                 

if __name__ == '__main__':
    word="solar energy"
    if len(sys.argv)>=3:
        start_year=sys.argv[1]
        end_year=sys.argv[2]
        crawler(word,start_year,end_year)
    else:
        print "Usage: python googlenewscrawler.py <start year> <end year> <num_pages>"                   
