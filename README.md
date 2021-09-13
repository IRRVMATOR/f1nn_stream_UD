# f1nn_stream_UD
Source code and description for the Twitter bot @f1nn_stream_UD
Tip (I guess): I have notificaitons for that twitter account turned on, so i get a notification anytime there is an update to the stream schedule

Ok so here is the code for the twitter bot. If it breaks or you have any suggestions or complaints, feel free to dm me on twitter @IRRVMATOR1 or shoot me an email at IRRVMATOR@gmail.com (tho I would prefer twitter dms).
Had the thing running for a few weeks by now and it seems to work quite well... I'm shure there are still a ton of bugs and they will be fixed once I find them. If you see any big mistakes, please tell me. 


So here is how this thing works really quickly:
-i have a twitch account lurking in f1nns twitch chat
-if someone uses the !stream command or the mods use the !set commands to update the paramters for the !stream command my bot parses it
  
  person  : !stream
  f3mmbot : The next stream will be "PO BOXS GAMERS" on today at 8:30 PM UK time. Stream Hype!
  
  or
  
  mod     : !setday today  
  f3mmbot : Set the stream day to today
  mod     : !settime 8:30 PM
  f3mmbot : Set the stream time to 8:30 PM
  mod     : !settitle PO BOXS GAMERS
  f3mmbot : Set the stream title to PO BOXS GAMERS
  
  ==> stream_info(title='PO BOXS GAMERS', date='today', time='8:30 PM')
  
-if there is new info it checks it's filters
  e.g. it's not gonna send a tweet if the day is set to 'undefined'
-if it passes the filters, a tweet is scheduled for 2min after that (this is to give the mods some time to update all of the parameters)
  (don't want the bot to send something like: 'unknown' on today at unknown UK time)
-that's basically it. pretty simple huh? well kinda, there's a bit more to it... if you really wanna know how it works take a look at the source


How to run:
the main loop is in main.py...duh... also it's python3. Just in case you want to run it, there are a few text files that need some keys and stuff: 
-you need to provide the oauth token to a twitch account so the bot can lurk in twitch irc. 
-it also needs the tokens for a twitter account (you only get these if you request api access from twitter)
-lastly i use email for debugging, so it needs access to an email account, should work with most, i personally use gmail (that needs bot access enabled however)

:)
