# Cal Poly CSGold Plus Dollar Web Scraper
This program is designed to scrape the Cal Poly CSGold webpage and send an email with the amount of dollars that can be spent that day. The script has no built in automation. You must either use windows task scheduler or a cron job.

This script (as of right now) is very poorly written. Please, if you know how to, make it better. There were some parts that I could not get working, and had to "hack" to get it to work. Basically, it creates a temp file with the contents of the page and then parses that. Ideally, it would just use the live page and would not require a temp file. (The temp file will get deleted once the program is done.)


Make sure you have

* lxml
* requests
* bs4
* re
* configparser
* twilio

This script will create a config file. If you don't have a config.ini file, the script will make one on its first run and then quit. Make sure that you put your username with @calpoly.edu at the end (at least for the email login).Also, the script is configured to use TLS security, so if you use another SMTP server, keep that in mind. If you do not have a twilio account, then leave that section empty on the config.ini file. Just make sure that you set the SEND_BY to 'EMAIL'. The other option is 'SMS'. The date should also be formatted yyyy,m,d (no leading zeros.)
Both of these issues will be fixed soon, as well as optimizing the script. Until then, enjoy!


### Feature List
- [ ] ~~Check contents of config.ini file to make sure it is correct~~
- [ ] ~~Check username and append '@calpoly.edu' if necessary~~
- [ ] ~~Check date format and correct if necessary~~
- [ ] Check cases the could cause script to crash
- [ ] Find out what is wrong with script and fix (it's not as easy at it seems)
- [x] Switch between text and email
