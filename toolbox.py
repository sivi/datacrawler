from bs4 import BeautifulSoup # For HTML parsing
import urllib2 # Website connections
import re # Regular expressions
import logging
import time

class ToolBox:

  #
  #  ----------------
  #
  #def __init__(self):
    #print 'Hello from toolbox'
    
  #
  #  ----------------
  #
  def getParsedPage(self, pageUrl, delayBetweenRequests=1):
    
      try:
          time.sleep(delayBetweenRequests * 1.0)
          logging.info(pageUrl)
          response = urllib2.urlopen(pageUrl) # Connect to the job posting
          site = response.read() # Read the job posting
      except urllib2.HTTPError, e:
        logging.error('HTTPError = ' + str(e.code)+ '  ' + pageUrl)
        raise Exception, 'Error reading url'
      except urllib2.URLError, e:
        logging.error('URLError = ' + str(e.reason)+ '  ' + pageUrl)
        raise Exception, 'Error reading url'
      except httplib.HTTPException, e:
        logging.error('HTTPException ' + str(e)+ '  ' + pageUrl)
        raise Exception, 'Error reading url'
      except Exception:
        import traceback
        logging.error('generic exception: ' + traceback.format_exc())
        raise Exception, 'Error reading url'
      except: 
        logging.error('ERROR READING ' + pageUrl)
        raise Exception, 'Error reading url '
  
      soup_obj = BeautifulSoup(site, 'lxml') # Get the html from the site
      
      if len(soup_obj) == 0: # In case the default parser lxml doesn't work, try another one
          soup_obj = BeautifulSoup(site, 'html5lib')
  
      return soup_obj
  
  #
  #  ----------------
  #
  @staticmethod
  def prepareURLParameter(parameterValue):
    aValue = parameterValue.replace(' ', '+')
    aValue = aValue.replace(',', '%2C')
    return aValue
     
  #
  #  ----------------
  #
  @staticmethod
  def prepareURLParameterList(aList):
    if aList is None:
      return
    i = 0
    while i < len(aList):
      aValue = aList[i]
      aValue = aValue.replace(' ', '+')
      aValue = aValue.replace(',', '%2C')
      aList[i] = aValue
      i += 1
    return
