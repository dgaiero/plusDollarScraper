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

# ========================================================
# Variables
# ========================================================
USERNAME = "USERNAME" # Put Cal Poly username here with @calpoly.edu
PASSWORD = "PASSWORD" # Put passsword here

LOGIN_URL = "https://my.calpoly.edu/cas/login"
URL = "https://cardcenter.calpoly.edu/student/welcome.php"

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
        data = form,
        #headers = dict(referer = LOGIN_URL)
)

# =========================================================
# Scrape url
# =========================================================
    result = session_requests.get(URL)
    soup = BeautifulSoup(result.text, "lxml")
    try:
        os.remove('page.txt')
    except OSError:
        pass
    f = open("page.txt","w+")
    f.write(str(soup))
    f.close()
    #print (soup.find_all('td'))
    fh = open("page.txt")
    balances = []
    for line in fh:
        if re.search(r"\$.*</td>",line):
            __inputData = line.rstrip().split("<")
            __inputData = __inputData[1].split("$")
            __processedData = __inputData
            balances.extend(__processedData)
    balance = balances[1]
    fh.close()
    try:
        os.remove('page.txt')
    except OSError:
        pass
    balance = float(balance)
    return balance

'''
    tree = lxml.html.fromstring(result.content)
    balance = tree.xpath(r'//*[@id="divContent"]/table[2]/tbody/tr/td[2]/div/table/tbody/tr[1]/td[2]/text()')
    result.ok
    result.status_code

    #print(balance[0])
'''

def sendMail(amount):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = USERNAME
    msg['Subject'] = "Your Daily Balance"

    body = "Today you have ${} to spend".format(amount)
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(USERNAME, PASSWORD)
    text = msg.as_string()
    server.sendmail(USERNAME, USERNAME, text)
    server.quit()

def daysUntil(__year,__month,__day):
        today = date.today()
        future = date(__year,__month,__day)
        diff = future - today
        return diff.days

def main():
    balance = returnBalance()
    daysLeft = daysUntil(2017,6,16)
    amountToday = balance / daysLeft
    sendMail(round(amountToday, 2))

if __name__ == '__main__':
    main()
