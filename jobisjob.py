from bs4 import BeautifulSoup # For HTML parsing
from toolbox import ToolBox 
import re # Regular expressions
import logging


class JobIsJob:

  todayDate = ''
  aJobTypeMap = {} # map of job type/job url entry: type --> url entry
  aJobList = [] # resulting list of job maps
  delayBetweenRequests = 0 #delay between subsequent calls in miliseconds
  totalcount = 0 # total count of available records (parsed from page)
  retrievedRecords = 0 # internal progress counter
  logger = logging.getLogger()
  
  #
  #  ----------------
  #
  def __init__(self, delayBetweenRequests = 1, loggingLevel = logging.WARNING):
    if len(self.aJobTypeMap) != 0:
      return
    self.logger.setLevel(loggingLevel)
    self.delayBetweenRequests = delayBetweenRequests
    toolBox = ToolBox()
    soup_obj = toolBox.getParsedPage('https://www.jobisjob.com/search?directUserSearch=true&whatInSearchBox=&whereInSearchBox=chicago%2C+il')
    self.extractJobTypeAndTodayDate(soup_obj)
    
  #
  #  ----------------
  #
  def extractJobTypeAndTodayDate(self, soup_obj):
    jobTypeInputs = soup_obj.find_all('input', attrs={"name": "jobType"})  
    self.insertStaticUrlIntoMap(jobTypeInputs, self.aJobTypeMap)
    
    dateCheckbox = soup_obj.find('input', title="Last 24 hours")
    self.todayDate = dateCheckbox.get('value')
  #
  #  ----------------
  #
  def insertStaticUrlIntoMap(self, jobTypeInputs, aMap):
    
    for aInput in jobTypeInputs:
      key = aInput.get('title')
      if key is None:
        continue
      value = aInput.get('value')
      if key in aMap:
        #print ('In map already ' + key + ' ' + aMap[key] + ' ' + value)
        continue
      aMap[key] = value

  #
  #  ---------------- END of static data bootstrap  ----------------
  #
    
  # today
  # https://www.jobisjob.com/search?directUserSearch=true&whatInSearchBox=admin&whereInSearchBox=chicago%2C+il#what=admin&where=chicago%2C+il&jobType=Full%20Time^Temporary&date=2017-01-18
  # 3 days
  # https://www.jobisjob.com/search?directUserSearch=true&whatInSearchBox=admin&whereInSearchBox=chicago%2C+il#what=admin&where=chicago%2C+il&jobType=Full%20Time&date=2017-01-16

  #
  #  ----------------
  #
  def fetchJobList(self, city, searchKeywords='', jobTypeList=None, countLimit=10):
    
    self.totalcount = 0 # reset counter od available records
    retrievedRecords = 0
    nextBatchUrl = '' # url to retrieve next batch jobs page 
    baseUrl = 'https://www.jobisjob.com'
    aUrl = baseUrl + '/search?directUserSearch=true' + \
           '&whatInSearchBox=' + searchKeywords +\
           '&whereInSearchBox=' + city + '&order=date' + \
           '&date=' + self.todayDate
              
    self.aJobList = [] # purge the list from previous results 
    
    filters = ''
    if not jobTypeList is None:
      for aFilter in jobTypeList:
        filters = filters + '^' + self.aJobTypeMap[aFilter]
      aUrl = aUrl + '&jobType=' + filters
    toolBox = ToolBox()
    try:
      while True:
        soup_obj = toolBox.getParsedPage(aUrl, self.delayBetweenRequests)
        jobList = soup_obj.find_all(class_="box_offer")
        self.parseJobList(jobList, baseUrl, city, searchKeywords, countLimit)

        # check if next batch available
        nextPageListEntry = None
        nextBatchDiv = soup_obj.find('div', attrs={"class": "paginator"})
        
        if not nextBatchDiv is None: 
          listEntries = nextBatchDiv.find_all('li')
          if not listEntries is None:
            nextPageListEntry = listEntries[len(listEntries)-1]
            if not nextPageListEntry.get('class') is None:
              nextPageListEntry = None
        if self.retrievedRecords == countLimit or \
           nextPageListEntry is None:
          break
        aLink = nextPageListEntry.find('a')  
        aUrl = aLink.get('href')
      return True
    except Exception, e:
      self.logger.error(' fetchJobList FAILED ' + str(e)+ '  ' + aUrl)
      import traceback
      self.logger.error(traceback.format_exc())
      
      return False
      
  #
  #  ----------------
  #
  def parseJobList(self, jobList, baseUrl, city, searchKeywords, countLimit):
    for jobItem in jobList:
      if self.retrievedRecords == countLimit:
        break
      jobLink = jobItem.find('a', itemprop="title")
      if jobLink is None:
        continue
      
      self.parseJobUrl(baseUrl, jobLink, jobItem, city, searchKeywords)
      self.retrievedRecords +=1

  #
  #  ----------------
  #
  def parseJobUrl(self, baseUrl, jobLink, jobBlock, city, searchKeywords):
     url = jobLink.get('href')
     jobTitle = jobLink.get_text()
     
     parsedMap = {}
     parsedMap['url'] = url
     parsedMap['jobTitle'] = jobTitle
     parsedMap['city'] = city
     parsedMap['searchKeywords'] = searchKeywords
     self.parseOtherMetaData(jobBlock, parsedMap)
     pageSucceeded = self.parseJobDetailsPage(parsedMap, url)
     if pageSucceeded:
       self.aJobList.append(parsedMap)
    
  #
  #  ----------------
  #
  def parseOtherMetaData(self, jobBlock, parsedMap):

    parsedMap['company'] = ''
    nameProp = jobBlock.find('a', class_="company-page")
    if nameProp is None:
      nameProp = jobBlock.find('span', itemprop="hiringOrganization")
    if not nameProp is None:
      parsedMap['company'] = nameProp.get_text()
    parsedMap['jobLocation'] = ''
    locationProp = jobBlock.find('span', itemprop='addressLocality')
    if not locationProp is None:
      parsedMap['jobLocation'] = jobBlock.find('span', itemprop='addressLocality').get_text()
    
    fromEntry = jobBlock.find('p', class_='from').get_text()
    parsedMap['from'] = fromEntry.split(':')[1].strip() 

  #
  #  ----------------
  #
  def parseJobDetailsPage(self, parsedMap, parsedUrl):
      
    url = parsedMap['url']
    toolBox = ToolBox()
    try:
      soup_obj = toolBox.getParsedPage(url, self.delayBetweenRequests)
    except:
      return False

    jobDetails = soup_obj.find('div', class_='job-offer')
    jobType = jobDetails.find('span', itemprop="employmentType")
    if not jobType is None:
      parsedMap['jobType'] = jobType.get_text()
    jobText = ''
    jobSummary = jobDetails.find('p', class_='description')
    for paragraph in jobSummary.strings:
      jobText += paragraph + '\n'
    parsedMap['jobPostingBody'] = jobText
    return True          
    
  #
  #  ----------------  DUMP of the collected data  ------------------
  #
  #
  #  ----------------
  #
  def dumpJobTypeMap(self):
    for aKey in self.aJobTypeMap.keys():
      print (aKey + ' --> ' + self.aJobTypeMap[aKey])
    
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
    self.dumpJobTypeMap()
    
  #
  #  ----------------
  #
#
#  ------------------------  END of CraigList class  ---------------
#

