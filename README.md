# Cal Poly CSGold Plus Dollar Web Scraper
## Sends email with the amount of plus dollars left (using CSGOLD for CPSLO)
This program is designed to scrape the Cal Poly CSGold webpage and send an email with the amount of dollars that can be spent that day. The script has no built in automation. You must either use windows task scheduler or a cron job.

This script (as of right now) is very poorly written. Please, if you know how to, make it better. There were some parts that I could not get working, and had to "hack" to get it to work. Basically, it creates a temp file with the contents of the page and then parses that. Ideally, it would just use the live page and would not require a temp file. (The temp file will get deleted once the program is done.)


Make sure you have

* lxml
* requests
* bs4
* re
* configparser
* twilio

On first run, this script will run you through creating a config.ini file. When you put your username in, make sure to add the @calpoly.edu part (only necessary if you are planning on using cal poly email). If you do not want to use a third party email service or the cal poly email serivice, then leave the email part blank when going through the config file. It will fill in this information with the cal poly information, but if the send method isn't set to email, that information will not be used. If you do not have a Twilio account, then leave that section blank. If however, you do, make sure to add the country code (+1 for United States) in front of the phone number. The same applies for IFTTT. When you input the SEND_BY option, you should be able to type the input in either case, and it should correct to UPPER case. The three options are EMAIL, SMS, IFTTT. For the date formatting, it needs to be yyyy,m,d (notice no leading zeros). The password in the config.ini file in encoded with base64 so nobody can just glance at the file and determine the password.

If you want to "debug" the program. Set the debug option to 1 in the config.ini file.


### Feature List
- [x] Add base64 encoding to the password
- [ ] ~~Check contents of config.ini file to make sure it is correct~~
- [ ] ~~Check username and append '@calpoly.edu' if necessary~~
- [ ] ~~Check date format and correct if necessary~~
- [ ] Check cases the could cause script to crash
- [ ] Find out what is wrong with script and fix (it's not as easy at it seems)
- [x] Switch between text and email
