from django.shortcuts import render
from django.http import JsonResponse
from covid19nearyou.views import FindCovid19NearYou
import jwt
from django.conf import settings
import datetime
from django.views.defaults import page_not_found
from django.views.decorators.csrf import csrf_exempt
from . token import Token




def custom404(request, exception=None):
   
    if request.path.startswith('/api'):
        return JsonResponse({
            'status_code': 404,
            'error': 'The resource was not found'
        },status=404)
    else:
        return render(request, '404.html', status=404)
       

def handler500(request):
    if request.path.startswith('/api'):
        return JsonResponse({
            'status_code': 500,
            'error': 'Internal server error'
        },status=500)
    else:
        
        return render(request, '500.html', status=500)




@csrf_exempt
def index(request):

    data = {}
    clientid = 'infinixhot5'
   

   
    if request.method == 'GET':


        if 'Authorization' in request.headers:

            userToken = request.headers['Authorization']
            
            
            userToken = userToken.split('Bearer')[1]
            userToken = userToken.strip()

            #print(dir(jwt))
            # token verification goes here 
            token = Token(token=userToken)
            if  not token.is_token_expired():

                if request.GET.get('latitude',False) and request.GET.get('longitude',False) :
                    # print(request.GET.get('latitude',False))
                    # print(request.GET.get('longitude',False))
                    try:
                        latitude = float(request.GET.get('latitude'))
                        longitude = float(request.GET.get('longitude'))
                        # print('In Float: ', float(latidute))

                        # print('Tyoe :', type(latidute))

                    except ValueError:
                        #print('Provide valid parameters')
                        data['error'] = 'invalid parameters'
                        return JsonResponse(data,status=400)      
                else:
                    #print('Query parameters are missing')
                    data['error'] = 'Query parameters are missing'
                    return JsonResponse(data,status=400) 
            else:
                data['error'] = token.get_error_message()
                return JsonResponse(data,status=200) 
            
            data = FindCovid19NearYou(latitude=31.433254,longitude=74.350311)
            return JsonResponse(data)
        
        else:
            data['error'] = 'Token is missing'
            return JsonResponse(data,status=401)
            
         
   
    else:
        error = {
                'error_code':'invalid_reqeust',
                'message':'Send data with Get request',
        }
        
        return JsonResponse(error,status=400)

@csrf_exempt
def generate_token(request):
    
    if request.method == 'POST':
        if 'deviceid' in request.headers:
            deviceid = request.headers['deviceid']
            print('deviceid : ',deviceid)

            if deviceid:


                token = Token(deviceid=deviceid)
                token_key = token.generate_token_key()
                data = {
                    'token':token_key
                    }

                return JsonResponse(data)  
            else:
                error = {
                'error_code':'invalid_reqeust',
                'message':'Device id is missing',
                }
        
                return JsonResponse(error,status=400)

        else:
            error = {
                'error_code':'invalid_reqeust',
                'message':'Device id is missing',
            }
        
            return JsonResponse(error,status=400)
    else:
        error = {
                'error_code':'invalid_reqeust',
                'message':'Send data with POST request',
        }
        
        return JsonResponse(error,status=400)
   
 


def verify_token(request):

    algo = 'HS256'
    salt = '23bxzc89nb3489cvb324'
    secret = 'faizan' + salt
   
    payload = {
        'iat':datetime.datetime.now(),
        'exp':datetime.datetime.now() + datetime.timedelta(days=1),
       

    }

    token = jwt.encode(payload,secret,algorithm=algo)
    data = {
        'token':token.decode()
    }
    return JsonResponse(data)  




