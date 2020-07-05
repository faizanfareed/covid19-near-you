from django.db.models.signals import post_save , post_delete
from django.dispatch import Signal
from . import redis_keys as REDIS_KEYS
import time 
import datetime
from django_redis import get_redis_connection
from django.dispatch import Signal, receiver
from . models import *
from . signals import  *
from django.db.models import F



@receiver(location_done)
def Confirmed_Case_Location_Reciever(sender,**kwargs):
  if  kwargs['change']: # updated
    pass
   
  else:

    # created 
    instance = kwargs['instance']


    con = get_redis_connection("default")
    pipeline = con.pipeline()

       

    #GEOSPATIAL INSERTION 
    pipeline.execute_command('GEOADD',REDIS_KEYS.GEOSPATIAL_DATA_KEY,float(instance.longitude),float(instance.latitude),instance.get_redis_key())
    #EXPIRE AND DATA INSERTION
    pipeline.execute_command('zadd',REDIS_KEYS.COVID19_GEOSPATIAL_POINTS_EXPIRE_DATA_KEY,'nx','ch',instance.get_expire_at_in_unixtime() ,instance.get_redis_key())
        
    #COVID19 GEOSPATIAL HASH
    pipeline.hmset(instance.get_redis_key(),instance.get_hash_for_redis())

    #COVID19 GEOSPATIAL HASH SETTING EXPIRE DATE
    pipeline.expireat(name=instance.get_redis_key(),when=instance.get_expire_at_in_unixtime())

    result = pipeline.execute()
    print(result)


@receiver(quarantine_done)
def Quarantine_Center_Receiver(sender,**kwargs):
    if  kwargs['change']: 
        # updated
    
        instance =  kwargs['instance']
        
        con = get_redis_connection("default")  
        pipeline = con.pipeline()


        if instance.is_visible:

            #GEOSPATIAL INSERTION 
            pipeline.execute_command('GEOADD',REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY,float(instance.longitude),float(instance.latitude),instance.get_redis_key())
                
            #COVID19 GEOSPATIAL HASH
            pipeline.hmset(instance.get_redis_key(),instance.get_hash_for_redis())

        else:
            pipeline.execute_command('ZREM', REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY,instance.get_redis_key())
            
            pipeline.execute_command('DEL',instance.get_redis_key())

        result = pipeline.execute()
   
    else:

        # created 
        instance = kwargs['instance']

        
        con = get_redis_connection("default")
        pipeline = con.pipeline()

        #GEOSPATIAL INSERTION 
        pipeline.execute_command('GEOADD',REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY,float(instance.longitude),float(instance.latitude),instance.get_redis_key())
        
        #COVID19 GEOSPATIAL HASH
        pipeline.hmset(instance.get_redis_key(),instance.get_hash_for_redis())

        result = pipeline.execute()
    

@receiver(post_save, sender=GeospatialFile)
def Geospatial_File_Reciever(**kwargs):
   
     instance = kwargs['instance']
    
     if instance.is_finshed == False and instance.sourcetype == 1:
        AddToFileNewAndExpireOldCovid19Location.objects.create(geospatialfile=instance)
        
   
@receiver(post_save, sender=AddToFileNewAndExpireOldCovid19Location)
def Add_To_File_New_And_Expire_Old_Covid19_Location_Reciever(**kwargs):
     
     instance = kwargs['instance']
    
     if instance.is_finshed == True:
       
        fileobj = GeospatialFile.objects.get(id=instance.geospatialfile.id)
        fileobj.is_finshed = True
        fileobj.finshed_at = datetime.datetime.now()
        fileobj.save()


@receiver(post_save, sender=RedisBatchManager)
def Redis_Batch_Manager_Reciever(**kwargs):
   
     instance = kwargs['instance']
   
     if kwargs['created'] == True:
      
        if instance.location_batches > 0:
            Create_Confirmed_Case_Batch_Ranges(instance.location_points,instance.location_batches,instance)
        if instance.qurantine_batches > 0:
            Create_Quarantine_Center_Batch_Ranges(instance.qurantine_points,instance.qurantine_batches,instance)
     
    
def Create_Confirmed_Case_Batch_Ranges(totalpoints,step,instance):
  

    BtachObjectsList = []
    listofBtach = []
    index = 0
    
    if totalpoints > 1:
        for i in range(0,totalpoints,round(totalpoints/step)):
    
            if i+(round((totalpoints/step))  ) < totalpoints:
                
                start =  i
                end = i+round((totalpoints/step))
                batch = {
                    'batch':index,
                    'start':start,
                    'end':end
                }
                btachObject = ConfirmedCaseLocationBatch(batch_manager=instance,batch_no=index,range_start=start,range_end=end)
                BtachObjectsList.append(btachObject)

                listofBtach.append(batch)
            else:    
                
                start =  i
                end = totalpoints
                batch = {
                    'batch':index,
                    'start':start,
                    'end':end
                }
                listofBtach.append(batch)
                btachObject = ConfirmedCaseLocationBatch(batch_manager=instance,batch_no=index,range_start=start,range_end=end)
                BtachObjectsList.append(btachObject)
            index = index + 1 
    

        ConfirmedCaseLocationBatch.objects.bulk_create(BtachObjectsList,step)
    elif totalpoints == 1:
       
        ConfirmedCaseLocationBatch.objects.create(batch_manager=instance,batch_no=1,range_start=0,range_end=1)
       

    return None


def Create_Quarantine_Center_Batch_Ranges(totalpoints,step,instance):
  

    BtachObjectsList = []
    listofBtach = []
    index = 0
    
    if totalpoints > 1:
        for i in range(0,totalpoints,round(totalpoints/step)):
    
            if i+(round((totalpoints/step))  ) < totalpoints:
                
                start =  i
                end = i+round((totalpoints/step))
                batch = {
                    'batch':index,
                    'start':start,
                    'end':end
                }
                btachObject = QuarantineCenterBatch(batch_manager=instance,batch_no=index,range_start=start,range_end=end)
                BtachObjectsList.append(btachObject)

                listofBtach.append(batch)
            else:    
                
                start =  i
                end = totalpoints
                batch = {
                    'batch':index,
                    'start':start,
                    'end':end
                }
                listofBtach.append(batch)
                btachObject = QuarantineCenterBatch(batch_manager=instance,batch_no=index,range_start=start,range_end=end)
                BtachObjectsList.append(btachObject)
            index = index + 1 
        QuarantineCenterBatch.objects.bulk_create(BtachObjectsList,step)
    elif totalpoints == 1:
       
        QuarantineCenterBatch.objects.create(batch_manager=instance,batch_no=1,range_start=0,range_end=1)
       

    return None

