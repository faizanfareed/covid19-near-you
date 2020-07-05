#Custom signals 
import django.dispatch

location_done = django.dispatch.Signal(providing_args=['sender','instance','change','changedfeilds'])

quarantine_done = django.dispatch.Signal(providing_args=['sender','instance','change','changedfeilds'])