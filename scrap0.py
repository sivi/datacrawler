from bs4 import BeautifulSoup # For HTML parsing
import urllib2 # Website connections
import re # Regular expressions
from time import sleep # To prevent overwhelming the server between connections
from collections import Counter # Keep track of our term counts
from nltk.corpus import stopwords # Filter out stopwords, such as 'the', 'or', 'and'
import pandas as pd # For converting results to a dataframe and bar chart plots 
#matplotlib inline
import logging



#Now create our first website parsing function.

def text_cleaner(website=None):
    '''
    This function just cleans up the raw html so that I can look at it.
    Inputs: a URL to investigate
    Outputs: Cleaned text only
    '''

    if website == None or len(website) == 0:
      print 'URL missing'
      return '' 

    try:
        response = urllib2.urlopen(website) # Connect to the job posting
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
      return   # Need this in case the website isn't there anymore or some other weird connection problem 

    soup_obj = BeautifulSoup(site, 'lxml') # Get the html from the site
    
    if len(soup_obj) == 0: # In case the default parser lxml doesn't work, try another one
        soup_obj = BeautifulSoup(site, 'html5lib')

    for script in soup_obj(["script", "style"]):
        script.extract() # Remove these two elements from the BS4 object
    
    text = soup_obj.get_text() # Get the text from this

    lines = (line.strip() for line in text.splitlines()) # break into lines
    
    chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break multi-headlines into a line each

    text = ''.join(chunk for chunk in chunks if chunk).encode('utf-8') # Get rid of all blank lines and ends of line
    
    # Now clean out all of the unicode junk (this line works great!!!)
    
    try:
        text = text.decode('unicode_escape').encode('ascii', 'ignore') # Need this as some websites aren't formatted
    except:                                                            # in a way that this works, can occasionally throw
        return                                                         # an exception
    
    text = re.sub("[^a-zA-Z+3]"," ", text)  # Now get rid of any terms that aren't words (include 3 for d3.js)
                                             # Also include + for C++
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text) # Fix spacing issue from merged words
    
    text = text.lower().split()  # Go to lower case and split them apart
    
    stop_words = set(stopwords.words("english")) # Filter out any stop words
    text = [w for w in text if not w in stop_words]
    
    text = list(set(text)) # Last, just get the set of these. Ignore counts (we are just looking at whether a term existed
                           # or not on the website)
    
    return text

# https://en.wikipedia.org/wiki/List_of_employment_websites

#sample = text_cleaner('http://www.indeed.com/viewjob?jk=5505e59f8e5a32a4&q=%22data+scientist%22&tk=19ftfgsmj19ti0l3&from=web&advn=1855944161169178&sjdu=QwrRXKrqZ3CNX5W-O9jEvWC1RT2wMYkGnZrqGdrncbKqQ7uwTLXzT1_ME9WQ4M-7om7mrHAlvyJT8cA_14IV5w&pub=pub-indeed')


try:
  sample = text_cleaner('https://www.linkup.com/')
  print sample[:20]
except:
  print 'FAILED'

try:
  sample = text_cleaner('https://www.linkedin.com/')
  print sample[:20]
except:
  print 'FAILED'
  
try:
  sample = text_cleaner('https://www.monster.com/')
  print sample[:20]
except:
  print 'FAILED'
  


