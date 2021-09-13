#for legal reasons:
#   -code is as is, no garatues given, WITHOUT ANY WARRANTY, use at your own risk
#   -do what ever you want with the code: redistribute, alter, sell, whatever
#   -when in doubt, just contact me :)
#
#   If you whish to contact me dm @IRRVMATOR1 on Twitter or send an email to IRRVMATOR@gmail.com

import smtplib, ssl
#ignore this, this is mainly for debugging
#it sends emails... pretty boring anyway
class Mail:
    def __init__(self, creds_file='email_credetials.txt',logger=None):
        self.logger = logger
        with open('email_credetials.txt') as f:
            lines = f.readlines()
        self.sender = lines[0][:-1]
        self.receiver = lines[1][:-1]
        self.pw = lines[2][:-1]
        
    def send(self,subject='',msg=''):
        if len(msg)+len(subject)<1:
            self._log('No. I\'m not sending an empty mail. Fuck you')
            return
        mail = f'Subject: {subject}\n\n{msg}'
     
        try:
            self._log(f'Trying to send mail: {msg}')
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(self.sender, self.pw)
                server.sendmail(self.sender, self.receiver, mail)
            self._log('Mail sent.')
        except Exception as e:
            self._log(str(e))
        

    def _log(self,msg):
        if self.logger:
            self.logger.log(f'{self.__class__.__name__.upper()}: {msg}')
        else:
            print(msg)


