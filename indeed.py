from bs4 import BeautifulSoup # For HTML parsing
from toolbox import ToolBox 
import re # Regular expressions
import logging


class Indeed:

  aLinkMap = {}   # map of city/url links: city --> url
  aStateMap = {}  # map of state/state url:  state --> state url
  aJobCategoryMap = {} # map of job category/job url entry: category --> url entry
  aJobFilterMap = {} # map of job filter / job filter url: filter --> url entry
  aJobList = [] # resulting list of job maps
  delayBetweenRequests = 0 #delay between subsequent calls in miliseconds
  totalcount = 0 # total count of available records (parsed from page)
  retrievedRecords = 0 # internal progress counter
  logger = logging.getLogger()
  
  #
  #  ----------------
  #
  def __init__(self, delayBetweenRequests = 1, loggingLevel = logging.WARNING):
    if len(self.aLinkMap) != 0:
      return
    self.logger.setLevel(loggingLevel)
    self.delayBetweenRequests = delayBetweenRequests
    toolBox = ToolBox()
    soup_obj = toolBox.getParsedPage('https://www.indeed.com/find-jobs.jsp')
    self.extractStateAndJobsCategoriesIndeedUrl(soup_obj)
    
    #self.extractCitiesCraiglistUrl(soup_obj)
    #soup_obj = toolBox.getParsedPage('https://sfbay.craigslist.org/')
    #soup_obj = toolBox.getParsedPage('https://sfbay.craigslist.org/search/eng')
    #self.extractRefineFiltersCraiglistUrl(soup_obj)

  #
  #  ----------------
  #
  def extractStateAndJobsCategoriesIndeedUrl(self, soup_obj):
    tableEntry = soup_obj.find('table', id='states')
    self.insertStaticUrlIntoMap(tableEntry, self.aStateMap)
    tableEntry = soup_obj.find('table', id='categories')
    self.insertStaticUrlIntoMap(tableEntry, self.aJobCategoryMap)
    

  #
  #  ----------------
  #
  def insertStaticUrlIntoMap(self, item, aMap):
    allLinks = item.find_all('a')
    for aLink in allLinks:
      key = aLink.get_text()
      if key.strip() == '':
        continue
      value = aLink.get('href').split('?')[1]
      if key in aMap:
        print ('In map already ' + key + ' ' + aMap[key] + ' ' + value)
        continue
      aMap[key] = value


  #https://www.indeed.com/jobs?q=business+$95,000&l=Chicago,+IL&jt=internship&explvl=mid_level

  #
  #  ----------------  DUMP of the collected data  ------------------
  #
  def dumpCityUrlMap(self):
    for aKey in self.aLinkMap.keys():
      print (aKey + ' --> ' + self.aLinkMap[aKey])
    
  #
  #  ----------------
  #
  def dumpStateUrlMap(self):
    for aKey in self.aStateMap.keys():
      print (aKey + ' --> ' + self.aStateMap[aKey])
    
  #
  #  ----------------
  #
  def dumpJobCategoryUrlMap(self):
    for aKey in self.aJobCategoryMap.keys():
      print (aKey + ' --> ' + self.aJobCategoryMap[aKey])
    
  #
  #  ----------------
  #
  def dumpJobFilterMap(self):
    for aKey in self.aJobFilterMap.keys():
      print (aKey + ' --> ' + self.aJobFilterMap[aKey])
    
  #
  #  ----------------
  #
  def dumpJobList(self):
    for item in self.aJobList:
      print (item)
      print '\n'
    
  #
  #  ----------------
  #
  def dumpMaps(self):
    self.dumpCityUrlMap()
    self.dumpCityStateMap()
    self.dumpJobCategoryUrlMap()
    self.dumpJobFilterMap()
    
  #
  #  ----------------
  #
#
#  ------------------------  END of CraigList class  ---------------
#

