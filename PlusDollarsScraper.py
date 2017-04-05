# Plus Dollar Scraper to email/SMS
# Dominic Gaiero, Josiah Pang
# Based on "Logging in with Requests" article by Stephen Brennan
# ========================================================
# Import libraries
# ========================================================
import lxml.html
import requests
from bs4 import BeautifulSoup
import re
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import *
import configparser
from twilio.rest import TwilioRestClient
import base64


# ========================================================
# Variables
# ========================================================

LOGIN_URL = "https://my.calpoly.edu/cas/login"
URL = "https://cardcenter.calpoly.edu/student/welcome.php"

# ========================================================
# Setup session variables
# ========================================================


def configSetup():
    global config, USERNAME, PASSWORD, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_SERVER
    global EMAIL_PORT, EMAIL_TO, SEND_BY, SEND_METHOD, END_DATE, SMS_ACCOUNT_SID
    global SMS_AUTH_TOKEN, SMS_SENDING_NUMBER, SMS_RECEIVING_NUMBER, IFTTT_SECRETKEY, IFTTT_EVENTNAME, DEBUG_ID
    # checks if the config file already exists
    fileExists = os.path.isfile("config.ini")
    config = configparser.ConfigParser()  # initalizes config parser
    if fileExists:  # If the file exists, then parse the fields and set to global variables
        config.read('config.ini')
        USERNAME = config['CALPOLY_CREDENTIALS']['USERNAME']
        PASSWORD = base64.b64decode(
            config['CALPOLY_CREDENTIALS']['PASSWORD']).decode("utf-8")
        EMAIL_USERNAME = config['EMAIL_SETTINGS']['LOGIN']
        EMAIL_PASSWORD = base64.b64decode(
            config['EMAIL_SETTINGS']['PASSWORD']).decode("utf-8")
        EMAIL_SERVER = config['EMAIL_SETTINGS']['SERVER']
        EMAIL_PORT = int(config['EMAIL_SETTINGS']['PORT'])
        EMAIL_TO = config['EMAIL_SETTINGS']['TO']
        SMS_ACCOUNT_SID = config['SMS_SETTINGS']['ACCOUNT_SID']
        SMS_AUTH_TOKEN = config['SMS_SETTINGS']['AUTH_TOKEN']
        SMS_SENDING_NUMBER = config['SMS_SETTINGS']['SENDING_NUMBER']
        SMS_RECEIVING_NUMBER = config['SMS_SETTINGS']['RECEIVING_NUMBER']
        IFTTT_SECRETKEY = config['IFTTT_SETTINGS']['IFTTT_SECRETKEY']
        IFTTT_EVENTNAME = config['IFTTT_SETTINGS']['IFTTT_EVENTNAME']
        DEBUG_ID = int(config['OPTIONS']['DEBUG'])
        # Makes value case insensitive
        sendBy = config['OPTIONS']['SEND_BY'].upper()
        if sendBy == "EMAIL":  # SEND_METHOD defaults to 1 (Email)
            SEND_METHOD = 1
        elif sendBy == "SMS":
            SEND_METHOD = 2
        elif sendBy == "IFTTT":
            SEND_METHOD = 3
        else:
            SEND_METHOD = 1
        END_DATE = config['OPTIONS']['END'].split(
            ",")  # Split end date into yyyy,m,d
    else:  # If the config file does not exist, this writes config.ini
        print("The following prompots will setup the config.ini file.\nThis will only run once.\n\n")
        USERNAME = input('Enter your cal poly username (with @calpoly.edu): ')
        PASSWORD = input('Enter your cal poly password: ')
        passwordEncode = base64.b64encode(
            bytes(PASSWORD, "utf-8")).decode("utf-8")
        print("If you do not want to use a third party email service, then leave the following sections blank\n")
        EMAIL_USERNAME = input(
            "Enter your email address (or leave blank for CALPOLY email) : ") or USERNAME
        EMAIL_PASSWORD = input(
            "Enter your password (or leave blank for CALPOLY password) : ") or PASSWORD
        emailPasswordEncode = base64.b64encode(
            bytes(EMAIL_PASSWORD, "utf-8")).decode("utf-8")
        EMAIL_SERVER = input(
            "Enter the email server (or leave blank for smtp.office365.com) : ") or "smtp.office365.com"
        EMAIL_PORT = input(
            "Enter the email server port (or leave blank for CALPOLY port 587) : ") or "587"
        EMAIL_TO = input(
            "Enter the receiving email address (or leave blank for CALPOLY email) : ") or USERNAME
        print("If you do not want to use Twilio SMS, then leave the following sections blank\n")
        SMS_ACCOUNT_SID = input("Enter your Twilio account SID: ")
        SMS_AUTH_TOKEN = input("Enter your Twilio auth token: ")
        SMS_SENDING_NUMBER = input("Enter your phone number (with +1): ")
        SMS_RECEIVING_NUMBER = input("Enter your Twilio number (with +1): ")
        print("If you do not want to use IFTTT, then leave the following sections blank.\n")
        IFTTT_SECRETKEY = input("Enter your IFTTT Secret Key: ")
        IFTTT_EVENTNAME = input("Enter your IFTTT Event Name: ")
        sendBy = input(
            "How do you want to recieve notifications? 'EMAIL' 'SMS' or 'IFTTT': ").upper() or "EMAIL"
        END_DATE = input(
            "What is the end date? (yyyy,m,d). No leading zeros: ") or "2017,6,16"
        if sendBy == "EMAIL":  # SEND_METHOD defaults to 1 (Email)
            SEND_METHOD = 1
        elif sendBy == "SMS":
            SEND_METHOD = 2
        elif sendBy == "IFTTT":
            SEND_METHOD = 3
        else:
            SEND_METHOD = 1
        # Dictionary for config file

        config['CALPOLY_CREDENTIALS'] = {
            'USERNAME': USERNAME, 'PASSWORD': passwordEncode}
        config['EMAIL_SETTINGS'] = {'LOGIN': EMAIL_USERNAME, 'PASSWORD': emailPasswordEncode,
                                    'SERVER': EMAIL_SERVER, 'PORT': EMAIL_PORT, 'TO': EMAIL_TO}
        config['SMS_SETTINGS'] = {
            'ACCOUNT_SID': SMS_ACCOUNT_SID, 'AUTH_TOKEN': SMS_AUTH_TOKEN, 'SENDING_NUMBER': SMS_SENDING_NUMBER, 'RECEIVING_NUMBER': SMS_RECEIVING_NUMBER}
        config['IFTTT_SETTINGS'] = {
            'IFTTT_SECRETKEY': IFTTT_SECRETKEY, 'IFTTT_EVENTNAME': IFTTT_EVENTNAME}
        config['OPTIONS'] = {'SEND_BY': sendBy, 'END': END_DATE,'DEBUG':'0'}

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    debug(1)

# ========================================================
# Scrapes balance
# ========================================================


def returnBalance():
    session_requests = requests.session()  # Initalize web session
    result = session_requests.get(LOGIN_URL)  # Get page data for login
    login_html = lxml.html.fromstring(result.text)
    # Looks for all hidden inputs (mainly for CSRF token)
    hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

# ========================================================
# Dictionary for login
# ========================================================

    # Add the hidden inputs to login dictionary
    form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}
    # Add global username and password to login dictionary
    form['username'] = USERNAME
    form['password'] = PASSWORD
    result = session_requests.post(  # post data to login URL
        LOGIN_URL,
        data=form,
    )

# =========================================================
# Scrape url
# =========================================================

    # Read data from CSGOLD page (using session)
    result = session_requests.get(URL)

    # This part should be unnecessary, but I can't seem to figure out
    # how to do it another way

    soup = BeautifulSoup(result.text, "lxml")  # Convert to regular text
    fileName = "temp.webScrape"  # Create a temp file
    f = open(fileName, "w+")  # open and fill temp file with the webbpage
    f.write(str(soup))
    f.close()
    fh = open(fileName)  # Opens file again, with different rights (r != w)
    balances = []
    for line in fh:  # Reads the webpage and looks for $xxxxxx</td>
        if re.search(r"\$.*</td>", line):
            inputData = line.rstrip().split("<")
            inputData = inputData[1].split("$")
            processedData = inputData  # Splits the data so it returns just a number
            # Adds the number to end of balances
            balances.extend(processedData)
    balance = balances[1]
    fh.close()
    try:  # Removes the temp file
        os.remove(fileName)
    except OSError:
        pass
    balance = float(balance)  # Converts str to float
    return balance

# ========================================================
# Send EMail
# ========================================================


def sendEMail(message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME  # Adds the pertinant values to msg dictionary
    msg['To'] = EMAIL_TO
    msg['Subject'] = "Your Daily Balance"
    msg.attach(MIMEText(_message, 'plain'))
    server = smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT)
    server.starttls()  # change this depending on the server requirements.
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    EMAIL_MESSAGE = msg.as_string()
    server.sendmail(EMAIL_USERNAME, EMAIL_TO, EMAIL_MESSAGE)
    server.quit()

# ========================================================
# Send SMS
# ========================================================


def sendSMS(message):

    client = TwilioRestClient(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)
    message = client.messages.create(body=_message,
                                     to=SMS_RECEIVING_NUMBER,
                                     from_=SMS_SENDING_NUMBER)
    debug("\nHeader for Twilio\n================\n{}".format(str(message)))
# ========================================================
# Send notificaiotn with IFTTT
# ========================================================


def sendIFTTT(message):

    report = {}
    report["value1"] = message
    url = "https://maker.ifttt.com/trigger/{}/with/key/{}".format(
        IFTTT_EVENTNAME, IFTTT_SECRETKEY)
    urlPost = requests.post(url, data=report)
    debug("\nHeader for IFTTT\n================\n{}".format(urlPost.status_code))

# ========================================================
# Calcualte days remaining until the end of quarter
# ========================================================


def daysUntil(year, month, day):
    today = date.today()
    # The date format has to have (a) no leading zeros and (b) must be
    # formatted yyyy,m,d
    future = date(year, month, day)
    diff = future - today
    debug("\nDate Information\n================\nToday = {}.\nFuture Day = {}\nDifference in days = {}".format(today,future,diff))
    return diff.days

# ========================================================
# Debugger
# ========================================================


def debug(message):
    if DEBUG_ID == 0:
        return()
    elif DEBUG_ID == 1:
        if message == 1:
            print("Config Settings")
            for x in config:
                print ("\n{}\n================".format(x))
                for y in config[x]:
                    print (y,':',config[x][y])
        else:
            print(message)

# ========================================================
# Main Function
# ========================================================


def main():
    configSetup()  # Run configsetup to return global variables
    balance = returnBalance()
    # Everything from config comes as str, must convert to int.
    daysLeft = daysUntil(int(END_DATE[0]), int(END_DATE[1]), int(END_DATE[2]))
    amountToday = balance / daysLeft  # Just some simple division
    endDate = "{}/{}/{}".format(END_DATE[1], END_DATE[2], END_DATE[0])
    message = "Today you have ${:,.2f} to spend.\nYou have ${:,.2f} left.\nThere are {} days left until the end date ({}).".format(
        round(amountToday, 2), round(balance, 2), daysLeft, endDate)
    debug("\nExpected Message\n================\n{}".format(message))
    if SEND_METHOD == 1:  # 1 = Email
        sendEMail(message)
    elif SEND_METHOD == 2:  # 2 = SMS
        sendSMS(message)
    elif SEND_METHOD == 3:
        sendIFTTT(message)
    debug("\n\n##End##")


if __name__ == '__main__':
    main()
