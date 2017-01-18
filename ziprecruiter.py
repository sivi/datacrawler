from bs4 import BeautifulSoup # For HTML parsing
from toolbox import ToolBox 
import re # Regular expressions
import logging

#
# Usage note:
#
#    value of daysBeforeNow='' or daysBeforeNow=0 means "Posted anytime"
#

class ZipRecruiter:

  initiated = False
  aJobList = [] # resulting list of job maps
  delayBetweenRequests = 0 #delay between subsequent calls in miliseconds
  retrievedRecords = 0 # internal progress counter
  logger = logging.getLogger()
  
  #
  #  ----------------
  #
  def __init__(self, delayBetweenRequests = 1, loggingLevel = logging.WARNING):
    if self.initiated:
      return
    self.logger.setLevel(loggingLevel)
    self.delayBetweenRequests = delayBetweenRequests
    self.initiated = True

  #
  #  ---------------- END of static data bootstrap  ----------------
  #
    

  # https://www.ziprecruiter.com/candidate/search?search=contractor&location=Chicago%2C+il&radius=5&days=1

  #
  #  ----------------
  #
  def fetchJobList(self, city, radius=0, searchKeywords='', daysBeforeNow=1, \
                   countLimit=10):
    
    self.totalcount = 0 # reset counter od available records
    retrievedRecords = 0
    nextBatchUrl = '' # url to retrieve next batch jobs page 
    baseUrl = 'https://www.ziprecruiter.com'
    aUrl = baseUrl + '/candidate/search?search=' + searchKeywords + '&radius=' + str(radius) +\
              '&location=' + city + '&days=' + str(daysBeforeNow)
              
    self.aJobList = [] # purge the list from previous results 
    
    toolBox = ToolBox()
    try:
      while True:
        soup_obj = toolBox.getParsedPage(aUrl, self.delayBetweenRequests)
        jobList = soup_obj.find_all('article')
        self.parseJobList(jobList, baseUrl, city, searchKeywords, countLimit)

        # check if next batch available
        nextPageAnchor = soup_obj.find('a', id='pagination-button-next')
        if self.retrievedRecords == countLimit or \
           nextPageAnchor is None:
          break
        aUrl = baseUrl + nextPageAnchor.get('href')
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
      jobBlock = jobItem.find('h2', class_='job_title')
      # skip references to neighbouring areas which are different cities / servers
      if jobBlock is None:
        continue
      jobLink = jobBlock.find('a')
      if jobLink is None:
        continue
      
      self.parseJobUrl(baseUrl, jobLink, jobBlock, city, searchKeywords)
      self.retrievedRecords +=1

  #
  #  ----------------
  #
  def parseJobUrl(self, baseUrl, jobLink, jobBlock, city, searchKeywords):
     url = jobLink.get('href')
     jobTitle = jobLink.find(itemprop="title").get_text()
     
     parsedMap = {}
     parsedMap['url'] = baseUrl + url
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
    aParent = jobBlock.parent
    nameProp = aParent.find('span', itemprop='hiringOrganization')
    namePropSpan = nameProp.find('span')
    
    parsedMap['company'] = namePropSpan.get_text()
    namePropLink = namePropSpan.find('a') 
    if not namePropLink is None:
      parsedMap['company'] = namePropLink.get_text()
      
    locationProp = aParent.find('span',  itemprop='jobLocation')
    parsedMap['jobLocation'] = locationProp.find(itemprop='addressLocality').get_text()

    perksList = aParent.find_all('section', class_="perks_item")
    for perkItam in perksList:
      keySource = perkItam.find('h3')
      key = keySource.get_text()
      if not keySource.get('title') is None:
        key = keySource.get('title')
      valueList = perkItam.find('p', class_="data").strings
      value = ''
      for valueItem in valueList:
        value += valueItem + '\n'
      parsedMap[key] = value

  #
  #  ----------------
  #
  def parseJobDetailsPage(self, parsedMap, parsedUrl):
      
    parsedMap['jobPostingBody'] = ''
    return True
    url = parsedMap['url']
    toolBox = ToolBox()
    try:
      soup_obj = toolBox.getParsedPage(url, self.delayBetweenRequests)
    except:
      return True

    jobText = ''
    jobSummary = soup_obj.find('div', class_='jobDescriptionSection')
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
#  ------------------------  END of ZipRecruiter class  ---------------
#

