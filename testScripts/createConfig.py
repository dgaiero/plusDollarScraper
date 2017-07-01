import tkinter
import ttkcalendar
import os
import sys
from tkinter import messagebox
import tkSimpleDialog
from configparser import *
from base64 import *


import requests
import lxml.html

class CalendarDialog(tkSimpleDialog.Dialog):
    """Dialog box that displays a calendar and returns the selected date"""

    def body(self, master):
        self.calendar = ttkcalendar.Calendar(master)
        self.calendar.pack()

    def apply(self):
        self.result = self.calendar.selection


class CalendarFrame(tkinter.LabelFrame):
    def __init__(self, master):
        tkinter.LabelFrame.__init__(self, master, text="Date Selector")

        def getdate():
            cd = CalendarDialog(self)
            result = cd.result
            # Change this to "%Y,%-m,%-d" on linux
            self.selected_date.set(result.strftime("%Y,%#m,%#d"))
            global getDate
            getDate = self.selected_date.get()
            # return self.selected_date
        self.selected_date = tkinter.StringVar()
        dateTextField = tkinter.Entry(master, textvariable=self.selected_date)
        dateTextField.grid(row=3, column=1, pady=2)
        dateTextField.config(width=25, state='readonly')
        dateTextButton = tkinter.Button(
            master, text="Choose a date", command=getdate)
        dateTextButton.grid(row=3, column=0, padx=5, pady=2, sticky="E")
        dateTextButton.config(width=12)
    def set(self,date):
        self.selected_date.set(date)

def quitApplication():
    if messagebox.askyesno("Quit", "Do you really wish to quit?"):
        form.destroy()
        sys.exit()


class configForm(tkinter.Tk):

    def __init__(self):
        '''
        Configuration
        Setup form
        Set form to non-resizable
        Set form title
        '''

        tkinter.Tk.__init__(self)

        self.resizable(0, 0)
        self.wm_title('PSU Config')

        '''
        Part One
        Setup credentials and other basic Settings
        '''

        self.stepOne = tkinter.LabelFrame(self, text="Enter Login Details: ")
        self.stepOne.grid(row=0, columnspan=7, sticky='WE',
                          padx=5, pady=5, ipadx=5, ipady=5)

        self.cpLoginUserLbl = tkinter.Label(self.stepOne, text="Cal Poly Uesrname:")
        self.cpLoginUserLbl.grid(row=0, column=0, sticky='E', padx=5, pady=2)

        self.cpLoginUserText = tkinter.Entry(self.stepOne)
        self.cpLoginUserText.config(width=25)
        self.cpLoginUserText.grid(
            row=0, column=1, columnspan=7, sticky="W", pady=3)

        self.cpLoginPassLbl = tkinter.Label(self.stepOne, text="Cal Poly Password:")
        self.cpLoginPassLbl.grid(row=1, column=0, sticky='E', padx=5, pady=2)

        self.cpLoginPassText = tkinter.Entry(self.stepOne, show="\u2022")
        self.cpLoginPassText.config(width=25)
        self.cpLoginPassText.grid(
            row=1, column=1, columnspan=7, sticky="W", pady=3)

        self.sendByLbl = tkinter.Label(self.stepOne, text="Send By:")
        self.sendByLbl.grid(row=2, column=0, sticky='E', padx=5, pady=2)

        self.sendByVar = tkinter.StringVar(self)
        self.sendByVar.set("Send Method")
        self.sendByDropMenu = tkinter.OptionMenu(
            self.stepOne, self.sendByVar,  "CP Email", "Other Email", "SMS", "IFTT", "Pushbullet")
        self.sendByDropMenu.config(width=19)
        self.sendByDropMenu.grid(row=2, column=1, sticky='W', pady=2)

        self.endDateTxt = CalendarFrame(self.stepOne)
        self.endDateTxt.grid(sticky='W')
        self.testLoginBtn = tkinter.Button(self.stepOne, text="Test Login", command=self.checkLogin)
        self.testLoginBtn.grid(row=4, column=1, sticky='E', padx=5, pady=2)

        '''
        Information between parts
        '''

        informationLabel = tkinter.Label(self,
                                         text="Please note, you only have to fill"
                                         " out the\ninformation corosponding to"
                                         "what\nSend Method you selected.",
                                         justify="left")
        informationLabel.grid(
            row=1, column=0, columnspan=2, pady=2, sticky='W')

        '''
        Part Two
        Enter other email Settings
        '''

        self.stepTwo = tkinter.LabelFrame(self, text="Enter Email Settings: ")
        self.stepTwo.grid(row=3, columnspan=7, sticky='WE',
                          padx=5, pady=5, ipadx=5, ipady=5)

        self.emailLoginUserLbl = tkinter.Label(self.stepTwo, text="Email Uesrname:")
        self.emailLoginUserLbl.grid(
            row=0, column=0, sticky='E', padx=5, pady=2)

        self.emailLoginUserText = tkinter.Entry(self.stepTwo)
        self.emailLoginUserText.grid(
            row=0, column=1, columnspan=40, sticky="WE", pady=3)

        self.emailLoginPassLbl = tkinter.Label(self.stepTwo, text="Email Password:")
        self.emailLoginPassLbl.grid(
            row=1, column=0, sticky='E', padx=5, pady=2)

        self.emailLoginPassText = tkinter.Entry(self.stepTwo, show="\u2022")
        self.emailLoginPassText.config(width=25)
        self.emailLoginPassText.grid(
            row=1, column=1, columnspan=40, sticky="WE", pady=3)

        self.emailServerLbl = tkinter.Label(self.stepTwo, text="    Email Server:")
        self.emailServerLbl.grid(row=2, column=0, sticky='E', padx=5, pady=2)

        self.emailServerText = tkinter.Entry(self.stepTwo)
        self.emailServerText.config(width=25)
        self.emailServerText.grid(
            row=2, column=1, columnspan=40, sticky="E", pady=3)

        self.emailPortLbl = tkinter.Label(self.stepTwo, text="Email Port:")
        self.emailPortLbl.grid(row=3, column=0, sticky='E', padx=5, pady=2)

        self.emailPortText = tkinter.Entry(self.stepTwo)
        self.emailPortText.config(width=25)
        self.emailPortText.grid(
            row=3, column=1, columnspan=40, sticky="E", pady=3)

        self.emailSendToLbl = tkinter.Label(self.stepTwo, text="Send mail to:")
        self.emailSendToLbl.grid(row=3, column=0, sticky='E', padx=5, pady=2)

        self.emailSendToText = tkinter.Entry(self.stepTwo)
        self.emailSendToText.config(width=25)
        self.emailSendToText.grid(
            row=3, column=1, columnspan=40, sticky="E", pady=3)

        '''
        Part Three
        SMS Settings
        '''

        self.stepThree = tkinter.LabelFrame(self, text="Enter SMS Settings: ")
        self.stepThree.grid(row=4, columnspan=7, sticky='WE',
                            padx=5, pady=5, ipadx=5, ipady=5)

        self.smsAccountSIDLbl = tkinter.Label(
            self.stepThree, text="SMS Account SID:")
        self.smsAccountSIDLbl.grid(row=0, column=0, sticky='E', padx=5, pady=2)

        self.smsAccountSIDText = tkinter.Entry(self.stepThree)
        self.smsAccountSIDText.config(width=25)
        self.smsAccountSIDText.grid(
            row=0, column=1, columnspan=40, sticky="EE", pady=3)

        self.smsAccountAUTHLbl = tkinter.Label(
            self.stepThree, text="SMS Auth Token:")
        self.smsAccountAUTHLbl.grid(
            row=1, column=0, sticky='E', padx=5, pady=2)

        self.smsAccountAUTHText = tkinter.Entry(self.stepThree)
        self.smsAccountAUTHText.config(width=25)
        self.smsAccountAUTHText.grid(
            row=1, column=1, columnspan=40, sticky="EE", pady=3)

        self.smsSendNumLbl = tkinter.Label(self.stepThree, text="Sending Number:")
        self.smsSendNumLbl.grid(row=2, column=0, sticky='E', padx=5, pady=2)

        self.smsSendNumText = tkinter.Entry(self.stepThree)
        self.smsSendNumText.config(width=25)
        self.smsSendNumText.grid(
            row=2, column=1, columnspan=40, sticky="EE", pady=3)

        self.smsRecieveNumLbl = tkinter.Label(
            self.stepThree, text="Receiving Number:")
        self.smsRecieveNumLbl.grid(row=3, column=0, sticky='E', padx=5, pady=2)

        self.smsRecieveNumText = tkinter.Entry(self.stepThree)
        self.smsRecieveNumText.config(width=25)
        self.smsRecieveNumText.grid(
            row=3, column=1, columnspan=40, sticky="EE", pady=3)

        '''
        Part Four
        IFTTT Settings
        '''

        self.stepFour = tkinter.LabelFrame(self, text="Enter IFTTT Settings: ")
        self.stepFour.grid(row=5, columnspan=7, sticky='WE',
                           padx=5, pady=5, ipadx=5, ipady=5)

        self.iftttSecretKeyLbl = tkinter.Label(self.stepFour, text="IFTTT Secret:")
        self.iftttSecretKeyLbl.grid(
            row=0, column=0, sticky='E', padx=5, pady=2)

        self.iftttSecretKeyText = tkinter.Entry(self.stepFour)
        self.iftttSecretKeyText.config(width=25)
        self.iftttSecretKeyText.grid(
            row=0, column=1, columnspan=40, sticky="EE", pady=3)

        self.iftttEventNameLbl = tkinter.Label(
            self.stepFour, text="IFTTT Event Name:")
        self.iftttEventNameLbl.grid(
            row=1, column=0, sticky='E', padx=5, pady=2)

        self.iftttEventNameText = tkinter.Entry(self.stepFour)
        self.iftttEventNameText.config(width=25)
        self.iftttEventNameText.grid(
            row=1, column=1, columnspan=40, sticky="EE", pady=3)

        '''
        Part Five
        Pushbullet API
        '''

        self.stepFive = tkinter.LabelFrame(
            self, text="Enter Pushbullet Information: ")
        self.stepFive.grid(row=6, columnspan=7, sticky='WE',
                           padx=5, pady=5, ipadx=5, ipady=5)

        self.pushBulletApiLbl = tkinter.Label(self.stepFive, text="Pushbullet API:")
        self.pushBulletApiLbl.grid(row=1, column=0, sticky='E', padx=5, pady=2)

        self.pushBulletApiText = tkinter.Entry(self.stepFive)
        self.pushBulletApiText.config(width=25)
        self.pushBulletApiText.grid(
            row=1, column=1, columnspan=40, sticky="EE", pady=3)

        '''
        Save/Quit/etc buttons
        '''

        self.saveExit = tkinter.Button(self, text="Save and Exit", command=self.askToSave)
        self.saveExit.grid(row=7, column=0, sticky='W', padx=5, pady=2)

        self.saveRun = tkinter.Button(self, text="Save and Run")
        self.saveRun.grid(row=7, column=1, sticky='W', padx=5, pady=2)

        self.cancel = tkinter.Button(
            self, text="Quit", command=quitApplication)
        self.cancel.grid(row=7, column=2, sticky='W', padx=5, pady=2)

        cwd = os.getcwd()
        iconLocation = "{}\\testScripts\\icon.ico".format(cwd)
        self.iconbitmap(r'{}'.format(iconLocation))


        fileExists = os.path.isfile("config.ini")
        self.config = ConfigParser()

        if fileExists:
            self.readInitialConfigSettings()
            self.populateData()

    class cpCred():
        def __init__(self, username, password):
            self.username = username
            self.password = password

    class emailSettings():
        def __init__(self, username, password, server, port, to):
            self.username = username
            self.password = password
            self.server = server
            self.port = port
            self.to = to

    class smsSettings():
        def __init__(self, accountSID, authToken, sendNumber, recieveNum):
            self.accountSID = accountSID
            self.authToken = authToken
            self.sendNumber = sendNumber
            self.recieveNum = recieveNum

    class iftttSettings():
        def __init__(self, iftttSecretKey, iftttEventName):
            self.iftttSecretKey = iftttSecretKey
            self.iftttEventName = iftttEventName

    class pushBulletSettings():
        def __init__(self, pushBulletAPI):
            self.pushBulletAPI = pushBulletAPI

    class options():
        def __init__(self, sendBy, end, debug):
            self.sendBy = sendBy
            self.end = end
            self.debug = debug

        def sendMethod(self):
            # SEND_METHOD defaults to 1 (Email)
            if self.sendBy == "EMAIL":
                self.sendMethod = 1
            elif self.sendBy == "SMS":
                self.sendMethod = 2
            elif self.sendBy == "IFTTT":
                self.sendMethod = 3
            elif self.sendBy == "PB":
                self.sendMethod = 4
            else:
                self.sendMethod = 1
            return self.sendMethod

    def populateData(self):
        '''
        Step 1
        '''
        self.cpLoginUserText.insert(0,self.userData.username)
        self.cpLoginPassText.insert(0,self.userData.password)
        self.sendByVar.set(self.mOptions.sendBy)
        self.endDateTxt.set(self.mOptions.end)
        '''
        Step 2
        '''
        self.emailLoginUserText.insert(0,self.email.username)
        self.emailLoginPassText.insert(0,self.email.password)
        self.emailServerText.insert(0,self.email.server)
        self.emailPortText.insert(0,self.email.port)
        self.emailSendToText.insert(0,self.email.to)
        '''
        Step 3
        '''
        self.smsAccountSIDText.insert(0,self.sms.accountSID)
        self.smsAccountAUTHText.insert(0,self.sms.authToken)
        self.smsSendNumText.insert(0,self.sms.sendNumber)
        self.smsRecieveNumText.insert(0,self.sms.recieveNum)
        '''
        Step 4
        '''
        self.iftttSecretKeyText.insert(0,self.ifttt.iftttSecretKey)
        self.iftttEventNameText.insert(0,self.ifttt.iftttEventName)
        '''
        Step 5
        '''
        self.pushBulletApiText.insert(0,self.pushBullet.pushBulletAPI)

    def readInitialConfigSettings(self):
        self.config.read('config.ini')
        '''
        CP CALPOLY_CREDENTIALS
        '''
        username = self.config['CALPOLY_CREDENTIALS']['USERNAME']
        password = b64decode(
            self.config['CALPOLY_CREDENTIALS']['PASSWORD']).decode("utf-8")
        self.userData = self.cpCred(username,password)
        '''
        Email Settings
        '''
        emailUsername = self.config['EMAIL_SETTINGS']['LOGIN']
        emailPassword = b64decode(
            self.config['EMAIL_SETTINGS']['PASSWORD']).decode("utf-8")
        emailServer = self.config['EMAIL_SETTINGS']['SERVER']
        emailPort = int(self.config['EMAIL_SETTINGS']['PORT'])
        emailTo = self.config['EMAIL_SETTINGS']['TO']
        self.email = self.emailSettings(emailUsername,emailPassword,emailServer,emailPort,emailTo)
        '''
        SMS Settings
        '''
        accountSID = self.config['SMS_SETTINGS']['ACCOUNT_SID']
        authToken = self.config['SMS_SETTINGS']['AUTH_TOKEN']
        sendNumber = self.config['SMS_SETTINGS']['SENDING_NUMBER']
        recieveNum = self.config['SMS_SETTINGS']['RECEIVING_NUMBER']
        self.sms = self.smsSettings(accountSID,authToken,sendNumber,recieveNum)
        '''
        IFTTT Settings
        '''
        iftttSecretKey = self.config['IFTTT_SETTINGS']['IFTTT_SECRETKEY']
        iftttEventName = self.config['IFTTT_SETTINGS']['IFTTT_EVENTNAME']
        self.ifttt = self.iftttSettings(iftttSecretKey,iftttEventName)
        '''
        Misc. Options
        '''
        debug = int(self.config['OPTIONS']['DEBUG'])
        sendBy = self.config['OPTIONS']['SEND_BY'].upper()
        end = self.config['OPTIONS']['END']
        self.mOptions = self.options(sendBy,end,debug)
        '''
        PushBullet
        '''
        pushBulletAPI = self.config['PUSHBULLET']['API']
        self.pushBullet = self.pushBulletSettings(pushBulletAPI)


        if self.mOptions.sendBy == "EMAIL" and (self.email.username == self.userData.username):
            self.mOptions.sendBy = "CP Email"
        elif self.mOptions.sendBy == "SMS":
            self.mOptions.sendBy = "SMS"
        elif self.mOptions.sendBy == "IFTTT":
            self.mOptions.sendBy = "IFTTT"
        elif self.mOptions.sendBy == "PB":
            self.mOptions.sendBy = "Pushbullet"
        else:
            self.mOptions.sendBy = "Other Email"


    '''
    Should be able to delete once the two scripts are integrated
    '''

    def checkLogin(self):
        self.loginUser(self.cpLoginUserText.get(),self.cpLoginPassText.get())
        result = self.loginTest()
        print(self.cpLoginUserText.get())
        print(result)
        if result:
            loginTest = tkinter.Label(self.stepOne, text="Login Successful")
        else:
            loginTest = tkinter.Label(self.stepOne, text="Login Unsuccessful", fg="red")
        loginTest.grid(row=4, column=0, sticky='E', padx=5, pady=2)

    def loginUser(self,username, password):
        print (username)
        self.session_requests = requests.session()  # Initalize web session
        result = self.session_requests.get("https://my.calpoly.edu/cas/login")  # Get page data for login
        login_html = lxml.html.fromstring(result.text)
        # Looks for all hidden inputs (mainly for CSRF token)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

    # ========================================================
    # Dictionary for login
    # ========================================================

        # Add the hidden inputs to login dictionary
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}
        # Add global username and password to login dictionary
        form['username'] = username
        form['password'] = password
        self.session_requests.post(  # post data to login URL
            "https://my.calpoly.edu/cas/login",
            data=form,
        )
        return self.session_requests

    def loginTest(self):
        cookie = str(self.session_requests.cookies)
        if "myportal.calpoly.edu" in cookie:
            return True
        else:
            return False

    '''
    '''

    def writeToConfig(self):

        if not(self.cpLoginUserText.get().endswith("@calpoly.edu")):
            cpLoginUser = self.cpLoginUserText.get() + "@calpoly.edu"
        else:
            cpLoginUser = self.cpLoginUserText.get()

        if self.sendByVar.get() == "CP Email":
            sendByMethod = "EMAIL"
            emailLoginUser = cpLoginUser
            emailLoginPass = self.cpLoginPassText.get()
            emailPort = "587"
            emailServer = "smtp.office365.com"
            emailTo = cpLoginUser
        elif self.sendByVar.get() == "Other Email":
            sendByVar = "EMAIL"
            emailLoginUser = self.emailLoginUserText.get()
            emailLoginPass = self.emailLoginPassText.get()
            emailPort = self.emailPortText.get()
            emailServer = self.emailServerText.get()
            emailTo = self.emailSendToText.get()
        elif self.sendByVar.get() == "PushBullet":
            sendByMethod = "PB"
        elif self.sendByVar.get() == "SMS":
            sendByMethod = "SMS"
        elif self.sendByVar.get() == "IFTTT":
            sendByMethod = "IFTTT"

        configSettings = ConfigParser()
        configSettings.read("config01.ini")
        cpLoginPassTextEncoded = b64encode(bytes(self.cpLoginPassText.get(), "utf-8")).decode("utf-8")
        emailLoginPassTextEncoded = b64encode(bytes(emailLoginPass, "utf-8")).decode("utf-8")
        configSettings['CALPOLY_CREDENTIALS'] = {
            'USERNAME': cpLoginUser, 'PASSWORD': cpLoginPassTextEncoded}
        configSettings['EMAIL_SETTINGS'] = {'LOGIN': emailLoginUser, 'PASSWORD': emailLoginPassTextEncoded,
                                    'SERVER': emailServer, 'PORT': emailPort, 'TO': emailTo}
        configSettings['SMS_SETTINGS'] = {
            'ACCOUNT_SID': self.smsAccountSIDText.get(), 'AUTH_TOKEN': self.smsAccountAUTHText.get(), 'SENDING_NUMBER': self.smsSendNumText.get(), 'RECEIVING_NUMBER': self.smsRecieveNumText.get()}
        configSettings['IFTTT_SETTINGS'] = {
            'IFTTT_SECRETKEY': self.iftttSecretKeyText.get(), 'IFTTT_EVENTNAME': self.iftttEventNameText.get()}
        configSettings['PUSHBULLET'] = {'API': ''}
        configSettings['OPTIONS'] = {'SEND_BY': sendByMethod.upper(),
                             'END': getDate, 'DEBUG': 0}
        print(configSettings._sections)
        with open('config01.ini', 'w') as configfile:
            configSettings.write(configfile)

    def askToSave(self):
        if messagebox.askyesno("Save Information", "The information in the password fields are bas64 decoded. Do you understand the risks associated with using this progam. Please note, all login data is only supplied to Cal Poly."):
            self.writeToConfig()

if __name__ == '__main__':
    form = configForm()
    form.mainloop()
