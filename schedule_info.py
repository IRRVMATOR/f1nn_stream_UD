#for legal reasons:
#   -code is as is, no garatues given, WITHOUT ANY WARRANTY, use at your own risk
#   -do what ever you want with the code: redistribute, alter, sell, whatever
#   -when in doubt, just contact me :)
#
#   If you whish to contact me dm @IRRVMATOR1 on Twitter or send an email to IRRVMATOR@gmail.com

#basically stores the !stream message
import copy
class Schedule_info:
    #defaults
    title = 'undefined'
    date = 'undefined'
    time = 'undefined'
    
    def __init__(self, title_or_msg=False, date=False, time=False):
        #no parameters -> leave defautls
        if not title_or_msg:
            return
        #if only title_or_msg assume it's the entire !stream message
        if not date and not time:
            vals = self._parse_from_message(title_or_msg)
            self.title = vals[0]
            self.date = vals[1]
            self.time = vals[2]
        #throw error on invalid combo... at least some error handling here...
        elif (not date and time) or (not time and date):
            raise TypeError('Either pass twitch message as first parameter or use all parameters') 
        #copy individual paramters 
        else:
            self.title = title_or_msg
            self.date = date
            self.time = time

    #custom to_string
    def __str__(self):
        return f'Title {self.title}\nDate  {self.date}\nTime  {self.time} UK Time'

    #custom =
    def __eq__(self,other):
        return self.title == other.title and self.date == other.date and self.time == other.time

    #custom !=
    def __ne__(self,other):
        return (not self.title == other.title) or (not self.date == other.date) or (not self.time == other.time)

    #custom copy
    def __copy__(self):
        return Schedule_info(self.title, self.date, self.time)
    
    #parse paramters from f3mmbot message
    def _parse_from_message(self,msg):
        #message format:
        #ACTION The next stream will be "GIRL MONTH DAY UNO" on Monday 9th at 8 PM UK time. Stream Hype!

        msg = msg[8:-1]
        #The next stream will be "GIRL MONTH DAY UNO" on Monday 9th at 8 PM UK time. Stream Hype!

        #GIRL MONTH DAY UNO
        title = msg[msg.index('"')+1:len(msg)-msg[::-1].index('"')-1]
        #Monday 9th
        date = msg[len(msg)-msg[::-1].index(" on "[::-1]):len(msg)-msg[::-1].index(" at "[::-1])-4]
        #8 PM
        time = msg[len(msg)-msg[::-1].index(" at "[::-1]):-23]
        return (title,date,time)

    #parse singel parameter, if schedule is updated
    def parse_single_param_ud(self, msg):
        if "Set the stream" in msg:
            #ACTION Set the stream title to PO BOXS GAMERS
            if "Set the stream title to" in msg:
                self.title = msg[32:-2]
            #ACTION Set the stream day to Tuesday 10th
            elif "Set the stream day to" in msg:
                self.date = msg[30:-2]
            #ACTION Set the stream time to 8:30 PM
            elif "Set the stream time to" in msg:
                self.time = msg[31:-2]
        
    #save to file, to avoid tweeting same thing twice, if bot needs to be restarted
    def write_to_file(self,file_name):
        with open(file_name,'w') as f:
            f.write(str(self))
            
    #read from file
    def read_from_file(self,file_name):
        with open(file_name) as f:
            lines = f.readlines()
        self.title = lines[0][6:-1]
        self.date = lines[1][6:-1]
        self.time = lines[2][6:-8]
