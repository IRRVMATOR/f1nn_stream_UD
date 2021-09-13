#for legal reasons:
#   -code is as is, no garatues given, WITHOUT ANY WARRANTY, use at your own risk
#   -do what ever you want with the code: redistribute, alter, sell, whatever
#   -when in doubt, just contact me :)
#
#   If you whish to contact me dm @IRRVMATOR1 on Twitter or send an email to IRRVMATOR@gmail.com

#handles connecetion to twitch irc and buffers messages
from logger import Logger
import threading
import select
import time
import socket

class Twitch:
    #default timeout just over 5min
    #twitch irc pings every 5min
    time_out = 330

    TWITCH_PING = 'PING :tmi.twitch.tv'
    TWITCH_PONG = 'PONG :tmi.twitch.tv\r\n'
    TWITCH_WELCOME_MSG = 'Welcome, GLHF!'

    #[(nickname,message),(nickname,message),(nickname,message)]
    _in_buffer = []
    _rc_active = False
    
    def __init__(self,logger=None, channel='#f1nn5ter', token_file='twitch_token.txt'):
        self._logger = logger
        self.channel = channel
        self._last_contact = time.time()
        
        try:
            with open(token_file) as f:
                lines = f.readlines()
            self.nickname = lines[0][:-1]
            self._log(f'Nick set to {self.nickname}')
            self.token = lines[1][:-1]
            self._log(f'Auth set to {self.token}')

            #initial connect
            self._connect()
            self._start_receive()
        
        except FileNotFoundError:
            self._log(f'Please provide twitch token as {token_file}')

    #pop irc message from buffer
    def pop(self):
        if len(self._in_buffer) > 0:
            return self._in_buffer.pop()

    #true if there is something on the buffer
    def has_new(self):
        return len(self._in_buffer) > 0

    #timestamp for console
    def time_out_msg(self):
        return f'IRC timeout in {int(self.time_out-(time.time()-self._last_contact)):03d}s'

    #closes connection to IRC... duh
    def close(self):
        if self._rc_active:
            self._stop_rc()
        if self._sock:
            self._sock.close()
        
            

    def _connect(self):
        #retry until connected
        while True:
            try:
                self._sock = socket.socket()
                self._log(f'Connecting to IRC Channel: {self.channel}')
                self._sock.connect(('irc.chat.twitch.tv', 6667))
                self._sock.send(f'PASS {self.token}\n'.encode('utf-8'))
                self._sock.send(f'NICK {self.nickname}\n'.encode('utf-8'))
                self._sock.send(f'JOIN {self.channel}\n'.encode('utf-8'))
                #check if actually connected, might drop some messages tho
                ready = select.select([self._sock],[],[],10)
                if ready[0]:
                    resp = self._sock.recv(2048).decode('utf-8')
                    lines = resp.split("\n")
                    for line in lines:
                        if self.TWITCH_WELCOME_MSG in line:   
                            self._log(f"Connection Successful")
                            self._last_contact = time.time()
                            #return on successful connection
                            return
            except:
                #10s timeout
                self._log('Connecting to IRC failed. Retrying in 10s')
                time.sleep(10)
                

    def _start_receive(self):
        self._log('Starting receive thread')
        self._rc_thread = threading.Thread(target=self._rc)
        self._rc_thread.start()
        self._log('Receive thread now active')

    def _stop_rc(self):
        self._log('Stopping receive thread')
        self._rc_active = False
        self._rc_thread.join()
        self._log('Receive thread successfully stopped')

    #receive thread
    def _rc(self):
        self._rc_active = True
        
        #2nd logger for chat log
        #raw_logger = Logger("chat_log.txt")
        #raw_logger.x_log_to_terminal = False
        
        while self._rc_active:
            tic = time.time()
            self._sock.setblocking(0)
            #waits 1s for new messages, returns before 1s elapse if messsage received or connection down
            ready = select.select([self._sock],[],[],1)
            toc = time.time()
            #if no msg + less than 1s 
            if not ready[0] and toc-tic<1:
                self._log('Cocket closed')
                self._connect()
            #if msg 
            if ready[0]:
                #update time
                self._last_contact = time.time()    
                #get messages from irc
                try:
                    resp = self._sock.recv(2048).decode('utf-8')
                    lines = resp.split("\n")
                    for line in lines:
                        #respond to ping
                        if self.TWITCH_PING in line:
                            self._sock.send(self.TWITCH_PONG.encode('utf-8'))
                        #only add twitch messages
                        if len(line) > 0 and line[0] == ":" and len(line.split(":",2)) > 2:
                            #write to buffer as tuple (nickname,message)
                            self._in_buffer.append(((line.split("!",1)[0])[1:],line.split(":",2)[2]))
                            #raw_logger.log(line)
                except ConnectionResetError:
                    self._log('ConnectionResetError')
                    self._connect()
            #reconnect on timeout        
            if self.time_out-(time.time()-self._last_contact) < 0:
                self._log(f'IRC timed out after {self.time_out}s')
                self._connect()


    def _log(self,msg):
        if self._logger:
            self._logger.log(f'{self.__class__.__name__.upper()}: {msg}')
        else:
            print(msg)
            
