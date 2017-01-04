from bs4 import BeautifulSoup # For HTML parsing
import urllib2 # Website connections
import re # Regular expressions

#
#  ----------------
#

def getParsedPage(pageUrl):
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

#
#  ----------------
#

def extractCitiesCraiglistUrl(soup_obj):
  aList = soup_obj.find_all('ul', class_='acitem')
  for item in aList:
    allLinks = item.find_all('a')
    for aLink in allLinks:
      print (aLink.get('href') + ' --> ' + aLink.get_text())

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
soup_obj = getParsedPage(pageUrl='http://sfbay.craigslist.org')
extractCitiesCraiglistUrl(soup_obj)

