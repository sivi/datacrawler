from bs4 import BeautifulSoup # For HTML parsing
from toolbox import ToolBox 
import re # Regular expressions
import logging


class CraigList:

  aLinkMap = {}   # map of city/url links: city --> url
  aStateMap = {}  # map of city/state:  city --> state
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
    soup_obj = toolBox.getParsedPage('https://www.craigslist.org/about/sites')
    self.extractCitiesCraiglistUrl(soup_obj)
    soup_obj = toolBox.getParsedPage('https://sfbay.craigslist.org/')
    self.extractJobsCraiglistUrl(soup_obj)
    soup_obj = toolBox.getParsedPage('https://sfbay.craigslist.org/search/eng')
    self.extractRefineFiltersCraiglistUrl(soup_obj)
    
    
  #
  #  ----------------
  #
  def extractCitiesCraiglistUrl(self, soup_obj):
    aList = soup_obj.find_all('h4')
    for item in aList:
      self.insertCityIntoMap(item.find_next_sibling(), item.get_text())
    
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
  def extractRefineFiltersCraiglistUrl(self, soup_obj):
    aList = soup_obj.find_all(class_='searchgroup')
    for item in aList:
      self.insertRefineFilterUrlIntoMap(item)

  #
  #  ----------------
  #
  def insertCityIntoMap(self, item, state):
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
  def insertRefineFilterUrlIntoMap(self, item):
    ulList = item.find_all('ul')
    for ulItem in ulList:
      if not self.classNot_nearbyAreas(ulItem.attrs):
       continue
      checkBoxItemList = ulItem.find_all('input', type='checkbox')
      for checkBoxItem in checkBoxItemList:
        self.insertIntoFilterUrlMap(checkBoxItem)
        
    if len(ulList) > 0:
      return
      
    checkBoxItemList = item.find_all('input', type='checkbox')
    for checkBoxItem in checkBoxItemList:
      self.insertIntoFilterUrlMap(checkBoxItem)
    
     

  #
  #  ----------------
  #
  def classNot_nearbyAreas(self, attrs):
    return attrs is None or \
      attrs.get('class') is None or \
      not 'nearbyAreas' in attrs.get('class')
    
  #
  #  ----------------
  #
  def insertIntoFilterUrlMap(self, checkBoxEntry):
    aName = checkBoxEntry.get('name')
    aValue = checkBoxEntry.get('value')
    aKey = checkBoxEntry.parent.get_text().strip()
    self.aJobFilterMap[aKey] = '&' + aName + '=' + aValue
  
  #
  #  ---------------- END of static data bootstrap  ----------------
  #
    
  #
  #  ----------------
  #
  def fetchJobList(self, city, jobCategory, filterList=None, countLimit=10):
    
    self.totalcount = 0 # reset counter od available records
    retrievedRecords = 0
    nextBatchUrl = '' # url to retrieve next batch jobs page 
    baseUrl = self.aLinkMap[city]
    assert( baseUrl != None)
    jobUrl = self.aJobCategoryMap[jobCategory]
    assert( jobUrl != None)
    
    self.aJobList = [] # purge the list from previous results 
    
    if not baseUrl.startswith('http'):
      baseUrl = 'https:' + baseUrl
    if baseUrl.endswith('/') and jobUrl.startswith('/'):
      baseUrl = baseUrl[0:len(baseUrl)-1]
    aUrl = baseUrl + jobUrl
    if not filterList is None:
      filters = ''
      for aFilter in filterList:
        filters = filters + self.aJobFilterMap[aFilter]
      filters = '?' + filters[1:]
      aUrl = aUrl + filters
    toolBox = ToolBox()
    try:
      while True:
        self.logger.info('retrieving ' + aUrl)
        soup_obj = toolBox.getParsedPage(aUrl, self.delayBetweenRequests)
        jobList = soup_obj.find_all(class_="result-row")
        totalcount = soup_obj.find('span', class_='totalcount')
        if not totalcount is None:
           self.totalcount = totalcount.get_text()
        self.parseJobList(jobList, baseUrl, city, jobCategory, countLimit)

        # check if next batch available
        nextBatchUrl = soup_obj.find('link', rel='next') 
        if self.retrievedRecords == countLimit or \
           nextBatchUrl is None:
          break
        aUrl = nextBatchUrl.get('href')
      return True
    except Exception, e:
      self.logger.error(' fetchJobList FAILED ' + str(e)+ '  ' + aUrl)
      import traceback
      self.logger.error(traceback.format_exc())
      
      return False
      
  #
  #  ----------------
  #
  def parseJobList(self, jobList, baseUrl, city, jobCategory, countLimit=10):
    loopCount = 0
    for jobItem in jobList:
      if self.retrievedRecords == countLimit:
        break
      jobUrl = jobItem.find(class_="result-title hdrlnk")
      # skip references to neighbouring areas which are different cities / servers
      if jobUrl is None or \
         jobUrl.get('href').startswith('//'): 
        continue
      # neighbourhood within city domain
      neighbourhoodItem = jobItem.find(class_="result-hood")
      if neighbourhoodItem == None:
        neighbourhood = ''
      else:
        neighbourhood = neighbourhoodItem.get_text()
      
      self.parseJobUrl(baseUrl, jobUrl, city, neighbourhood, jobCategory)
      self.retrievedRecords +=1

  #
  #  ----------------
  #
  def parseJobUrl(self, baseUrl, jobUrl, city, neighbourhood, jobCategory):
     url = jobUrl.get('href')
     jobTitle = jobUrl.get_text()
     
     parsedMap = {}
     parsedMap['url'] = baseUrl + url
     parsedMap['jobTitle'] = jobTitle
     parsedMap['city'] = city
     parsedMap['neighbourhood'] = neighbourhood 
     parsedMap['jobCategory'] = jobCategory
     pageSucceeded = self.parseJobDetailsPage(parsedMap)
     if pageSucceeded:
       self.aJobList.append(parsedMap)

  #
  #  ----------------
  #
  def parseJobDetailsPage(self, parsedMap):
    url = parsedMap['url']
    toolBox = ToolBox()
    try:
      soup_obj = toolBox.getParsedPage(url, self.delayBetweenRequests)
    except:
      return False
    postDateEntry = soup_obj.find('p', id='display-date')
    parsedMap['postingDate'] = postDateEntry.find('time').get('datetime')
    jobPostingBody = soup_obj.find('section', id='postingbody')
    jobText = ''
    for paragraph in jobPostingBody.strings: 
      jobText += paragraph + '\n' 
    parsedMap['jobPostingBody'] = jobText 
    jobAttributes = soup_obj.find(class_='mapAndAttrs')
    if not jobAttributes == None:
      attributeList = jobAttributes.find_all('span')
      if not attributeList == None and len(attributeList) > 0 :
        compensationEntry = attributeList[0].get_text()
        compensationList = compensationEntry.split(':', 1)
        parsedMap['compensation'] = compensationList[1] 
        if len(attributeList) > 1 :
          jobTypeEntry = attributeList[1].get_text()
          jobTypeList = jobTypeEntry.split(':', 1)
          parsedMap['jobType'] = jobTypeList[1] 
    return True          
    
  #
  #  ----------------  DUMP of the collected data  ------------------
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
#
#  ------------------------  END of CraigList class  ---------------
#

