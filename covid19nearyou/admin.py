from django.contrib import admin
from .models import *


admin.site.register(ConfirmedCaseLocation,ConfirmedCaseLocationAdmin)

admin.site.register(QurantineCenter,QurantineCenterAdmin)

admin.site.register(GeospatialFile,GeospatialFileAdmin)

admin.site.register(RedisBatchManager,RedisBatchManagerAdmin)

admin.site.register(ConfirmedCaseLocationBatch,ConfirmedCaseLocationBatchAdmin)

admin.site.register(QuarantineCenterBatch,QuarantineCenterBatchAdmin)


