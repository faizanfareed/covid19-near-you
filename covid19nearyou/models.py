from django.db import models
from django.contrib.humanize.templatetags import humanize
from django.conf import settings
from django.contrib import admin
from django.utils import timezone
import datetime
from datetime import timedelta
import time 
from django_redis import get_redis_connection
from . import redis_keys as REDIS_KEYS
from django.contrib import messages
from . import signals 


class GeospatialFile(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_finshed = models.BooleanField(default=False)
    finshed_at = models.DateTimeField(auto_now=False,blank=False,null=True)
    

    def isNeedTo_Update_Points_Into_File(self):

        file_update_time =  timezone.now() - timedelta(hours=settings.COVID19_UPDATE_DATA_TIME)


        if self.finshed_at < file_update_time and self.is_finshed: 
            
            return True
        else:
            
            return False 
          
    def getDataUpdatedAt(self):
        return humanize.naturaltime(self.finshed_at) 

    def __str__(self):
        return str(self.is_finshed)

class GeospatialFileAdmin(admin.ModelAdmin):
  
    list_display = ( 'finshed_at','is_finshed','created_at',)
   

class AddToFileNewAndExpireOldCovid19Location(models.Model):

    geospatialfile = models.OneToOneField(GeospatialFile,on_delete=models.CASCADE)
    is_file_created = models.BooleanField(default=False)
    is_points_removed = models.BooleanField(default=False)
    is_finshed = models.BooleanField(default=False)
    url = models.URLField(editable=True,null=True,blank=False)

class AddToFileNewAndExpireOldCovid19LocationAdmin(admin.ModelAdmin):
  
    list_display = ('geospatialfile', 'url','is_file_created','is_points_removed','is_finshed',)
    search_fields = ('url',)
    

class RedisBatchManager(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    is_finshed = models.BooleanField(default=False)

    is_quarantine_batches_completed = models.BooleanField(default=False)
    is_location_batches_completed = models.BooleanField(default=False)
    
    
    location_points = models.PositiveIntegerField(blank=True,default=0)
    qurantine_points = models.PositiveIntegerField(blank=True,default=0)

    location_batches = models.PositiveIntegerField(blank=True,default=0)
    qurantine_batches = models.PositiveIntegerField(blank=True,default=0)

    location_completed_batches = models.PositiveIntegerField(blank=True,default=0)
    qurantine_completed_batches = models.PositiveIntegerField(blank=True,default=0)

    def is_location_batch_completed(self):
         return self.is_location_batches_completed
    
    def is_quarantine_batch_completed(self):
         return self.is_quarantine_batches_completed
     

    def get_Id_of_which_batch_is_not_completed(self,batches):
        #   Quarantine_batch_not_completed_Id = -1

        #             for batch in Quarantine_Batches:
        #                 if batch.is_completed == False:
        #                     Quarantine_batch_not_completed_Id = batch.id
        #                     break

        for batch in batches:
            if batch.is_completed == False:
                 return batch.id
  
class RedisBatchManagerAdmin(admin.ModelAdmin):
  
    list_display = ( 'created_at','is_finshed','is_quarantine_batches_completed','is_location_batches_completed','location_batches','qurantine_batches','location_points','qurantine_points','location_completed_batches','qurantine_completed_batches',)
   


class ConfirmedCaseLocationBatch(models.Model):

    batch_manager = models.ForeignKey(RedisBatchManager,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    batch_no = models.PositiveIntegerField()
    range_start = models.PositiveIntegerField()
    range_end = models.PositiveIntegerField()


class ConfirmedCaseLocationBatchAdmin(admin.ModelAdmin):
  
    list_display = ('batch_manager', 'created_at','is_completed','batch_no','range_start','range_end',)

class QuarantineCenterBatch(models.Model):

    batch_manager = models.ForeignKey(RedisBatchManager,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    batch_no = models.PositiveIntegerField()
    range_start = models.PositiveIntegerField()
    range_end = models.PositiveIntegerField()
    

class QuarantineCenterBatchAdmin(admin.ModelAdmin):
  
    list_display = ('batch_manager', 'created_at','is_completed','batch_no','range_start','range_end',)


class QurantineCenter(models.Model):

    
    name = models.CharField(max_length=150,unique=True)
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_visible = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=8,decimal_places=6)
    longitude = models.DecimalField(max_digits=8,decimal_places=6)


    
    def __str__(self):
        return self.name

    def get_redis_key(self):
        return REDIS_KEYS.QUARANTINE_OBJECT_KEY+ str(self.id)+':'+ self.name 

    def get_hash_for_redis(self):

        object_dic = self.__dict__
        object_dic = object_dic.copy()


        object_dic.pop('_state')
        object_dic.pop('is_visible')
        object_dic.pop('id')
        
    
        object_dic['created_at'] = object_dic['created_at'].strftime("%Y-%m-%d")
        object_dic['updated_at'] = object_dic['updated_at'].strftime("%Y-%m-%d")

        object_dic['latitude'] = float(object_dic['latitude'])
        object_dic['longitude'] = float(object_dic['longitude'])
        

        object_dic['is_quarantine'] = 1

        return object_dic

class QurantineCenterAdmin(admin.ModelAdmin):
  
    list_display = ('name', 'latitude','longitude','is_visible', 'created_at', 'updated_at',)
    list_filter = ('is_visible',)
    
   
    def message_user(self, *args):
        pass

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('name', 'latitude','longitude',)
        return self.readonly_fields 

    def delete_queryset(self, request, queryset):

        con = get_redis_connection("default")
        pipeline = con.pipeline()

        for instance in queryset:
           
            pipeline.execute_command('DEL',instance.get_redis_key())
            pipeline.execute_command('ZREM',REDIS_KEYS.GEOSPATIAL_QUARANTINE_DATA_KEY,instance.get_redis_key())
              
        result = pipeline.execute()
        queryset.delete()
       
    def save_model(self, request, obj, form, change):
       

        if not change and form.has_changed():  

           
            super(QurantineCenterAdmin, self).save_model(request, obj, form, change)
            signals.quarantine_done.send(self.__class__,instance=obj,change=change,changedfeilds=form.changed_data)
           
        elif change and form.has_changed(): 
                
                super(QurantineCenterAdmin, self).save_model(request, obj, form, change)
                signals.quarantine_done.send(self.__class__,instance=obj,change=change,changedfeilds=form.changed_data)
            
                messages.add_message(request, messages.SUCCESS, 'Qurantine Center saved successfully.')
                  
            
           
            
        elif change and not form.has_changed() :
            messages.add_message(request, messages.ERROR, 'Qurantine Center not updated.')
            return   
        


class ConfirmedCaseLocation(models.Model):

    
    name = models.CharField(max_length=150)
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expire_at = models.DateTimeField(auto_now=False)
    is_visible = models.BooleanField(default=True)
    
    latitude = models.DecimalField(max_digits=8,decimal_places=6)
    longitude = models.DecimalField(max_digits=8,decimal_places=6)


    
    def __str__(self):
        return self.name
 
    def get_expire_at_in_unixtime(self):
        return  int(time.mktime(self.expire_at.timetuple()))

    def get_redis_key(self):
        
        return REDIS_KEYS.LOCATION_OBJECT_KEY+str(self.id) +':'+ self.name 

    def get_hash_for_redis(self):

        object_dic = self.__dict__
        object_dic = object_dic.copy()

        object_dic.pop('_state')
        object_dic.pop('is_visible')
        object_dic.pop('id')

        object_dic['created_at'] = object_dic['created_at'].strftime("%Y-%m-%d")
        object_dic['updated_at'] = object_dic['updated_at'].strftime("%Y-%m-%d")

        object_dic['latitude'] = float(object_dic['latitude'])
        object_dic['longitude'] = float(object_dic['longitude'])
        object_dic['is_quarantine'] = 0

        object_dic['expire_at'] = object_dic['expire_at'].strftime("%Y-%m-%d")

        return object_dic
    
    def is_location_expired(self):

        current_time_hours =  timezone.now()


        if current_time_hours > self.expire_at : 

            return True
        else:
            return False  
           


class ConfirmedCaseLocationAdmin(admin.ModelAdmin):
  
    list_display = ('name', 'latitude','longitude' ,'is_visible', 'created_at', 'expire_at','updated_at',)
    list_filter = ('is_visible',)
    exclude =('expire_at',)
 
    search_fields = ('name',)


    def delete_queryset(self, request, queryset):

        con = get_redis_connection("default")
        pipeline = con.pipeline()
  
        for instance in queryset:
      
            pipeline.execute_command('DEL',instance.get_redis_key())
            pipeline.execute_command('ZREM',REDIS_KEYS.GEOSPATIAL_DATA_KEY,instance.get_redis_key())
            pipeline.execute_command('ZREM',REDIS_KEYS.COVID19_GEOSPATIAL_POINTS_EXPIRE_DATA_KEY,instance.get_redis_key())
    
        result = pipeline.execute()


        TotalDeletedObjects = queryset.delete()

    def message_user(self, *args):
        pass

    def has_change_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
      

        if not change and form.has_changed():  

            currentdate = datetime.date.today()
            obj.expire_at =  currentdate + timedelta(days=settings.COVID19_INCUBATION_PERIOD_FOR_EXPIRE_POINT)
            
            super(ConfirmedCaseLocationAdmin, self).save_model(request, obj, form, change)
            signals.location_done.send(self.__class__,instance=obj,change=change,changedfeilds=form.changed_data)
           
        elif change and form.has_changed(): 
        

                messages.add_message(request, messages.error, 'Location does not exist anymore.')
                return 

        elif change and not form.has_changed() :
           
            messages.add_message(request, messages.info, 'Post not created or not updated only saved')
                     
     





