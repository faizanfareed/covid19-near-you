from django.shortcuts import render, redirect
from django_redis import get_redis_connection
from covid19.settings import STATIC_URL
from geojson import Point, Feature, FeatureCollection, dump
from .forms import *
from .redis_keys import  * 
from .models import * 
import datetime
from datetime import timedelta
import time 
import shutil
from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string
from . import context_processors 
from . import redis_keys as REDIS_KEYS
import os
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.contrib.humanize.templatetags import humanize
from django.contrib.auth.decorators import login_required

#Settings view  
@login_required(login_url='/admin/') 
def settings_config(request):
    return render(request,'covid19nearyou/pages/settings.html',)

#Help view   
@login_required(login_url='/admin/') 
def help(request):
    return render(request,'covid19nearyou/pages/help.html',)



"""
Index() view.

1 : Render Map, location form and with some advices 
2 : Get user location and pass to FindCovid19NearYou function and then pass response to template and render back to user 

"""

#Map Index page 
def index(request):
    context = {}

    geospatialFile_obj = GeospatialFile.objects.filter(is_finshed=True).order_by('-created_at').first()
           
    if geospatialFile_obj:
        context['data_updated_at'] = geospatialFile_obj.finshed_at
    
    if request.method == 'POST':
      
        form = LatitudeLongitudeForm(request.POST)

        if form.is_valid():
            
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']

            newcontext = FindCovid19NearYou(latitude,longitude)
            context = newcontext
            context['form']=form
            
        else:
            context['form']= form
            
    else:
        context['form'] =  LatitudeLongitudeForm()       

    return render(request,'covid19nearyou/pages/index.html',context) 


"""
dashboard() view 

This view is guery to Redis database to make sure  if any point (data) missing or not 

if data is missing :
     1- Get recent geospatial file object from MySQL db for store information in context like
        - Store object 
        - Last updated at time
    2- And also get those points from MySQL db which are not expired if points greater than 0 that's mean cache is missing 
       and then set is_cache_miss = True.  

if data not missing :
    1-  Set is_cache_exist = True 
    2- Get recent geospatial file object from MySQL db for store information in context like
        - Store object 
        - Last updated at time
        - Set Is_need_to_update_points_into_file =  geospatialFile_obj.isNeedTo_Update_Points_Into_File()
        - Set is_need_to_add_data_into_cache = is_need_to_add_data_into_cache(pipeline)
   
"""

#dashboard view  
@login_required(login_url='/admin/')  
def dashboard(request):
        context={}

        con = get_redis_connection("default")
        pipeline = con.pipeline()

        pipeline.execute_command('EXISTS',REDIS_KEYS.GEOSPATIAL_DATA_KEY)
        pipeline.execute_command('EXISTS',REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY)

        result = pipeline.execute()
        today = datetime.date.today()
        
        if result[0] == 0 : # Cache Miss 
            print('HEre ')
            context['is_cache_exist'] = False # Not exist
            geospatialFile_obj = GeospatialFile.objects.filter(is_finshed=True).order_by('-created_at').first()
           
            if geospatialFile_obj:
                    context['geospatialfile'] = geospatialFile_obj
                    context['DataUpdatedAt'] = geospatialFile_obj.getDataUpdatedAt() 
                    
            location_points = ConfirmedCaseLocation.objects.filter(expire_at__gt=today).count() # No of Locations points in Db for cache
            quarantine_points = QurantineCenter.objects.all().count() # No of QurantineCenter points in Db for cache

            if (location_points > 0 and quarantine_points > 0) or location_points > 0:
                context['is_cache_miss'] = True
                
            elif quarantine_points > 0 and result[1] == 0: 
                context['is_cache_miss'] = True

        else:# Cache Exist
            context['is_cache_exist'] = True #  exist
          
            geospatialFile_obj = GeospatialFile.objects.filter(is_finshed=True).order_by('-created_at').first()
           
            if geospatialFile_obj:
                context['geospatialfile']=geospatialFile_obj
                context['DataUpdatedAt'] = geospatialFile_obj.getDataUpdatedAt() 
                context['Is_need_to_update_points_into_file'] = geospatialFile_obj.isNeedTo_Update_Points_Into_File()
                context['is_need_to_add_data_into_cache'] = is_need_to_add_data_into_cache(pipeline)

        return render(request,'covid19nearyou/pages/dashboard.html',context)

"""
This method is used for is_need_to_add_data_into_cache().

1- Get current date 
2 - Count no of points in Redis which are not expired 
3 - Also Count no of points which are not expired in MySQl db.

After that comparing points if points are not equal in Redis and MySQL db that's mean some points are missing in 
Redis and return True else False.   
"""


def is_need_to_add_data_into_cache(pipeline):
        today = datetime.date.today()
        today_for_redis = time.mktime(today.timetuple())

        pipeline.execute_command('ZCOUNT',REDIS_KEYS.COVID19_GEOSPATIAL_POINTS_EXPIRE_DATA_KEY,today_for_redis,'+inf')
        pipeline.execute_command('ZCOUNT',REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY,'-inf','+inf')

        Location_Points_In_Redis,Quarantine_Points_In_Redis,  = pipeline.execute()

        location_points_In_MYSQL = ConfirmedCaseLocation.objects.filter(expire_at__gte=today).count() # No of Locations points in Db for cache
        quarantine_points_In_MYSQL = QurantineCenter.objects.filter(is_visible=True).count()


        if Location_Points_In_Redis == location_points_In_MYSQL and Quarantine_Points_In_Redis == quarantine_points_In_MYSQL:
            return False
        else:
            return True


# -------   Add data into Geospatial file and remov expired points  ------------#

"""
These 4 function  

1 - Add_To_File_New_And_Expire_Old_Covid19_Locations()
2 - AddPointsToGeojsonFile()
3 - RemoveCovid19ExpirePointsFromCache()
4 - get_features()

are used for add data into Geospatial File and Remove expired points from Redis and Geojosn file.

"""

# Function : 1     
@login_required
def Add_To_File_New_And_Expire_Old_Covid19_Locations(request):
    context={}

    if request.method == 'POST':
      
        if 'step1' in request.POST:

            #here to call function which update the coordinate file
            filepath = AddPointsToGeojsonFile(request)
            Filecreated = AddToFileNewAndExpireOldCovid19Location.objects.get(id=request.POST['id'])
            if Filecreated:
                Filecreated.is_file_created = True
                Filecreated.url = filepath
                Filecreated.save()
           
        elif 'step2' in request.POST:

            RemoveCovid19ExpirePointsFromCache()
            Filecreated = AddToFileNewAndExpireOldCovid19Location.objects.get(id=request.POST['id'])
            print(Filecreated)
            if Filecreated:
                  Filecreated.is_points_removed = True
                  Filecreated.is_finshed = True
                  Filecreated.save()
                  
                  return redirect('dashboard')  
       
        elif 'creategeospatialfile' in request.POST:
            
            form = GeospatialFileForm(request.POST)
            if form.is_valid():
               
                form.instance.sourcetype = 1

                form.save()
            
                
        return redirect('Add_To_File_New_And_Expire_Old_Covid19_Locations')
    else:
            
            geospatialfile = GeospatialFile.objects.filter(is_finshed=False).select_related('addtofilenewandexpireoldcovid19location').first()
            
            if geospatialfile:
           
                context['geospatialfile'] = geospatialfile
              
                if  hasattr(geospatialfile, 'addtofilenewandexpireoldcovid19location'):
                
                   
                    if geospatialfile.addtofilenewandexpireoldcovid19location.is_file_created == False:
                        context['is_step1'] = False
                    else:
                        context['is_step1'] = True
                       
                    context['singlepoint'] = geospatialfile.addtofilenewandexpireoldcovid19location

                    
                return render(request,'covid19nearyou/pages/add_delete_points.html',context)        
                
            else:
               

                geospatialFile_obj = GeospatialFile.objects.filter(is_finshed=True).order_by('-created_at').first()
              

                if geospatialFile_obj:
                    
                    if geospatialFile_obj.isNeedTo_Update_Points_Into_File():
                        
                        context['form'] = GeospatialFileForm()
                         
                    else:
                            return redirect('dashboard')
                else:

                 
                    context['form'] = GeospatialFileForm()
                
    return render(request,'covid19nearyou/pages/add_delete_points.html',context)


# Function : 2
# Add new points into Geospatial file 
def AddPointsToGeojsonFile(request):

    today = datetime.date.today()
    today = time.mktime(today.timetuple())


    con = get_redis_connection("default",)
    pipeline = con.pipeline()


    features= []

    pipeline.execute_command('ZRANGEBYSCORE',REDIS_KEYS.COVID19_GEOSPATIAL_POINTS_EXPIRE_DATA_KEY,today,'+inf')
    pipeline.execute_command('ZRANGEBYSCORE',REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY,'-inf','+inf')

    NewPoints,Quarantine_Points,  = pipeline.execute()
    
    for keys in NewPoints:
        pipeline.execute_command('hgetall',keys.decode())

    LcoationHashKeys = pipeline.execute()

    locationFeatures = get_features(LcoationHashKeys,False)

    for keys in Quarantine_Points:
        pipeline.execute_command('hgetall',keys.decode())

    QuarantineHashKeys = pipeline.execute()    
    QurantineFeatures =  get_features(QuarantineHashKeys,True)

   
    features =  locationFeatures + QurantineFeatures
    feature_collection = FeatureCollection(features)

    
    today = datetime.date.today()

    filename = today.strftime('%d-%m-%y')
    filepath = os.path.join(settings.MEDIA_ROOT+'location/', filename+'.json')


    with open(filepath, 'w') as f:
        dump(feature_collection, f)
    

    mapfilepath = os.path.join(settings.MEDIA_ROOT+'location/data/', 'data.json')
    shutil.copy(filepath, mapfilepath)    
        
    full_url = ''.join(['http://', get_current_site(request).domain, '/media/location/data/'+filename+'.json'])

    return full_url
   
# Function : 3
# Remove expired points from Redis 
def RemoveCovid19ExpirePointsFromCache():

    con = get_redis_connection("default",)
    pipeline = con.pipeline()

    today = datetime.date.today()
    today = time.mktime(today.timetuple())
    

    pipeline.execute_command('ZRANGEBYSCORE','EXPR_AND_POINTS','-inf',today)

    ExpirePoints,  = pipeline.execute()

   
    for key in ExpirePoints:
        pipeline.execute_command('zrem','COVID19POINTS',key.decode())

    for key in ExpirePoints:
        pipeline.execute_command('zrem','EXPR_AND_POINTS',key.decode())


    deletedpointsstatus = pipeline.execute()

# Function : 4
# Create features for Geospatial file (Geojson file)
def get_features(hashes,is_quarantine):


    features= []

    for zone in hashes:
    
        if  zone:

            if is_quarantine:
        
                point = Point((float(zone[b'longitude'].decode()),float(zone[b'latitude'].decode())))
                
                features.append(Feature(geometry=point, properties={
                    "name": zone[b'name'].decode(),
                    "created_at": zone[b'created_at'].decode(),
                    "updated_at" : zone[b'updated_at'].decode(),
                
                    "is_quarantine":1,
                    }
                    ))
            else:
                point = Point((float(zone[b'longitude'].decode()),float(zone[b'latitude'].decode())))
            
                features.append(Feature(geometry=point, properties={
                    "name": zone[b'name'].decode(),
                    "created_at": zone[b'created_at'].decode(),
                    "updated_at" : zone[b'updated_at'].decode(),
                    "expire_at" : zone[b'expire_at'].decode(),
                    "is_quarantine":0,
                    }
                    ))        
    return features





# -------   Add data into Redis Database.  ------------#


"""
Add data into Redis Database.
These methods add data into Redis.

1 -  Cache_Failed_Add_Geospatial_Data_Into_Cache() view
2 -  Add_Location_Batch_Into_Cache()
3 -  Add_Quarantine_Batch_Into_Cache()
4 -  getNoOfBatches()

"""



# Function : 1
# Main view for Add data into Redis        
@login_required(login_url='/admin/')  
def Cache_Failed_Add_Geospatial_Data_Into_Cache(request):

    context={}

    if request.method == 'POST':
       

        if 'createbtach' in request.POST:
            form = LocationBatchManagerForm(request.POST)
          
            if form.is_valid():

                form = form.save(commit=False)

              
                form.qurantine_points = int(request.POST['qurantine_points'])

                form.qurantine_batches = int(request.POST['qurantine_batches'])
                    
                form.location_points = int(request.POST['location_points'])

                form.location_batches = int(request.POST['location_batches'])

                if form.qurantine_points == 0:
                    form.is_quarantine_batches_completed = True


                if form.location_points == 0:
                    form.is_location_batches_completed = True

                form.save()

                return redirect('Cache_Failed_Add_Geospatial_Data_Into_Cache')
      
        elif 'process_location_batch' in request.POST:

            batchId= request.POST['Location_batch_not_completed_Id']

            if batchId:
                try:
                    batch = ConfirmedCaseLocationBatch.objects.get(id=batchId,is_completed=False)
                    result = Add_Location_Batch_Into_Cache(batch)
                    if result:
                        batch.is_completed = True
                        batch.save()

                        Batch_Manager_Object  = RedisBatchManager.objects.get(id=batch.batch_manager.id)
                        
                        Batch_Manager_Object.location_completed_batches = Batch_Manager_Object.location_completed_batches + 1
                        
                        if Batch_Manager_Object.location_completed_batches == Batch_Manager_Object.location_batches:
                            if Batch_Manager_Object.qurantine_completed_batches == Batch_Manager_Object.qurantine_batches:
                                Batch_Manager_Object.is_finshed = True

                            Batch_Manager_Object.is_location_batches_completed = True   
                            Batch_Manager_Object.save()
                            return redirect('dashboard')  
                        else:
            
                            Batch_Manager_Object.save()  
                       
                            return redirect('Cache_Failed_Add_Geospatial_Data_Into_Cache')

                except ConfirmedCaseLocationBatch.DoesNotExist:
                    batch = None
                   
            else:
                pass # error     
        
        elif 'process_quarantine_batch' in request.POST: 
            batchId= request.POST['Quarantine_batch_not_completed_Id']

            if batchId:
                try:
                    batch = QuarantineCenterBatch.objects.get(id=batchId,is_completed=False)
                    result = Add_Quarantine_Batch_Into_Cache(batch)
                    if result:
                        batch.is_completed = True
                        batch.save()

                        Batch_Manager_Object  = RedisBatchManager.objects.get(id=batch.batch_manager.id)
                        
                        Batch_Manager_Object.qurantine_completed_batches = Batch_Manager_Object.qurantine_completed_batches + 1
                        
                        if Batch_Manager_Object.qurantine_completed_batches == Batch_Manager_Object.qurantine_batches:
                            if Batch_Manager_Object.qurantine_completed_batches == Batch_Manager_Object.qurantine_batches:
                                Batch_Manager_Object.is_finshed = True

                            Batch_Manager_Object.is_quarantine_batches_completed = True   
                            Batch_Manager_Object.save()
                            return redirect('dashboard')  
                        else:
                            
                            Batch_Manager_Object.save()  
                       
                            return redirect('Cache_Failed_Add_Geospatial_Data_Into_Cache')

                except QuarantineCenterBatch.DoesNotExist:
                    batch = None
                   
            else:
                pass # errror     
     
        return redirect('Cache_Failed_Add_Geospatial_Data_Into_Cache')
    else:
        con = get_redis_connection("default",)
        pipeline = con.pipeline()
        pipeline.execute_command('EXISTS',REDIS_KEYS.GEOSPATIAL_DATA_KEY)
        pipeline.execute_command('EXISTS',REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY)
        result = pipeline.execute()

       
       

        if result[0] == 0 : # Cache Miss 
          

            today = datetime.date.today()
            
            location_points = ConfirmedCaseLocation.objects.filter(expire_at__gt=today).count() # No of Locations points in Db for cache
            quarantine_points = QurantineCenter.objects.all().count() # No of QurantineCenter points in Db for cache

            if location_points > 0 or quarantine_points > 0: # Locations or QurantineCenter Points greater 0 

                Batch_Manager_Object = RedisBatchManager.objects.filter(is_finshed=False).first()

                if Batch_Manager_Object:

                    context['Batch_Manager_Object']= Batch_Manager_Object

                    Location_Batches = ConfirmedCaseLocationBatch.objects.filter(batch_manager=Batch_Manager_Object)
                    Quarantine_Batches = QuarantineCenterBatch.objects.filter(batch_manager=Batch_Manager_Object)
              
                    if Location_Batches:
                        context['Location_Batches'] = Location_Batches
                        context['Location_batch_not_completed_Id'] = Batch_Manager_Object.get_Id_of_which_batch_is_not_completed(Location_Batches) 

                    if Quarantine_Batches:
                        context['Quarantine_Batches'] = Quarantine_Batches
                        context['Quarantine_batch_not_completed_Id'] = Batch_Manager_Object.get_Id_of_which_batch_is_not_completed(Quarantine_Batches) 


                else:

                    intial_data = {'location_batches':getNoOfBatches(location_points),'location_points':location_points,'qurantine_batches':getNoOfBatches(quarantine_points),'qurantine_points':quarantine_points}
                    form = LocationBatchManagerForm(intial_data)
                    
                    context['form']=form

                    context['location_points'] = location_points

                    context['location_batches'] = getNoOfBatches(location_points)

                    context['qurantine_points'] = quarantine_points

                    context['qurantine_batches'] = getNoOfBatches(quarantine_points)
            
            else:
                context['message']= 'Add  points and then create first geospatil file thanks'                    
        else: # No Cache Miss
           
            Batch_Manager_Object = RedisBatchManager.objects.filter(is_finshed=False).first() #If cache in processing then comes here

            if Batch_Manager_Object:
                context['Batch_Manager_Object']= Batch_Manager_Object

                Location_Batches = ConfirmedCaseLocationBatch.objects.filter(batch_manager=Batch_Manager_Object)  
                Quarantine_Batches = QuarantineCenterBatch.objects.filter(batch_manager=Batch_Manager_Object)
 
                if Location_Batches:
                    context['Location_Batches'] = Location_Batches
                    context['Location_batch_not_completed_Id'] = Batch_Manager_Object.get_Id_of_which_batch_is_not_completed(Location_Batches) 
                
                if Quarantine_Batches:
                        context['Quarantine_Batches'] = Quarantine_Batches
                        context['Quarantine_batch_not_completed_Id'] = Batch_Manager_Object.get_Id_of_which_batch_is_not_completed(Quarantine_Batches) 


            else:
                print('Cache is not empty sad : Thier is no need to update Cache.')    
                context['message']='Thier is no need to update Cache.'       

           
           
       
            
    return render(request,'covid19nearyou/pages/add_data_into_redis.html',context)

# Function : 2 
# Add Confirmed Case location batch into Redis database
def Add_Location_Batch_Into_Cache(batch):
    
    
    today = datetime.date.today()
    locationlist = ConfirmedCaseLocation.objects.filter(expire_at__gt=today).all()[batch.range_start:batch.range_end]
   
    
   
    con = get_redis_connection("default")
    pipeline = con.pipeline()
    
    for instance in locationlist:
       
        
        #GEOSPATIAL INSERTION 
        pipeline.execute_command('GEOADD',REDIS_KEYS.GEOSPATIAL_DATA_KEY,float(instance.longitude),float(instance.latitude),instance.get_redis_key())
        #EXPIRE AND DATA INSERTION
        pipeline.execute_command('zadd',REDIS_KEYS.COVID19_GEOSPATIAL_POINTS_EXPIRE_DATA_KEY,'nx','ch',instance.get_expire_at_in_unixtime() ,instance.get_redis_key())
            
        #COVID19 GEOSPATIAL HASH
        pipeline.hmset(instance.get_redis_key(),instance.get_hash_for_redis())

        #COVID19 GEOSPATIAL HASH SETTING EXPIRE DATE
        pipeline.expireat(name=instance.get_redis_key(),when=instance.get_expire_at_in_unixtime())

    result = pipeline.execute()
    
   
    
    return result

# Function : 3 
# Add Quarantine batch into Redis database
def Add_Quarantine_Batch_Into_Cache(batch):
    
    
    today = datetime.date.today()
    Quarantine_Batches = QurantineCenter.objects.all()[batch.range_start:batch.range_end]

    con = get_redis_connection("default")
    pipeline = con.pipeline()
    
    for instance in Quarantine_Batches:
    
        #GEOSPATIAL INSERTION 
        pipeline.execute_command('GEOADD',REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY,float(instance.longitude),float(instance.latitude),instance.get_redis_key())
        
        #COVID19 GEOSPATIAL HASH
        pipeline.hmset(instance.get_redis_key(),instance.get_hash_for_redis())

    result = pipeline.execute()
   
    
    return result

# Function : 4
# Calculate no of batches required for Redis 
def getNoOfBatches(locationPoints):

    if locationPoints == 0:
        return 0
    elif locationPoints <= settings.LOCATION_CACHE_BATCH_SIZE:
        return 1
    else:
        if locationPoints/settings.LOCATION_CACHE_BATCH_SIZE % 2 == 0 :    
            return round(locationPoints/settings.LOCATION_CACHE_BATCH_SIZE)   
        else:
            return round(locationPoints/settings.LOCATION_CACHE_BATCH_SIZE) + 1



"""
This method is used for AJAX request and return back response.

1 - AJAX_find_covid19_near_you()

"""


#Handle AJAX request and send back response as a JSON
def AJAX_find_covid19_near_you(request):
    data = {}
    if request.is_ajax and request.method == 'POST':

        form = LatitudeLongitudeForm(request.POST)

        if form.is_valid():
            
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
          

            context = FindCovid19NearYou(latitude,longitude) 
            context.update(context_processors.setting_constants(request)) #render_to_string not supported context_processors
            templateTag = render_to_string('covid19nearyou/templates/covid19_near_you_template.html', context)
           

            data = {
            'is_success':True,
            'data':templateTag,
            'current_latitude':latitude,
            'current_longitude':longitude,
            }

            return  JsonResponse(data,safe=False)
        else: # Not Valid 

            data['is_success'] = False
           
            if form.has_error('latitude',code='invalid'):
               
                latitude_error = 'Latitude must be numeric'
                data['latitude_error'] = latitude_error

            else:
           
                latitude_error = 'Latitude out of range'
                data['latitude_error'] = latitude_error

            if form.has_error('longitude',code='invalid'):
                longitude_error = 'Longitude must be numeric'
          
                data['longitude_error'] = longitude_error
            else:
             
                longitude_error = 'Longitude out of range'
                data['longitude_error'] = longitude_error
            
        return  JsonResponse(data,safe=False)

"""
This method is actually finds the COVID19 related stuff.

1 - FindCovid19NearYou()

"""

#Find COVID-19 Nearest Points
def FindCovid19NearYou(latitude,longitude):

            con = get_redis_connection("default",)
            pipeline = con.pipeline()
            context = {}

            context['current_latitude']=latitude
            context['current_longitude']=longitude


            pipeline.georadius(name=REDIS_KEYS.GEOSPATIAL_DATA_KEY, longitude=longitude,
                            latitude=latitude, radius=settings.FIRST_RANGE_CIRCLE, unit=settings.RANGE_IN_UNITS, withdist=True, withcoord=True, sort='ASC')

            pipeline.georadius(name=REDIS_KEYS.GEOSPATIAL_DATA_KEY, longitude=longitude,
                            latitude=latitude, radius=settings.SECOND_RANGE_CIRCLE, unit=settings.RANGE_IN_UNITS, withdist=True, withcoord=True, sort='ASC')

            pipeline.georadius(name=REDIS_KEYS.GEOSPATIAL_DATA_KEY, longitude=longitude,
                            latitude=latitude, radius=settings.THIRD_RANGE_CIRCLE, unit=settings.RANGE_IN_UNITS, withdist=True, withcoord=True, sort='ASC')

            pipeline.georadius(name=REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY, longitude=longitude,
                             latitude=latitude, radius=settings.QUARANTINE_RADIUS_RANGE, unit=settings.QUARANTINE_RADIUS_RANGE_UNIT, withdist=True, withcoord=True, sort='ASC')


            covid19_point_list = pipeline.execute()
          
            dict_list_of_covid19_point = []
            
            nearest_covid19_quarantine = {}
        
            index = 0
            radius_range = 'radius_range_in_' + settings.RANGE_IN_UNITS

            for covid19_point in covid19_point_list:

                if index == 3: #Quarantine 
                   
                    if covid19_point:
                        for nearestQuarantine in covid19_point: # Quarantine consist of multiple quarantine center 
                            address = nearestQuarantine[0].decode()
                            address = address.split(':')
                            zone = {

                            'address':address[2],
                            'distance': nearestQuarantine[1],
                            'longitude': nearestQuarantine[2][0],
                            'latitude': nearestQuarantine[2][1],
                            'lat_long':str(nearestQuarantine[2][0]) + ','+  str(nearestQuarantine[2][1]),
                            }

                            nearest_covid19_quarantine = zone
                            break # if nearest quarantine found then no need to find others 



                else: #Other 3 queries result Confirmed cases
                    
                    if covid19_point:
                
                        listofmultiplezones = []
                    
                        total_zone = {radius_range: index+1, 'total_effected_zone': len(covid19_point), 'is_empty': False,
                        }
                        listofmultiplezones.append(total_zone)
                        address = []
                        for eachzone in covid19_point:

                            address = eachzone[0].decode()
                            address = address.split(':')

                            zone = {

                            'address':address[2],
                    
                             radius_range: index+1,

                            'distance': eachzone[1],

                            'longitude': eachzone[2][0],
                            'latitude': eachzone[2][1],
                            'lat_long':str(eachzone[2][0]) + ','+  str(eachzone[2][1]),
                            }
                            
        
                            listofmultiplezones.append(zone)

                        dict_list_of_covid19_point.append(listofmultiplezones)

                    else:  # empty
                        listofmultiplezones = []
                        total_zone = {radius_range: index+1,
                            'total_effected_zone': len(covid19_point), 'is_empty': True, }
                        listofmultiplezones.append(total_zone)

                        zone = {
                            radius_range: index+1,
                        }
                        listofmultiplezones.append(zone)
                        dict_list_of_covid19_point.append(listofmultiplezones)


                index = index + 1


            

           
            nearest_covid19_point = {}

               
        
            
              
            if dict_list_of_covid19_point[0][0]['radius_range_in_km'] == 1 and not dict_list_of_covid19_point[0][0]['is_empty']:
                   
                    nearest_covid19_point = dict_list_of_covid19_point[0][1]
                

                    nearest_covid19_point['red'] = 0 #'Red zone'

                    zones = {
                        'is_empty':True,
                       
                    }
                    nearest_covid19_point['zones'] = zones

            elif dict_list_of_covid19_point[1][0]['radius_range_in_km'] == 2 and not dict_list_of_covid19_point[1][0]['is_empty']:
                   

                    nearest_covid19_point = dict_list_of_covid19_point[1][1]

                    nearest_covid19_point['yellow'] = 1 #'yellow zone' 
                    

            elif dict_list_of_covid19_point[2][0]['radius_range_in_km'] == 3 and not  dict_list_of_covid19_point[2][0]['is_empty']:
                   
                    nearest_covid19_point = dict_list_of_covid19_point[2][1]
                   
                    nearest_covid19_point['green'] = 2 #'green zone' 
                    
            else: # no points around you
               
                nearest_covid19_point['no_points'] = 3

            total_covid19_points_near_you =  dict_list_of_covid19_point[2][0]['total_effected_zone']


            context['total_covid19_points_near_you'] = total_covid19_points_near_you
            context['nearest_covid19_point'] = nearest_covid19_point
            context['covid19_point_list'] = dict_list_of_covid19_point
            context['nearest_covid19_quarantine'] = nearest_covid19_quarantine
           

            return context


















