from django.conf import settings # import the settings file

def setting_constants(request):
    # return the value you want as a dictionnary. 
    instance = settings.__dict__['_wrapped'].__dict__
    return instance 



    