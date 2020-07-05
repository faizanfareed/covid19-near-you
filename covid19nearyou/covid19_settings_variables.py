
#Batch size 
LOCATION_CACHE_BATCH_SIZE = 50


#Region incuabation peroid. 
# See Incubation peroid time of COVID-19 on World Health Organization website 
COVID19_INCUBATION_PERIOD_FOR_EXPIRE_POINT = 6 # days 

#Geospatial file update time 
COVID19_UPDATE_DATA_TIME = 12 # Hours


#Different radius ranges for finding points 
FIRST_RANGE_CIRCLE = 1 # 1st range/zone
SECOND_RANGE_CIRCLE = 2 # 2nd radius range/zone 
THIRD_RANGE_CIRCLE = 3  # 3rd radius range/zone

# The radius is specified in one of the following units:
#   m for meters.
#   km for kilometers.
#   mi for miles.
#   ft for feet.

# Radius range unit
RANGE_IN_UNITS = 'km'






#Don't need to change these. These are used for Map
FIRST_RANGE_CIRCLE_RADIUS = FIRST_RANGE_CIRCLE * 1000
SECOND_RANGE_CIRCLE_RADIUS = SECOND_RANGE_CIRCLE *  1000
THIRD_RANGE_CIRCLE_RADIUS = THIRD_RANGE_CIRCLE * 1000


# Quarantine radius range 
QUARANTINE_RADIUS_RANGE = 10 # Km
QUARANTINE_RADIUS_RANGE_UNIT = 'km'


#Pakistan Map canter point
#Change these according to your country 

MAP_CENTER_POINT_LATITUDE = 31.433254
MAP_CENTER_POINT_MAGNITUDE = 74.350311



#By Default Pakistan boundry (polygon) 
#Change these according to your country 

REGION_BOUNDRY_MIN_LATITUDE = 23
REGION_BOUNDRY_MAX_LATITUDE = 37

REGION_BOUNDRY_MIN_LONGITUDE = 60
REGION_BOUNDRY_MAX_LONGITUDE = 77


#No need to change 
WHO_WEBSITE_LINK_NAME = 'WHO advice'
WHO_WEBSITE_LINK = 'https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public'

#By default Pakistan
#Change these according to your country 
MY_COUNTRY_COVID19_WEB_LINK_NAME = 'PAKISTAN COVID-19'
MY_COUNTRY_COVID19_WEB_LINK = 'http://covid.gov.pk/'

#Country name 
COUNTRY_NAME = 'PAKISTAN'