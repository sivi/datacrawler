from craiglist import CraigList

#craiglist(country='US', state='CA', city='San Francisco', filters=None)
test = CraigList()
#test.dumpCityUrlMap()  
#test.dumpJobCategoryUrlMap()  
#test.dumpJobFilterMap()

#print ('link map lenght ' + str(len(test.aLinkMap)))
test.fetchJobList(city='san francisco bay area', jobCategory='jobs', filterList=['full-time','contract'], countLimit=5)
test.dumpJobList()
