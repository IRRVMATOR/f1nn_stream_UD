
#if you read this, I'm sorry for the spagetti mess you're about to read :)
#
#for legal reasons:
#   -code is as is, no garatues given, WITHOUT ANY WARRANTY, use at your own risk
#   -do what ever you want with the code: redistribute, alter, sell, whatever
#   -when in doubt, just contact me :)
#
#   If you whish to contact me dm @IRRVMATOR1 on Twitter or send an email to IRRVMATOR@gmail.com
#

import time
from datetime import datetime
import socket
import tweepy
import select
import smtplib, ssl


x_twitter_connection = True
x_send_live_notif = True
x_email_tweets = True

#system startup time
startup_time = time.time()
log_file = "log.txt"
stream_ud = ("title","date","time")
live_notif_timeout = 0

def _init():
    log(f'Bot started at {datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")}')
    log("###################################################################################")

    #dumb banner on startup
    try:
        from pyfiglet import Figlet
        custom_fig = Figlet(font='slant')
        print(custom_fig.renderText('f1nn twitter bot'))
    except:
        log("Intstall the packet pyfiglet if you want a cool big text banner")
    
    sock = connect_twtich_irc()
    last_irc_msg = startup_time

    #store last time f3mmbot said anthing about stream
    last_update = ""
    
    try:
        with open('last_update.txt') as f:
            last_update = f.readline()
        log(f'Read "{last_update}" from cache')
    except FileNotFoundError:
        log("no cache found")
    
    #delay between new "!stream"-message and actually sending tweet
    #allows for a bit of time, so mods can actually set it up and stuff
    tweet_delay = 120
    time_last_update = 0
    send_tweet_flag = False

    log("Entring main loop")
    while True:
        #uptime display
        print(f"{get_ts()}IRC timeout in {int(1000-(time.time()-last_irc_msg)):04d}s\r",end='')
        tic = time.time()
        sock.setblocking(0)
        #waits 10s for new messages, returns before 10s elapse if messsage received or connection down
        ready = select.select([sock],[],[],10)
        toc = time.time()
        
        if ready[0]:
            #update time
            last_irc_msg = time.time()    
            #get messages from irc
            try:
                resp = sock.recv(2048).decode('utf-8')
            except ConnectionResetError:
                sock = connect_twtich_irc(sock)
                last_irc_msg = time.time()

            #check if f3mmbot message and cut it down a bit 
            msg = handle_raw_message(resp)

            #send live notif if more than 30min since last live notif
            if x_send_live_notif and msg and "F1NN5TER just went live!" in msg and time.time()-live_notif_timeout > 1800:
                send_tweet("F1NN just went live\nhttps://www.twitch.tv/f1nn5ter")
                live_notif_timeout = time.time()

            #found scedule message    
            elif msg and "The next stream will be" in msg:
                log(f'Received stream update:"{msg}"')
                #check if scedule changed
                if not msg == last_update:
                    log('New stream update :)')
                    last_update = msg
                    time_last_update = time.time()
                    send_tweet_flag = True
                else:
                    log('Known stream update :(')
            
            #hack to deal with diconnects
            if not resp and toc -tic < 9:
                sock= connect_twtich_irc(sock)
                last_irc_msg = time.time()

        #send tweet after no change in 2 minutes
        if send_tweet_flag and time.time() - time_last_update > tweet_delay:
            #save last sent tweet to file, to prevent resending tweet after restart
            with open('last_update.txt','w') as f:
                f.write(last_update)
            #parse parameter from f3mmbot msg and check for filtered words
            if parse_stream_ud_info(last_update[24:-22]) and check_filters():
                send_tweet(f'Title {stream_ud[0]}\nDate  {stream_ud[1]}\nTime  {stream_ud[2]} UK Time')
                log("TWEET: "+ last_update)
            #regardless if tweet sent, mark as don't send again
            send_tweet_flag = False

        #attempt to reconnect to twitch, if no new message for 1000s (ca. 17min)
        #expecting at least one f3mmbot message every 15 min (hydration notif + discord link)
        if time.time()-last_irc_msg > 1000:
            log("IRC timeout")
            sock = connect_twtich_irc(sock)
            last_irc_msg = time.time()
          
    sock.close()


#TWITTER
############################################################################
def send_tweet(msg):
    global x_twitter_connection
    if x_email_tweets:
        send_mail(msg)
    if x_twitter_connection:
        try:
            #reading tokens
            with open('twitter_token.txt') as f:
                lines = f.readlines()

            #setting up api 
            auth = tweepy.OAuthHandler(lines[0][:-1], lines[1][:-1])
            auth.set_access_token(lines[2][:-1], lines[3][:-1])
            api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

            #check api connection
            try:
                api.verify_credentials()
                log("Twitter: Authentication OK")

                #sending tweet
                api.update_status(msg)
                
            except:
                log("Twitter: Error during authentication")
                log("Unexpected error:", sys.exc_info()[0])

                #better be careful than get api access blocked again 
                send_mail("Sending tweet failed, disabling twitter api for now")
                x_twitter_connection = False
                
                

        except FileNotFoundError:
            log('No twitter token found')

#TWICH
############################################################################
def connect_twtich_irc(old_sock=False):
    #try correctly closing connection, if reconnect
    if old_sock:
        log("Attempting to reconnect")
        old_sock.close()
        
    while True:
        try:
            #text file. First line is twitch nickname. Second line is oauth token
            with open('twitch_token.txt') as f:
                lines = f.readlines()

            nickname = lines[0][:-1]
            token = lines[1][:-1]
            channel = '#f1nn5ter'

            sock = socket.socket()
            log(f"Connecting to IRC Channel: {channel}")
            sock.connect(('irc.chat.twitch.tv', 6667))

            sock.send(f"PASS {token}\n".encode('utf-8'))
            sock.send(f"NICK {nickname}\n".encode('utf-8'))
            sock.send(f"JOIN {channel}\n".encode('utf-8'))
            #return on successful connection
            log(f"Connection Successful")
            return sock
        except ConnectionResetError:
            time.sleep(20)
    

#EMAIL
############################################################################
def send_mail(msg):
    try:
        #read credentials from file
        with open('email_credetials.txt') as f:
            lines = f.readlines()
        log(f'Trying to send mail: {msg}')
        sender_email = lines[0][:-1]
        receiver_email = lines[1][:-1]
        pw = lines[2][:-1]
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, pw)
            server.sendmail(sender_email, receiver_email, msg)
        log("Mail sent.")
    except FileNotFoundError:
        log('No mail credetials')
    except:
        log(f'Sending mail "{msg}" failed')

#will return after one stream update message is found
def handle_raw_message(resp):
    #split if multiple messages
    lines = resp.split("\n")
    #go through messages
    for line in lines:
        #ignore empty lines
        if len(line) > 0:
            #check if actual chat message
            if line[0] == ":" and len(line.split(":",2)) > 2:
                #get twitch nick name
                nick = (line.split("!",1)[0])[1:]
                #full chat log, for debugging only, bloates log file
                #log(f'{nick}: \t{line.split(":",2)[2]}',False,True)
                #only look at f3mmbot messages
                if nick == "f3mmbot":
                    #get message
                    msg = line.split(":",2)[2]
                    #log received f3mmbot messages for debugging
                    log(f'Found f3mmbot message: "{msg}"',False,True)
                    #ignore hydration notif etc
                    return msg[8:-1]
    return False

    
  
#write message to terminal and/or log file, also returns log string
def log(msg, x_terminal=True, x_log=True):
    #timestamp log messages
    log = f"{get_ts()}{msg}"
    log = log.replace('\n','; ')
    #print to terminal
    if x_terminal:    
        print(log)
    #write to log file
    if x_log:
        with open(log_file, "a") as file:
            try:
                file.write(log+'\n')
            #skip logging if unsupported characters
            except UnicodeEncodeError:
                print(f'{get_ts()}Skipped one message due to charset incompatibility')
    return log

#returns string time stamp
def get_ts():
    cur = int(time.time()-startup_time)
    h = ''
    if int(cur/3600) < 100:
        h = f'{int(cur/3600):02d}'
    else:
        h = f'{int(cur/3600)}'
    m = f'{int((cur%3600)/60):02d}'
    s = f'{int(cur%60):02d}'
    return f'{datetime.now().strftime("%H:%M:%S")} [{h}-{m}-{s}] '

#reads parameters from cut down message
#formatr needs to  be like this:
#"undefined" on undefined at undefined UK time
def parse_stream_ud_info(msg):
    try:
        global stream_ud
        #title = string between first " and last "
        title = msg[msg.index('"')+1:len(msg)-msg[::-1].index('"')-1]
        log(f'Title: {title}')
        #date = string between on and at (read backwards, to avoid triggering if 'on' or 'at' in title)
        date = msg[len(msg)-msg[::-1].index(" on "[::-1]):len(msg)-msg[::-1].index(" at "[::-1])-4]
        log(f'Date:  {date}')
        #time = string after 'at', with end (' UK time') cut off
        time = msg[len(msg)-msg[::-1].index(" at "[::-1]):-8]
        log(f'Time:  {time}')
        stream_ud =(title,date,time)
        return True
    except ValueError:
        log(f'Parsing "{msg}" went wrong')
        return False

#checks stream_ud for filtered words, only applies to date parameter
#returns true if no filtered word found or no filter file found
def check_filters():
    try:
        #load filter file
        with open('filter.txt') as f:
            lines = f.readlines()
        #make all lower case (case insensitive)
        date = stream_ud[1].lower()
        #check each filtered word
        for line in lines:
            if line[:-1].lower() in date:
                log(f'Filter: "{line[:-1].lower()}" found. Skipping tweet.')
                return False
        log('Filter: OK')
        return True
    #skip filtering if no filter file
    except FileNotFoundError:
        log('No Filter file found')
        return True


try:   
    _init()
#catch all crash notif
except:
    send_mail('Something went wrong, bot crashed')
    log("Unexpected error:", sys.exc_info()[0])
    
#Did you actually read the entire code? Hopefully you just scrolled down lol
