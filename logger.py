#for legal reasons:
#   -code is as is, no garatues given, WITHOUT ANY WARRANTY, use at your own risk
#   -do what ever you want with the code: redistribute, alter, sell, whatever
#   -when in doubt, just contact me :)
#
#   If you whish to contact me dm @IRRVMATOR1 on Twitter or send an email to IRRVMATOR@gmail.com

#it's a logger
#it logs
#why did i write a logger myself when there are prefectly good libraries out there?
#i don't know man... but here it is
class Logger:
    log_file = "log.txt"

    #toggles for output to terminal and file
    x_log_to_file = True
    x_log_to_terminal = True
    #timestamp relative to startup time
    x_relative_ts = False
    #timestamp
    x_absolute_ts = True
    startup_time = False
    date_format = "%Y|%m|%d - %H:%M:%S"

    #set startup_time for relative ts
    def __init__(self, log_file=False, startup_time=False):
        if log_file:
            self.log_file = log_file
        if startup_time:
            self.startup_time = startup_time
            self.x_relative_ts = True

    #log...         
    def log(self, msg, x_t=None, x_f=None):
        ts = self.get_ts()
        ls = f"{ts}{msg}"
        ls = ls.replace('\n',f'\n{ts}')
        #default to class attributes
        if x_t is None:
            x_t = self.x_log_to_terminal
        if x_f is None:
            x_f = self.x_log_to_file

        if x_t:
            self._log_terminal(ls)
        if x_f:
            self._log_file(ls)
        return ls
            
        
    def _log_terminal(self,ls):
        print(ls)

    def _log_file(self,ls):
        ls = ls.replace('\n','; ')
        with open(self.log_file, "a") as file:
            try:
                file.write(ls+'\n')
            #skip logging if unsupported characters
            except UnicodeEncodeError:
                self.log(f'{self.__class__.__name__.upper()}: Skipped logging message to file. Charset Incompatible')


    def get_ts(self):
        import time
        from datetime import datetime
        ts =''
        if self.x_absolute_ts:
            ts += f'{datetime.now().strftime(self.date_format)} '
        
        if self.x_relative_ts:
            cur = int(time.time()-self.startup_time)
            h = ''
            if int(cur/3600) < 100:
                h = f'{int(cur/3600):02d}'
            else:
                h = f'{int(cur/3600)}'
            m = f'{int((cur%3600)/60):02d}'
            s = f'{int(cur%60):02d}'
            ts += f'[{h}-{m}-{s}] '
        return ts

