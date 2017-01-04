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

def insertIntoMap(item, aLinkMap, state, aStateMap):
  allLinks = item.find_all('a')
  for aLink in allLinks:
    key = aLink.get_text()
    value = aLink.get('href')
    if key in aLinkMap:
      print ('In map already ' + key + ' ' + aLinkMap[key] + ' ' + value)
      continue
    aLinkMap[key] = value
    aStateMap[key] = state

#
#  ----------------
#

def extractCitiesCraiglistUrl(soup_obj, aLinkMap, aStateMap):
  aList = soup_obj.find_all('h4')
  for item in aList:
    insertIntoMap(item.find_next_sibling(), aLinkMap, item.get_text(), aStateMap)
  
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

aLinkMap = {}
aStateMap = {}

soup_obj = getParsedPage(pageUrl='https://www.craigslist.org/about/sites')
extractCitiesCraiglistUrl(soup_obj, aLinkMap, aStateMap)


for aKey in aLinkMap.keys():
  print (aKey + ' --> ' + aLinkMap[aKey])

for aKey in aStateMap.keys():
  print (aKey + ' --> ' + aStateMap[aKey])


