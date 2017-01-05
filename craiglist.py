from bs4 import BeautifulSoup # For HTML parsing
import urllib2 # Website connections
import re # Regular expressions


class CraigList:

  aLinkMap = {}   # map of city/url links: city --> url
  aStateMap = {}  # map of city/state:  city --> state
  aJobCategoryMap = {} # map of job category/job url entry: category --> url entry
  #
  #  ----------------
  #
  def __init__(self):
    if len(self.aLinkMap) != 0:
      return
      
    soup_obj = self.getParsedPage('https://www.craigslist.org/about/sites')
    self.extractCitiesCraiglistUrl(soup_obj)
    
  #
  #  ----------------
  #
  def getParsedPage(self, pageUrl):
      try:
          response = urllib2.urlopen(pageUrl) # Connect to the job posting
          site = response.read() # Read the job posting
      except urllib2.HTTPError, e:
        logging.error('HTTPError = ' + str(e.code)+ '  ' + website)
      except urllib2.URLError, e:
        logging.error('URLError = ' + str(e.reason)+ '  ' + website)
      except httplib.HTTPException, e:
        logging.error('HTTPException' + str(e)+ '  ' + website)
      except Exception:
        import traceback
        logging.error('generic exception: ' + traceback.format_exc())
      except: 
        print "ERROR"
        return None  # Need this in case the website isn't there anymore or some other weird connection problem 
  
      soup_obj = BeautifulSoup(site, 'lxml') # Get the html from the site
      
      if len(soup_obj) == 0: # In case the default parser lxml doesn't work, try another one
          soup_obj = BeautifulSoup(site, 'html5lib')
  
      return soup_obj
  
  #
  #  ----------------
  #
  def insertIntoMap(self, item, state):
    allLinks = item.find_all('a')
    for aLink in allLinks:
      key = aLink.get_text()
      value = aLink.get('href')
      if key in self.aLinkMap:
        print ('In map already ' + key + ' ' + self.aLinkMap[key] + ' ' + value)
        continue
      self.aLinkMap[key] = value
      self.aStateMap[key] = state
  
  #
  #  ----------------
  #
  def extractCitiesCraiglistUrl(self, soup_obj):
    aList = soup_obj.find_all('h4')
    for item in aList:
      self.insertIntoMap(item.find_next_sibling(), item.get_text())
    
  #
  #  ----------------
  #
  def dumpMaps(self):
    
    for aKey in self.aLinkMap.keys():
      print (aKey + ' --> ' + self.aLinkMap[aKey])
    
    for aKey in self.aStateMap.keys():
      print (aKey + ' --> ' + self.aStateMap[aKey])
  
  #
  #  ----------------
  #
  def craiglist(country, state=None, city=None, filters=None):
    if filters == None :
      print '''Filters are following:
        jobtype \n
        aaaa \n
        bbb'''
      return
    
    print 'OK'
  

  #
  #  ----------------
  #

  #craiglist(country='US', state='CA', city='San Francisco', filters=None)
test = CraigList()
#test.dumpMaps()  
print ('link map lenght ' + str(len(test.aLinkMap)))

