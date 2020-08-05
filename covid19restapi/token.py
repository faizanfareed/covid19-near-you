import jwt
from django.conf import settings
import datetime

class Token:

    algo = 'HS256'
    secret = settings.SECRET_KEY + settings.SALT
    expiration_time =  settings.JWT_EXPIRATION_TIME

    def __init__(self,deviceid=None,algo=None,expiration_time=settings.JWT_EXPIRATION_TIME,token=None):
        
        if algo:
            self.algo = algo
        if expiration_time:
            self.expiration_time = expiration_time
        if token:
            self.token = token
                
        if deviceid:
            self.deviceid = deviceid
            

    def generate_token(self):

        currenttime = datetime.datetime.now()
        expiredat = currenttime + datetime.timedelta(minutes=self.expiration_time)
        expiredat = datetime.datetime.timestamp(expiredat)
       
      
        self.payload = {
            'deviceid':self.deviceid,
            'iat':currenttime,
            'exp':expiredat,   
        }
       
        token = jwt.encode(self.payload,self.secret,algorithm=self.algo)
       
        return token.decode()  

    def is_token_expired(self):
     
        try:
            token = jwt.decode(self.token, self.secret, algorithms=self.algo)
            self.deviceid = token.get('deviceid')
            return False 
            
        except jwt.ExpiredSignatureError: # Signature has expired
          
            self.error = 'Token is expired.'
            return True  
       
        except jwt.InvalidTokenError:
            
            self.error = 'Invalid token.'
            return True 
    

    def get_error_message(self):
        return self.error        

    def get_algo(self):
        return self.algo

    def get_deviceid(self):
        return self.deviceid

 