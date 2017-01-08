from bs4 import BeautifulSoup # For HTML parsing
import urllib2 # Website connections
import re # Regular expressions
import logging

class ToolBox:

  #
  #  ----------------
  #
  #def __init__(self):
    #print 'Hello from toolbox'
    
  #
  #  ----------------
  #
  def getParsedPage(self, pageUrl):
    
      try:
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
  
