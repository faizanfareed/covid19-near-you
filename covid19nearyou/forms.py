from . models import * 

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.conf import settings





class LatitudeLongitudeForm(forms.Form):

    latitude = forms.FloatField(help_text='Latitude ',localize=True,widget= forms.TextInput
                           (attrs={'placeholder':'Latitude'}))

    longitude = forms.FloatField(help_text='  Longitude',localize=True, widget= forms.TextInput
                           (attrs={'placeholder':'Longitude'}))

   
    def clean_latitude(self):

        if  isinstance(self.cleaned_data['latitude'],(float)):

            Latitude = float(self.cleaned_data['latitude'])
        
            if Latitude < settings.REGION_BOUNDRY_MIN_LATITUDE or Latitude >= settings.REGION_BOUNDRY_MAX_LATITUDE :
                raise forms.ValidationError(
                    _(' Latitude out of range'),code='outofrange'
                   
                )

      

        return Latitude

    def clean_longitude(self):

        if  isinstance(self.cleaned_data['longitude'],(float)):

            Longitude = float(self.cleaned_data['longitude'])
          


            if Longitude < settings.REGION_BOUNDRY_MIN_LONGITUDE or Longitude >= settings.REGION_BOUNDRY_MAX_LONGITUDE :
                raise forms.ValidationError(
                    _('Longitude out of range'),code='outofrange',
                 
                )

            
       
        return Longitude

class GeospatialFileForm(forms.ModelForm):

    class Meta:
        model = GeospatialFile
        exclude = ('created_at','is_finshed','finshed_at',)


class LocationBatchManagerForm(forms.ModelForm):


    class Meta:
        model = RedisBatchManager
        exclude = ( 'created_at','is_finshed','is_quarantine_batches_completed','is_location_batches_completed','location_batches','qurantine_batches','location_points','qurantine_points','location_completed_batches','qurantine_completed_batches',)



