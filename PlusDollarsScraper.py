# Hack Tech 2017
# Plus Dollars Scrape
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
    global SMS_AUTH_TOKEN, SMS_SENDING_NUMBER, SMS_RECEIVING_NUMBER
    fileExists = os.path.isfile("config.ini")
    config = configparser.ConfigParser()
    config['CALPOLY_CREDENTIALS'] = {'USERNAME': '', 'PASSWORD': ''}
    config['EMAIL_SETTINGS'] = {'LOGIN': '', 'PASSWORD': '',
                                'SERVER': 'smtp.office365.com', 'PORT': '587', 'TO': ''}
    config['SMS_SETTINGS'] = {
        'ACCOUNT_SID': '', 'AUTH_TOKEN': '', 'SENDING_NUMBER': '', 'RECEIVING_NUMBER': ''}
    config['OPTIONS'] = {'SEND_BY': 'EMAIL', 'END': '2017,6,16'}
    if fileExists:
        config.read('config.ini')
        USERNAME = config['CALPOLY_CREDENTIALS']['USERNAME']
        PASSWORD = config['CALPOLY_CREDENTIALS']['PASSWORD']
        EMAIL_USERNAME = config['EMAIL_SETTINGS']['LOGIN']
        EMAIL_PASSWORD = config['EMAIL_SETTINGS']['PASSWORD']
        EMAIL_SERVER = config['EMAIL_SETTINGS']['SERVER']
        EMAIL_PORT = int(config['EMAIL_SETTINGS']['PORT'])
        EMAIL_TO = config['EMAIL_SETTINGS']['TO']
        SMS_ACCOUNT_SID = config['SMS_SETTINGS']['ACCOUNT_SID']
        SMS_AUTH_TOKEN = config['SMS_SETTINGS']['AUTH_TOKEN']
        SMS_SENDING_NUMBER = config['SMS_SETTINGS']['SENDING_NUMBER']
        SMS_RECEIVING_NUMBER = config['SMS_SETTINGS']['RECEIVING_NUMBER']
        SEND_BY = config['OPTIONS']['SEND_BY']
        if SEND_BY == "EMAIL":
            SEND_METHOD = 1
        elif SEND_BY == "SMS":
            SEND_METHOD = 2
        else:
            SEND_METHOD = 1
        END_DATE = config['OPTIONS']['END'].split(",")
    else:
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        exit()

# ========================================================
# Main Program
# ========================================================


def returnBalance():
    session_requests = requests.session()
    result = session_requests.get(LOGIN_URL)
    login_html = lxml.html.fromstring(result.text)
    hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

# ========================================================
# Dictionary for login
# ========================================================

    form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}
    form['username'] = USERNAME
    form['password'] = PASSWORD
    result = session_requests.post(
        LOGIN_URL,
        data=form,
        #headers = dict(referer = LOGIN_URL)
    )

# =========================================================
# Scrape url
# =========================================================

    result = session_requests.get(URL)
    soup = BeautifulSoup(result.text, "lxml")
    fileName = "temp.webScrape"
    f = open(fileName, "w+")
    f.write(str(soup))
    f.close()
    fh = open(fileName)
    balances = []
    for line in fh:
        if re.search(r"\$.*</td>", line):
            __inputData = line.rstrip().split("<")
            __inputData = __inputData[1].split("$")
            __processedData = __inputData
            balances.extend(__processedData)
    balance = balances[1]
    fh.close()
    try:
        os.remove(fileName)
    except OSError:
        pass
    balance = float(balance)
    return balance

# ========================================================
# Send Mail with balance
# ========================================================


def sendMail(__message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = EMAIL_TO
    msg['Subject'] = "Your Daily Balance"
    msg.attach(MIMEText(__message, 'plain'))
    server = smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT)
    server.starttls()
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    EMAIL_MESSAGE = msg.as_string()
    server.sendmail(EMAIL_USERNAME, EMAIL_TO, EMAIL_MESSAGE)
    server.quit()

# ========================================================
# Send SMS With balance
# ========================================================


def sendSMS(__message):

    client = TwilioRestClient(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)

    message = client.messages.create(body=__message,
                                     to=SMS_RECEIVING_NUMBER,
                                     from_=SMS_SENDING_NUMBER)

# ========================================================
# Calcualte days remaining until the end of quarter
# ========================================================


def daysUntil(__year, __month, __day):
    today = date.today()
    future = date(__year, __month, __day)
    diff = future - today
    return diff.days


def main():
    configSetup()
    balance = returnBalance()
    daysLeft = daysUntil(int(END_DATE[0]), int(END_DATE[1]), int(END_DATE[2]))
    amountToday = balance / daysLeft
    __endDate = "{}/{}/{}".format(END_DATE[0], END_DATE[1], END_DATE[2])
    __message = "Today you have ${} to spend. \n You have ${} left. \n There are {} days left until the end date ({}).".format(
        round(amountToday, 2), round(balance, 2), daysLeft, __endDate)
    if SEND_METHOD == 1:
        sendMail(__message)
    elif SEND_METHOD == 2:
        sendSMS(__message)


if __name__ == '__main__':
    main()
