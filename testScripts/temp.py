def populateData(self):
    '''
    Step 1
    '''
    self.cpLoginUserText.set(self.cpCred.username)
    self.cpLoginPassText.set(self.cpCred.password)
    self.sendByVar.set(self.options.sendBy)
    self.endDateTxt.set(self.options.end)
    '''
    Step 2
    '''
    self.emailLoginUserText.set(self.emailSettings.username)
    self.emailLoginPassText.set(self.emailSettings.password)
    self.emailServerText.set(self.emailSettings.server)
    self.emailPortText.set(self.emailSettings.port)
    self.emailSendToText.set(self.emailSettings.to)
    '''
    Step 3
    '''
    self.smsAccountSIDText.set(self.smsSettings.accountSID)
    self.smsAccountAUTHText.set(self.smsSettings.authToken)
    self.smsSendNumText.set(self.smsSettings.sendNumber)
    self.smsRecieveNumText.set(self.smsSettings.recieveNum)
    '''
    Step 4
    '''
    self.iftttSecretKeyText.est(self.iftttSettings.iftttSecretKey)
    self.iftttEventNameText.set(self.iftttSettings.iftttEventName)
    '''
    Step 5
    '''
    self.pushBulletAPI.set(self.pushBulletSettings.pushBulletAPI)

def readInitialConfigSettings(self):
    config.read('config.ini')
    self.cpCred.username = config['CALPOLY_CREDENTIALS']['USERNAME']
    self.cpCred.password = base64.b64decode(
        config['CALPOLY_CREDENTIALS']['PASSWORD']).decode("utf-8")
    self.emailSettings.username = config['EMAIL_SETTINGS']['LOGIN']
    self.emailSettings.password = base64.b64decode(
        config['EMAIL_SETTINGS']['PASSWORD']).decode("utf-8")
    self.emailSettings.server = config['EMAIL_SETTINGS']['SERVER']
    self.emailSettings.port = int(config['EMAIL_SETTINGS']['PORT'])
    self.emailSettings.to = config['EMAIL_SETTINGS']['TO']
    self.smsSettings.accountSID = config['SMS_SETTINGS']['ACCOUNT_SID']
    self.smsSettings.authToken = config['SMS_SETTINGS']['AUTH_TOKEN']
    self.smsSettings.sendNumber = config['SMS_SETTINGS']['SENDING_NUMBER']
    self.sendMessage.recieveNum = config['SMS_SETTINGS']['RECEIVING_NUMBER']
    self.iftttSettings.iftttSecretKey = config['IFTTT_SETTINGS']['IFTTT_SECRETKEY']
    self.iftttSettings.iftttEventName = config['IFTTT_SETTINGS']['IFTTT_EVENTNAME']
    self.options.debug = int(config['OPTIONS']['DEBUG'])
    self.options.sendBy = config['OPTIONS']['SEND_BY'].upper()
    self.pushBulletSettings.pushBulletAPI = config['PUSHBULLET']['API']
    self.options.sendBy = sendMethod(sendBy)
    self.options.end = config['OPTIONS']['END']

    if self.options.sendBy == "EMAIL" and (self.emailSettings.username == self.cpCred.username):
        self.options.sendBy = "CP Email"
    elif self.options.sendBy == "SMS":
        self.options.sendBy = "SMS"
    elif self.options.sendBy == "IFTTT":
        self.options.sendBy = "IFTTT"
    elif self.options.sendBy == "PB":
        self.options.sendBy = "PushBullet"
    else:
        self.options.sendBy = "Other Email"
