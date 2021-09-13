#for legal reasons:
#   -code is as is, no garatues given, WITHOUT ANY WARRANTY, use at your own risk
#   -do what ever you want with the code: redistribute, alter, sell, whatever
#   -when in doubt, just contact me :)
#
#   If you whish to contact me dm @IRRVMATOR1 on Twitter or send an email to IRRVMATOR@gmail.com

#here's the main...
#run this if you want to run the bot, python3 btw

from logger import Logger
from schedule_info import Schedule_info
from twitch import Twitch
from twitter import Twitter
from mail import Mail
import time
import copy
import select
import sys

#random string to disable live notif
LIVE_NOTIF = '87945894375947575678887667575675756765390875948075349085793'#'F1NN5TER just went live!'
LIVE_TWEET = 'F1NN just went live\nhttps://www.twitch.tv/f1nn5ter'

IRC_USER_FILTER = 'f3mmbot'
SCHEDULE_INFO_TAG = 'The next stream will be'
SCHEDULE_PARAMETER_CHANGE_TAG = 'Set the stream'

#log with realative time
logger = Logger(startup_time=time.time())
logger.log('Bot started')

#stream info
si = Schedule_info()
#other stream info... to compare 
so = Schedule_info()
#see if cached schedule there and load
try:
    si.read_from_file('cached_schedule.txt')
    logger.log(f'Read schedule from file:\n{str(si)}')
except FileNotFoundError:
    logger.log('No chached schedule found')

#connect to twitch irc
twitch = Twitch(logger, channel = '#f1nn5ter')
#connect to twitter api
twitter = Twitter(logger)
#enable twitter api... yeah i know this shit is backwards as hell...
twitter.disable = False

def _init():
    global si
    global so

    #cache time when live notif was send, to avoid spamming it
    last_live_notif = 0

    #main loop
    while True:
        #timestamp message, only properly works in terminal/cmd... idle console doesn't like it
        print(f'{logger.get_ts()}{twitch.time_out_msg()}\r',end='')

        #work through messages on buffer
        while twitch.has_new():
            #pop message
            nick,msg = twitch.pop()
            #filter user for f3mmbot
            if nick == IRC_USER_FILTER:
##                #if he goes live
##                if LIVE_NOTIF in msg:
##                    #send tweet if last live notif was ... a while a ago
##                    #whatever it's disbled anyway
##                    if time.time()-last_live_notif > 3800: 
##                        logger.log('F1nn went live. Sending tweet.')
##                        twitter.tweet(LIVE_TWEET)
##                        last_live_notif = time.time()
##                    else:
##                        logger.log(f'Not tweeting live notif. Last one was only {str(int(time.time()-last_live_notif))}s ago.')

                #handle !stream message    
                if SCHEDULE_INFO_TAG in msg:
                    so = Schedule_info(msg)
                    try_send_tweet()
                #handle single parameter update        
                if SCHEDULE_PARAMETER_CHANGE_TAG in msg:
                    so = copy.copy(si)
                    so.parse_single_param_ud(msg)
                    try_send_tweet()
        #free up some cpu...
        time.sleep(1)

#check if tweet should actully be sent        
def try_send_tweet():
    global si
    #only do shit if something has changed
    if si != so:
        si = copy.copy(so)
        #format tweet
        tweet = f"'{si.title}' on {si.date} at {si.time} UK Time"
        logger.log(f'Stream schedule update:\n{tweet}')
        #filter certain words
        if check_filters(si):
            #do the actual sending... well scheduling the tweet at least
            logger.log('Preparing to send tweet')
            twitter.schedule(tweet)
            si.write_to_file('cached_schedule.txt')
        #cancel tweet if filter found
        else:
            twitter.cancel()
    else:
        logger.log('Received schedule. Nothing new :(')

#filters date paramter 
def check_filters(si):
    try:
        #load filter file, do every time it is used
        #makes filter update while bot running possible
        #not gonna be called that often
        with open('filter.txt') as f:
            lines = f.readlines()
        #make case insensitive
        date = si.date.lower()
        #check each filtered word
        for line in lines:
            if line[:-1].lower() in date:
                logger.log(f'FILTER: "{line[:-1].lower()}" found. Skipping tweet.')
                return False
        logger.log('FILTER: OK')
        return True
    #skip filtering if no filter file
    except FileNotFoundError:
        logger.log('FILTER: No Filter file found')
        return True

try:
    _init()
except KeyboardInterrupt:
    #"properly" shutting down
    logger.log('MAIN: Prepearing for shutdown')
    logger.log('MAIN: Closing twitter module')
    twitter.cancel()
    logger.log('MAIN: Closing twitch module')
    twitch.close()
    logger.log('MAIN: bye... :\'(')
except:
    #try to send mail on crash
    logger.log('MAIN: Bot crashed, trying to send mail notif')
    mail = Mail(logger)
    mail.send('Bot Crashed','Yo man, the bot crashed. Look at it. Right now.')
