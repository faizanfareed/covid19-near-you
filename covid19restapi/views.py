from django.shortcuts import render
from django.http import JsonResponse
from covid19nearyou.views import FindCovid19NearYou
import jwt
from django.conf import settings
import datetime
from django.views.defaults import page_not_found
from django.views.decorators.csrf import csrf_exempt
from . token import Token
from django_redis import get_redis_connection
from . ratelimiter import SlidingWindowCounterRateLimiter


def custom404(request, exception=None):

    if request.path.startswith('/api'):
        return JsonResponse({
            'status_code': 404,
            'error': 'The resource was not found'
        }, status=404)
    else:
        return render(request, '404.html', status=404)


def handler500(request):
    if request.path.startswith('/api'):
        return JsonResponse({
            'status_code': 500,
            'error': 'Internal server error'
        }, status=500)
    else:

        return render(request, '500.html', status=500)


@csrf_exempt
def index(request):

    data = {}

    if request.method == 'GET':

        if 'secretcode' in request.headers:

            if request.headers['secretcode']:

                SECRET_CODE = request.headers['secretcode']

                if settings.SECRECT_CODE_FOR_SECURING_API_URL == SECRET_CODE:

                    if 'Authorization' in request.headers:

                        if request.headers['Authorization']:

                            userToken = request.headers['Authorization']

                            # token verification goes here
                            token = Token(token=userToken)

                            if not token.is_token_expired():

                                if request.GET.get('latitude', False) and request.GET.get('longitude', False):

                                    try:
                                        latitude = float(
                                            request.GET.get('latitude'))
                                        longitude = float(
                                            request.GET.get('longitude'))

                                        con = get_redis_connection("default")
                                        pipeline = con.pipeline()

                                        ratelimiter = SlidingWindowCounterRateLimiter(clientid=token.get_deviceid(
                                        ), redispipeline=pipeline, rate=settings.RATE, time_window_unit=settings.TIME_WINDOW_UNIT, is_ratelimit_reset_header_allowed=settings.IS_RATELIMIT_RESET_HEADER_ALLOWED, max_no_time_window_for_deletion=settings.MAX_NO_TIME_WINDOW_FOR_DELETION)

                                        if ratelimiter.isRequestAllowed():

                                            data = FindCovid19NearYou(
                                                latitude=latitude, longitude=longitude)

                                            response = JsonResponse(data)

                                            ratelimiterHttpHeaders = ratelimiter.getHttpResponseHeaders()

                                            for key, value in ratelimiterHttpHeaders.items():
                                                response[key] = value

                                            return response

                                        else:
                                            data['limit-exceeded'] = '429, Too many requests'
                                            response = JsonResponse(
                                                data, status=429)

                                            ratelimiterHttpHeaders = ratelimiter.getHttpResponseHeaders()

                                            for key, value in ratelimiterHttpHeaders.items():
                                                response[key] = value

                                            return response

                                    except ValueError:

                                        data['error'] = 'invalid parameters'
                                        return JsonResponse(data, status=400)
                                else:

                                    data['error'] = 'Query parameters are missing'
                                    return JsonResponse(data, status=400)
                            else:

                                data['error'] = token.get_error_message()
                                return JsonResponse(data, status=200)

                        else:

                            data['error'] = 'Access token is missing'
                            return JsonResponse(data, status=401)

                    else:
                        data['error'] = 'Authorization header is missing'
                        return JsonResponse(data, status=401)

                else:
                    error = {
                        'error_code': 'invalid_reqeust',
                        'message': 'Secret code is not valid.',
                    }

                    return JsonResponse(error, status=400)
            else:
                error = {
                    'error_code': 'invalid_reqeust',
                    'message': 'Secret code is missing.',
                }
                return JsonResponse(error)

        else:
            error = {
                'error_code': 'invalid_reqeust',
                'message': 'Secret code header is missing.',
            }

            return JsonResponse(error, status=400)

    else:
        error = {
            'error_code': 'invalid_reqeust',
            'message': 'Send data with Get request',
        }

        return JsonResponse(error, status=400)


@csrf_exempt
def generate_token(request):

    if request.method == 'POST':

        if 'secretcode' in request.headers:

            if request.headers['secretcode']:

                SECRET_CODE = request.headers['secretcode']

                if settings.SECRECT_CODE_FOR_SECURING_API_URL == SECRET_CODE:

                    if 'deviceid' in request.headers:

                        deviceid = request.headers['deviceid']

                       

                        if deviceid:

                         
                            token = Token(deviceid=deviceid)
                            token_key = token.generate_token()

                            data = {
                                'token': token_key
                            }

                            return JsonResponse(data)
                        else:
                           
                            error = {
                                'error_code': 'invalid_reqeust',
                                'message': 'Device id is missing',
                            }

                            return JsonResponse(error, status=400)
                    else:
                       
                        error = {
                            'error_code': 'invalid_reqeust',
                            'message': 'Device header is missing.',
                        }

                        return JsonResponse(error, status=400)

                else:
                    error = {
                        'error_code': 'invalid_reqeust',
                        'message': 'Secret code is not valid.',
                    }

                return JsonResponse(error, status=400)

            else:
                error = {
                    'error_code': 'invalid_reqeust',
                    'message': 'Secret code is missing.',
                }
                return JsonResponse(error)

        else:
            error = {
                'error_code': 'invalid_reqeust',
                'message': 'Secret code header is missing.',
            }

            return JsonResponse(error, status=400)

    else:
        error = {
            'error_code': 'invalid_reqeust',
            'message': 'Send data with POST request',
        }

        return JsonResponse(error, status=400)
