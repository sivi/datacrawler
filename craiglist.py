from bs4 import BeautifulSoup # For HTML parsing
from toolbox import ToolBox 
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
    toolBox = ToolBox()
    soup_obj = toolBox.getParsedPage('https://www.craigslist.org/about/sites')
    self.extractCitiesCraiglistUrl(soup_obj)
    
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

