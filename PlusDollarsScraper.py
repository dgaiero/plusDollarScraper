# CPSLO Plus Dollar Scraper to various web services
# Dominic Gaiero, Josiah Pang
# Based on "Logging in with Requests" article by Stephen Brennan

# ========================================================
# Import libraries
# ========================================================


import os
import sys
from datetime import *
import urllib.request
import base64
from getpass import getpass

import configparser
import lxml.html
import requests
import re
import smtplib
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import TwilioRestClient
from pushbullet import Pushbullet

# ========================================================
# Variables
# ========================================================


LOGIN_URL = "https://my.calpoly.edu/cas/login"
URL = "https://cardcenter.calpoly.edu/student/welcome.php"
ON_TARGET = "https://www.calpolydining.com/diningprograms/freshman/plusdollars/"

# ========================================================
# Run config file and setup global variables
# ========================================================


def configSetup():
    global config, USERNAME, PASSWORD, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_SERVER
    global EMAIL_PORT, EMAIL_TO, SEND_BY, SEND_METHOD, END_DATE, SMS_ACCOUNT_SID, PB_API
    global SMS_AUTH_TOKEN, SMS_SENDING_NUMBER, SMS_RECEIVING_NUMBER, IFTTT_SECRETKEY, IFTTT_EVENTNAME, DEBUG_ID
    fileExists = os.path.isfile("config.ini")
    config = configparser.ConfigParser()
    if fileExists:
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
        sendBy = config['OPTIONS']['SEND_BY'].upper()
        PB_API = config['PUSHBULLET']['API']
        SEND_METHOD = sendMethod(sendBy)
        END_DATE = config['OPTIONS']['END'].split(
            ",")
    else:
        print("The following prompots will setup the config.ini file.\nThis will only run once.\n\n")
        USERNAME = input('Enter your cal poly username (with @calpoly.edu): ')
        PASSWORD = getpass('Enter your cal poly password (The password will be invisible): ')
        passwordEncode = base64.b64encode(
            bytes(PASSWORD, "utf-8")).decode("utf-8")
        sendBy = input(
            "How do you want to recieve notifications? 'EMAIL' 'SMS' 'IFTTT' or 'PB': ").upper() or "EMAIL"
        SEND_METHOD = sendMethod(sendBy)


        EMAIL_USERNAME = USERNAME
        EMAIL_PASSWORD = PASSWORD
        emailPasswordEncode = base64.b64encode(
            bytes(EMAIL_PASSWORD, "utf-8")).decode("utf-8")
        EMAIL_SERVER = "smtp.office365.com"
        EMAIL_PORT = "587"
        EMAIL_TO = USERNAME
        SMS_ACCOUNT_SID = ""
        SMS_AUTH_TOKEN = ""
        SMS_SENDING_NUMBER = ""
        SMS_RECEIVING_NUMBER = ""
        IFTTT_SECRETKEY = ""
        IFTTT_EVENTNAME = ""
        PB_API = ""

        if SEND_METHOD == 1:
            EMAIL_USERNAME = input(
                "Enter your email address (or leave blank for CALPOLY email) : ") or USERNAME
            EMAIL_PASSWORD = getpass(
                "Enter your password (or leave blank for CALPOLY password) (The password will be invisible): ") or PASSWORD
            emailPasswordEncode = base64.b64encode(
                bytes(EMAIL_PASSWORD, "utf-8")).decode("utf-8")
            EMAIL_SERVER = input(
                "Enter the email server (or leave blank for smtp.office365.com) : ") or "smtp.office365.com"
            EMAIL_PORT = input(
                "Enter the email server port (or leave blank for CALPOLY port 587) : ") or "587"
            EMAIL_TO = input(
                "Enter the receiving email address (or leave blank for CALPOLY email) : ") or USERNAME
        elif SEND_METHOD == 2:
            SMS_ACCOUNT_SID = input("Enter your Twilio account SID: ")
            SMS_AUTH_TOKEN = input("Enter your Twilio auth token: ")
            SMS_SENDING_NUMBER = input("Enter your phone number (with +1): ")
            SMS_RECEIVING_NUMBER = input("Enter your Twilio number (with +1): ")
        elif SEND_METHOD ==3:
            IFTTT_SECRETKEY = input("Enter your IFTTT Secret Key: ")
            IFTTT_EVENTNAME = input("Enter your IFTTT Event Name: ")
            print("If you do not want to use Push Bullet, then leave the following sections blank.\n")
        elif SEND_METHOD ==4:
            PB_API = input("Enter your PushBullet API Key: ")
        else:
            pass
        END_DATE = input(
            "What is the end date? (yyyy,m,d). No leading zeros: ") or "2017,6,16"
        DEBUG_ID = input("Do you want to turn on DEBUG MODE? Enter 1 if yes: ") or 0

        DEBUG_ID = 0

        config['CALPOLY_CREDENTIALS'] = {
            'USERNAME': USERNAME, 'PASSWORD': passwordEncode}
        config['EMAIL_SETTINGS'] = {'LOGIN': EMAIL_USERNAME, 'PASSWORD': emailPasswordEncode,
                                    'SERVER': EMAIL_SERVER, 'PORT': EMAIL_PORT, 'TO': EMAIL_TO}
        config['SMS_SETTINGS'] = {
            'ACCOUNT_SID': SMS_ACCOUNT_SID, 'AUTH_TOKEN': SMS_AUTH_TOKEN, 'SENDING_NUMBER': SMS_SENDING_NUMBER, 'RECEIVING_NUMBER': SMS_RECEIVING_NUMBER}
        config['IFTTT_SETTINGS'] = {
            'IFTTT_SECRETKEY': IFTTT_SECRETKEY, 'IFTTT_EVENTNAME': IFTTT_EVENTNAME}
        config['PUSHBULLET'] = {'API': ''}
        config['OPTIONS'] = {'SEND_BY': sendBy, 'END': END_DATE, 'DEBUG': DEBUG_ID}

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    debug(1)

# ========================================================
# Send By
# ========================================================


def sendMethod(sendBy):
    # SEND_METHOD defaults to 1 (Email)
    if sendBy == "EMAIL":
        SEND_METHOD = 1
    elif sendBy == "SMS":
        SEND_METHOD = 2
    elif sendBy == "IFTTT":
        SEND_METHOD = 3
    elif sendBy == "PB":
        SEND_METHOD = 4
    else:
        SEND_METHOD = 1
    return SEND_METHOD
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

    result = session_requests.get(URL)

    '''
    This part should be unnecessary, but I can't seem to figure out
    how to do it another way
    '''

    soup = BeautifulSoup(result.text, "lxml")
    fileName = "temp.webScrape"
    fh = open(fileName, "w+")
    fh.write(str(soup))
    fh.close()
    fh = open(fileName)
    balances = []
    for line in fh:  # Reads the webpage and looks for $xxxxxx</td>
        if re.search(r"\$.*</td>", line):
            inputData = line.rstrip().split("<")
            inputData = inputData[1].split("$")
            processedData = inputData
            balances.extend(processedData)
    try:
        balance = balances[1]
        balance = float(balance)
    except IndexError:
        balance = "ERR"
    fh.close()
    try:
        os.remove(fileName)
    except OSError:
        pass
    return balance

# ========================================================
# Return on target per day budget - In the works
# ========================================================


def onTarget():
    page = urllib.request.urlopen(ON_TARGET)
    page = requests.get(ON_TARGET)
    time.sleep(10)
    soup = BeautifulSoup(page, 'html.parser')
    # Add plusdollars-apartment to config to change between apartment and non
    # apartment
    targetBalance_box = soup.find(
        'span', attrs={'class': 'plusdollars-apartment'})
    targetBalance = targetBalance_box.text.strip()
    print(targetBalance)

# ========================================================
# Send EMail
# ========================================================


def sendEMail(title, message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME  # Adds the pertinant values to msg dictionary
    msg['To'] = EMAIL_TO
    msg['Subject'] = title
    msg.attach(MIMEText(message, 'plain'))
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
    message = client.messages.create(body=message,
                                     to=SMS_RECEIVING_NUMBER,
                                     from_=SMS_SENDING_NUMBER)
    debug("\nHeader for Twilio\n================\n{}".format(str(message)))


# ========================================================
# Send PushBullet
# ========================================================
def sendPushBullet(title, message):

    pb = Pushbullet(PB_API)
    push = pb.push_note(title, message)
    debug("\nStatus for Push Bullet\n================")
    for key, value in push.items():
        debug("{} : {}".format(key,push[key]))

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
    debug("\nDate Information\n================\nToday = {}.\nFuture Day = {}\nDifference in days = {}".format(
        today, future, diff))
    return (diff.days + 1)

# ========================================================
# Debugger
# ========================================================


def debug(message):
    if DEBUG_ID == 0:
        return()
    elif DEBUG_ID == 1:
        if message == 1:
            print("\n================\nConfig Settings\n================\n")
            for x in config:
                print("\n{}\n================".format(x))
                for y in config[x]:
                    print(y, ':', config[x][y])
        else:
            print(message)

# ========================================================
# Main Function
# ========================================================


def main():
    configSetup()
    balance = returnBalance()
    #onTargetBalance = onTarget()
    if balance == "ERR":
        title = "Error Retrieving Data"
        message = "There was an error retrieving the data.\nAn exception was raised."
    else:
        date_month = int(END_DATE[1])
        date_day = int(END_DATE[2])
        date_year = int(END_DATE[0])
        daysLeft = daysUntil(date_year, date_month, date_day)
        amountToday = balance / daysLeft
        endDate = "{}/{}/{}".format(date_month, date_day, date_year)
        title = "${:,.2f} to spend today.".format(amountToday)
        message = "Today you have ${:,.2f} to spend.\nYou have ${:,.2f} left.\nThere are {} days left until the end date ({}).".format(
            amountToday, balance, daysLeft, endDate)
    debug("\nExpected Message\n================\n{}".format(message))
    if SEND_METHOD == 1:  # 1 = Email
        sendEMail(title, message)
    elif SEND_METHOD == 2:  # 2 = SMS
        sendSMS(message)
    elif SEND_METHOD == 3:  # 3 = Twilio
        sendIFTTT(message)
    elif SEND_METHOD == 4:
        sendPushBullet(title, message)
    debug("\n================\nEND PROGRAM\n================\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print ("\n================\nEND PROGRAM - KEYBOARD\n================\n")
        sys.exit()
