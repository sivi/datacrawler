from bs4 import BeautifulSoup # For HTML parsing
import urllib2 # Website connections
import re # Regular expressions


class ToolBox:

  #
  #  ----------------
  #
  def __init__(self):
    #print 'Hello from toolbox'
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
  
