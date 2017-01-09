from craiglist import CraigList
import logging

#craiglist(country='US', state='CA', city='San Francisco', filters=None)
test = CraigList(delayBetweenRequests=1, loggingLevel=logging.INFO)
#test.dumpCityUrlMap()  
#test.dumpJobCategoryUrlMap()  
#test.dumpJobFilterMap()

#print ('link map lenght ' + str(len(test.aLinkMap)))
#success = test.fetchJobList(city='san francisco bay area', jobCategory='jobs', filterList=['full-time','contract'], countLimit=5)
success = test.fetchJobList(city='san francisco bay area', jobCategory='jobs', filterList=['internship'], countLimit=500)
#success = test.fetchJobList(city='chicago', jobCategory='business / mgmt', filterList=['full-time','posted today'], countLimit=10)
if success:
  #test.dumpJobList()
  len(test.aJobList)
  test.totalcount
