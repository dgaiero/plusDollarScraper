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
    global USERNAME, PASSWORD, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_SERVER
    global EMAIL_PORT, EMAIL_TO, SEND_BY, SEND_METHOD, END_DATE, SMS_ACCOUNT_SID
    global SMS_AUTH_TOKEN, SMS_SENDING_NUMBER, SMS_RECEIVING_NUMBER, IFTTT_SECRETKEY, IFTTT_EVENTNAME
    # checks if the config file already exists
    _fileExists = os.path.isfile("config.ini")
    _config = configparser.ConfigParser()  # initalizes config parser

    if _fileExists:  # If the file exists, then parse the fields and set to global variables
        _config.read('config.ini')
        USERNAME = _config['CALPOLY_CREDENTIALS']['USERNAME']
        PASSWORD = base64.b64decode(
            _config['CALPOLY_CREDENTIALS']['PASSWORD']).decode("utf-8")
        EMAIL_USERNAME = _config['EMAIL_SETTINGS']['LOGIN']
        EMAIL_PASSWORD = base64.b64decode(
            _config['EMAIL_SETTINGS']['PASSWORD']).decode("utf-8")
        EMAIL_SERVER = _config['EMAIL_SETTINGS']['SERVER']
        EMAIL_PORT = int(_config['EMAIL_SETTINGS']['PORT'])
        EMAIL_TO = _config['EMAIL_SETTINGS']['TO']
        SMS_ACCOUNT_SID = _config['SMS_SETTINGS']['ACCOUNT_SID']
        SMS_AUTH_TOKEN = _config['SMS_SETTINGS']['AUTH_TOKEN']
        SMS_SENDING_NUMBER = _config['SMS_SETTINGS']['SENDING_NUMBER']
        SMS_RECEIVING_NUMBER = _config['SMS_SETTINGS']['RECEIVING_NUMBER']
        IFTTT_SECRETKEY = _config['IFTTT_SETTINGS']['IFTTT_SECRETKEY']
        IFTTT_EVENTNAME = _config['IFTTT_SETTINGS']['IFTTT_EVENTNAME']
        # Makes value case insensitive
        _sendBy = _config['OPTIONS']['SEND_BY'].upper()
        if _sendBy == "EMAIL":  # SEND_METHOD defaults to 1 (Email)
            SEND_METHOD = 1
        elif _sendBy == "SMS":
            SEND_METHOD = 2
        elif _sendBy == "IFTTT":
            SEND_METHOD = 3
        else:
            SEND_METHOD = 1
        END_DATE = _config['OPTIONS']['END'].split(
            ",")  # Split end date into yyyy,m,d
    else:  # If the config file does not exist, this writes config.ini
        print("The following prompots will setup the config.ini file.\nThis will only run once.\n\n")
        USERNAME = input('Enter your cal poly username (with @calpoly.edu): ')
        PASSWORD = input('Enter your cal poly password: ')
        _passwordEncode = base64.b64encode(
            bytes(PASSWORD, "utf-8")).decode("utf-8")
        print("If you do not want to use a third party email service, then leave the following sections blank\n")
        EMAIL_USERNAME = input(
            "Enter your email address (or leave blank for CALPOLY email) : ") or USERNAME
        EMAIL_PASSWORD = input(
            "Enter your password (or leave blank for CALPOLY password) : ") or PASSWORD
        _emailPasswordEncode = base64.b64encode(
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
        _sendBy = input(
            "How do you want to recieve notifications? 'EMAIL' 'SMS' or 'IFTTT': ").upper() or "EMAIL"
        END_DATE = input(
            "What is the end date? (yyyy,m,d). No leading zeros: ") or "2017,6,16"
        if _sendBy == "EMAIL":  # SEND_METHOD defaults to 1 (Email)
            SEND_METHOD = 1
        elif _sendBy == "SMS":
            SEND_METHOD = 2
        elif _sendBy == "IFTTT":
            SEND_METHOD = 3
        else:
            SEND_METHOD = 1
        # Dictionary for config file

        _config['CALPOLY_CREDENTIALS'] = {
            'USERNAME': USERNAME, 'PASSWORD': _passwordEncode}
        _config['EMAIL_SETTINGS'] = {'LOGIN': EMAIL_USERNAME, 'PASSWORD': _emailPasswordEncode,
                                     'SERVER': EMAIL_SERVER, 'PORT': EMAIL_PORT, 'TO': EMAIL_TO}
        _config['SMS_SETTINGS'] = {
            'ACCOUNT_SID': SMS_ACCOUNT_SID, 'AUTH_TOKEN': SMS_AUTH_TOKEN, 'SENDING_NUMBER': SMS_SENDING_NUMBER, 'RECEIVING_NUMBER': SMS_RECEIVING_NUMBER}
        _config['IFTTT_SETTINGS'] = {
            'IFTTT_SECRETKEY': IFTTT_SECRETKEY, 'IFTTT_EVENTNAME': IFTTT_EVENTNAME}
        _config['OPTIONS'] = {'SEND_BY': _sendBy, 'END': END_DATE}

        with open('config.ini', 'w') as _configfile:
            _config.write(_configfile)

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
            _inputData = line.rstrip().split("<")
            _inputData = _inputData[1].split("$")
            _processedData = _inputData  # Splits the data so it returns just a number
            # Adds the number to end of balances
            balances.extend(_processedData)
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


def sendEMail(_message):
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


def sendSMS(_message):

    client = TwilioRestClient(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)
    message = client.messages.create(body=_message,
                                     to=SMS_RECEIVING_NUMBER,
                                     from_=SMS_SENDING_NUMBER)

# ========================================================
# Send notificaiotn with IFTTT
# ========================================================


def sendIFTTT(_message):

    report = {}
    report["value1"] = _message
    url = "https://maker.ifttt.com/trigger/{}/with/key/{}".format(
        IFTTT_EVENTNAME, IFTTT_SECRETKEY)
    requests.post(url, data=report)

# ========================================================
# Calcualte days remaining until the end of quarter
# ========================================================


def daysUntil(_year, _month, _day):
    _today = date.today()
    # The date format has to have (a) no leading zeros and (b) must be
    # formatted yyyy,m,d
    _future = date(_year, _month, _day)
    _diff = _future - _today
    return _diff.days

# ========================================================
# Main Function
# ========================================================


def main():
    configSetup()  # Run configsetup to return global variables
    balance = returnBalance()
    # Everything from config comes as str, must convert to int.
    daysLeft = daysUntil(int(END_DATE[0]), int(END_DATE[1]), int(END_DATE[2]))
    amountToday = balance / daysLeft  # Just some simple division
    _endDate = "{}/{}/{}".format(END_DATE[2], END_DATE[1], END_DATE[0])
    _message = "Today you have ${} to spend. \n You have ${} left. \n There are {} days left until the end date ({}).".format(
        round(amountToday, 2), round(balance, 2), daysLeft, _endDate)
    if SEND_METHOD == 1:  # 1 = Email
        sendEMail(_message)
    elif SEND_METHOD == 2:  # 2 = SMS
        sendSMS(_message)
    elif SEND_METHOD == 3:
        sendIFTTT(_message)


if __name__ == '__main__':
    main()
