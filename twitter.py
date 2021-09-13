#for legal reasons:
#   -code is as is, no garatues given, WITHOUT ANY WARRANTY, use at your own risk
#   -do what ever you want with the code: redistribute, alter, sell, whatever
#   -when in doubt, just contact me :)
#
#   If you whish to contact me dm @IRRVMATOR1 on Twitter or send an email to IRRVMATOR@gmail.com

#handels connection to twitter api + tweet scheduling
import tweepy
import threading
import time
from logger import Logger
import sys

class Twitter:
    _api_connected = False
    #default twitter api disabled, only get's logged to console
    disable = True
    _tweet_scheduled = False
      
    def __init__(self,logger=None):
        self._logger = logger
        try:
            #reading tokens
            with open('twitter_token.txt') as f:
                lines = f.readlines()
            #setting up api 
            self._auth = tweepy.OAuthHandler(lines[0][:-1], lines[1][:-1])
            self._auth.set_access_token(lines[2][:-1], lines[3][:-1])
        except FileNotFoundError:
            self._log('No twitter token found')

    #send tweet directly, cancels scheduled tweet
    def tweet(self,msg):
        if self._tweet_scheduled:
            self.cancel()
        self._tweet(msg)

    #send tweet after delay    
    def schedule(self, msg, time_out=120):
        if self._tweet_scheduled:
            self.cancel()
        self._tweet_scheduled = True
        self._sc_thread = threading.Thread(target=self._sc,args=(msg,time_out))
        self._sc_thread.start()
        self._log(f'Scheduled:\n{msg}\n...Sending in {time_out}s')

    #cancel scheduled tweet           
    def cancel(self):
        if self._tweet_scheduled:
            self._log('Canceling last scheduled tweet.')
            self._tweet_scheduled = False
            self._sc_thread.join()
        
    def _tweet(self,msg):
        self._log(f'trying to send:\n{msg}')
        if self.disable:
            self._log('api diabled')
            return
        if not self._api_connected:
            self._connect_to_api()
        self._api.update_status(msg)
        self._log('Tweet sent.')
          
    def _sc(self,msg,time_out):
        while self._tweet_scheduled:
            if time_out < 0:
                self._tweet_scheduled = False
                self._tweet(msg)
                return
            time_out -= 1
            time.sleep(1)

    def _connect_to_api(self):
        try:
            self._api = tweepy.API(self._auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        except:
            self._log(f'Unexpected error:\n{sys.exc_info()[0]}')
            return
        #check api connection
        try:
            self._api.verify_credentials()
            self._log('Authentication OK')           
        except:
            #if it doesn't authenticate it breaks
            self._log('Error during authentication')
            self._log(f'Unexpected error:\n{sys.exc_info()[0]}')


    def _log(self,msg):
        if self._logger:
            self._logger.log(f'{self.__class__.__name__.upper()}: {msg}')
        else:
            print(msg)        

