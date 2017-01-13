from bs4 import BeautifulSoup # For HTML parsing
from toolbox import ToolBox 
import re # Regular expressions
import logging


class Indeed:

  aLinkMap = {}   # map of city/url links: city --> url
  aStateMap = {}  # map of state/state url:  state --> state url
  aJobTypeMap = {} # map of job type/job url entry: type --> url entry
  aJobExperienceLevelMap = {} # map of experience level / level url: level --> url entry
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
    soup_obj = toolBox.getParsedPage('https://www.indeed.com/q-business-l-chicago.il-jobs.html')
    self.extractJobTypeAndExperienceLevelIndeedUrl(soup_obj)
    
  #
  #  ----------------
  #
  def extractJobTypeAndExperienceLevelIndeedUrl(self, soup_obj):
    jobTypeDiv = soup_obj.find('div', id='JOB_TYPE_rbo')  
    self.insertStaticUrlIntoMap(jobTypeDiv, self.aJobTypeMap)
    
    experienceLevelDiv = soup_obj.find('div', id='EXP_LVL_rbo')
    self.insertStaticUrlIntoMap(experienceLevelDiv, self.aJobExperienceLevelMap)

  #
  #  ----------------
  #
  def insertStaticUrlIntoMap(self, item, aMap):
    allLinks = item.find_all('a')
    for aLink in allLinks:
      key = aLink.get_text()
      if key.strip() == '':
        continue
      value = aLink.get('href').split('&')[2]
      if key in aMap:
        print ('In map already ' + key + ' ' + aMap[key] + ' ' + value)
        continue
      aMap[key] = value

  #
  #  ---------------- END of static data bootstrap  ----------------
  #
    

  #https://www.indeed.com/jobs?q=business+$95,000&l=Chicago,+IL&jt=internship&explvl=mid_level
  #https://www.indeed.com/jobs?q=business&l=chicago.il&fromage=0&start=410

  #
  #  ----------------
  #
  def fetchJobList(self, city, radius=0, jobCategory='', daysBeforeToday=0, \
                   jobTypeList=None, jobExperienceLevelList=None, countLimit=10):
    
    self.totalcount = 0 # reset counter od available records
    retrievedRecords = 0
    nextBatchUrl = '' # url to retrieve next batch jobs page 
    baseUrl = 'https://www.indeed.com'
    aUrl = baseUrl + '/jobs?q=' + jobCategory + '&radius=' + str(radius) +\
              '&l=' + city + '&fromage=' + str(daysBeforeToday) + '&sort=date'
              
    self.aJobList = [] # purge the list from previous results 
    
    filters = ''
    if not jobTypeList is None:
      for aFilter in jobTypeList:
        filters = filters + '&' + self.aJobTypeMap[aFilter]
    if not jobExperienceLevelList is None:
      for aFilter in jobExperienceLevelList:
        filters = filters + '&' + self.aJobExperienceLevelMap[aFilter]
    aUrl = aUrl + filters
    toolBox = ToolBox()
    try:
      while True:
        soup_obj = toolBox.getParsedPage(aUrl, self.delayBetweenRequests)
        jobList = soup_obj.find_all(class_="result")
        totalcount = soup_obj.find('div', id='searchCount')
        if not totalcount is None:
           self.totalcount = totalcount.get_text().split('of')[1]
        self.parseJobList(jobList, baseUrl, city, jobCategory, countLimit)

        # check if next batch available
        nextPageSpan = None
        nextBatchDiv = soup_obj.find('div', class_='pagination')
        if not nextBatchDiv is None: 
          links = nextBatchDiv.find_all('a')
          nextPageSpan = links[len(links)-1].find('span', class_='np')
        if self.retrievedRecords == countLimit or \
           nextPageSpan is None:
          break
        links = nextBatchDiv.find_all('a')  
        aUrl = baseUrl + links[len(links)-1].get('href')
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
    for jobItem in jobList:
      if self.retrievedRecords == countLimit:
        break
      jobBlock = jobItem.find('h2', class_='jobtitle')
      # skip references to neighbouring areas which are different cities / servers
      if jobBlock is None:
        continue
      jobLink = jobBlock.find('a')
      if jobLink is None:
        continue
      
      self.parseJobUrl(baseUrl, jobLink, city, jobCategory)
      self.retrievedRecords +=1

  #
  #  ----------------
  #
  def parseJobUrl(self, baseUrl, jobLink, city, jobCategory):
     url = jobLink.get('href')
     jobTitle = jobLink.get('title')
     
     parsedMap = {}
     parsedMap['url'] = baseUrl + url
     parsedMap['jobTitle'] = jobTitle
     parsedMap['city'] = city
     parsedMap['jobCategory'] = jobCategory
     pageSucceeded = self.parseJobDetailsPage(parsedMap, url)
     if pageSucceeded:
       self.aJobList.append(parsedMap)

  #
  #  ----------------
  #
  def parseJobDetailsPage(self, parsedMap, parsedUrl):
    if parsedUrl.startswith('/rc/clk?'):
      return True
      
    url = parsedMap['url']
    toolBox = ToolBox()
    try:
      soup_obj = toolBox.getParsedPage(url, self.delayBetweenRequests)
    except:
      return False

    jobText = ''
    jobSummary = soup_obj.find('span', id='job_summary')
    for paragraph in jobSummary.strings:
      jobText += paragraph + '\n'
    parsedMap['jobPostingBody'] = jobText
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
  def dumpStateUrlMap(self):
    for aKey in self.aStateMap.keys():
      print (aKey + ' --> ' + self.aStateMap[aKey])
    
  #
  #  ----------------
  #
  def dumpJobTypeMap(self):
    for aKey in self.aJobTypeMap.keys():
      print (aKey + ' --> ' + self.aJobTypeMap[aKey])
    
  #
  #  ----------------
  #
  def dumpJobExperienceLevelMap(self):
    for aKey in self.aJobExperienceLevelMap.keys():
      print (aKey + ' --> ' + self.aJobExperienceLevelMap[aKey])
    
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
    self.dumpJobExperienceLevelMap()
    self.dumpJobFilterMap()
    
  #
  #  ----------------
  #
#
#  ------------------------  END of CraigList class  ---------------
#

