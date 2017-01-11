from craiglist import CraigList
from indeed import Indeed
import logging

#craiglist(country='US', state='CA', city='San Francisco', filters=None)
#test = CraigList(delayBetweenRequests=10, loggingLevel=logging.INFO)
#test = CraigList(delayBetweenRequests=10, loggingLevel=logging.WARNING)
#test.dumpCityUrlMap()  
#test.dumpJobCategoryUrlMap()  
#test.dumpJobFilterMap()

#print ('link map lenght ' + str(len(test.aLinkMap)))
#success = test.fetchJobList(city='san francisco bay area', jobCategory='jobs', filterList=['full-time','contract'], countLimit=5)
#success = test.fetchJobList(city='san francisco bay area', jobCategory='jobs', filterList=['internship'], countLimit=500)
#success = test.fetchJobList(city='chicago', jobCategory='business / mgmt', filterList=['full-time','posted today'], countLimit=3)
#if success:
#  test.dumpJobList()
#  print len(test.aJobList)
#  print test.totalcount

test = Indeed(delayBetweenRequests=1, loggingLevel=logging.INFO)
test.dumpJobCategoryUrlMap()  
test.dumpStateUrlMap()  

