from bs4 import BeautifulSoup # For HTML parsing
from toolbox import ToolBox 
import re # Regular expressions


class CraigList:

  aLinkMap = {}   # map of city/url links: city --> url
  aStateMap = {}  # map of city/state:  city --> state
  aJobCategoryMap = {} # map of job category/job url entry: category --> url entry
  aJobList = [] # resulting list of job maps

  #
  #  ----------------
  #
  def __init__(self):
    if len(self.aLinkMap) != 0:
      return
    toolBox = ToolBox()
    soup_obj = toolBox.getParsedPage('https://www.craigslist.org/about/sites')
    self.extractCitiesCraiglistUrl(soup_obj)
    soup_obj = toolBox.getParsedPage('https://sfbay.craigslist.org/')
    self.extractJobsCraiglistUrl(soup_obj)
    
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
  def insertJobUrlIntoMap(self, item):
    allLinks = item.find_all('a')
    for aLink in allLinks:
      key = aLink.get_text()
      value = aLink.get('href')
      if key in self.aJobCategoryMap:
        print ('In map already ' + key + ' ' + self.aJobCategoryMap[key] + ' ' + value)
        continue
      self.aJobCategoryMap[key] = value
  
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
  def extractJobsCraiglistUrl(self, soup_obj):
    aList = soup_obj.find_all(id='jjj')
    for item in aList:
      self.insertJobUrlIntoMap(item)
    
  #
  #  ----------------
  #
  def parseJobUrl(self, baseUrl, jobUrl):
     url = jobUrl.get('href')
     jobTitle = jobUrl.get_text()
     
     parsedMap = {}
     parsedMap['url'] = baseUrl + url
     parsedMap['jobTitle'] = jobTitle
     self.aJobList.append(parsedMap)
  #
  #  ----------------
  #
  def fetchJobList(self, city, jobCategory, countLimit=10):
    baseUrl = self.aLinkMap[city]
    assert( baseUrl != None)
    jobUrl = self.aJobCategoryMap[jobCategory]
    assert( jobUrl != None)
    
    self.aJobList = [] # purge the list from previous results 
    
    if not baseUrl.startswith('http'):
      baseUrl = 'https:' + baseUrl
    if baseUrl.endswith('/') and jobUrl.startswith('/'):
      baseUrl = baseUrl[0:len(baseUrl)-1]
   
    toolBox = ToolBox()
    soup_obj = toolBox.getParsedPage(baseUrl + jobUrl)
    jobList = soup_obj.find_all(class_="result-row")
    
    loopCount = 0
    for jobItem in jobList:
      if loopCount == countLimit:
        break
      jobUrl = jobItem.find(class_="result-title hdrlnk")
      self.parseJobUrl(baseUrl, jobUrl)
      loopCount +=1

  #
  #  ----------------
  #
  def dumpCityUrlMap(self):
    for aKey in self.aLinkMap.keys():
      print (aKey + ' --> ' + self.aLinkMap[aKey])
    
  #
  #  ----------------
  #
  def dumpCityStateMap(self):
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
  def dumpJobList(self):
    for item in self.aJobList:
      print (item)
    
  #
  #  ----------------
  #
  def dumpMaps(self):
    self.dumpCityUrlMap()
    self.dumpCityStateMap()
    self.dumpJobCategoryUrlMap()
  
  #
  #  ----------------
  #
  def craiglist(self, country, state=None, city=None, filters=None):
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
#test.dumpCityUrlMap()  
#test.dumpJobCategoryUrlMap()  

print ('link map lenght ' + str(len(test.aLinkMap)))
test.fetchJobList(city='san francisco bay area', jobCategory='jobs', countLimit=5)
test.dumpJobList()
