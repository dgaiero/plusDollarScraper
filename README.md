# Cal Poly CSGold Plus Dollar Web Scraper
Hey! This program is designed to scrape the Cal Poly CSGold webpage and send an email with the amount of dollars that can be spent that day. I have it automated through Windows Task Scheduler to send me an email every morning at 12:00 AM. I'm sure you could do a cron job on linux for the same thing.

This script (as of right now) is very poorly written. Please, if you know how to, make it better. There were some parts that I could not get working, and had to "hack" to get it to work.

It also requires a fair amount of libraries

Make sure you have

* lxml
* requests
* bs4
* re
* configparser

This script will create a config file for CREDENTIALS. if you don't have a config.ini file, the script will make one on its first run and then quit. Make sure that you put your username with @calpoly.edu at the end, otherwise the script will fail. The date should also be formatted yyyy,m,d (no leading zeros.)
Both of these issues will be fixed soon, as well as optimizing the script. Until then, enjoy!


### Feature List
- [ ] Check contents of config.ini file to make sure it is correct
- [ ] Check username and append '@calpoly.edu' if necessary
- [ ] Check date format and correct if necessary
- [ ] Check cases the could cause script to crash
- [ ] Find out what is wrong with script and fix (it's not as easy at it seems)