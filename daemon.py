import win32evtlog
import ConfigParser
import os
import sys
from daemon_ui import Ui_iAmVM
from PyQt4 import QtCore, QtGui

class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.user_choice=None
        self.ui = Ui_iAmVM()
        self.ui.setupUi(self)
        self.ui.allow.clicked.connect(self.allow_proc)
        self.ui.allow_once.clicked.connect(self.allow_once_proc)
        self.ui.block.clicked.connect(self.block_proc)

    def allow_proc(self):
        self.user_choice=0
        self.close()

    def allow_once_proc(self):
        self.user_choice=1
        self.close()

    def block_proc(self):
        self.user_choice=2
        self.close()

main_conf_path = r".\iAmVM_conf.ini"

def fileContains(fileLocation,processLocation,processCalled):
    file_obj=open(fileLocation,'r+')
    fileList=file_obj.readlines()
    file_obj.close()
    found=False
    for line in fileList:
        if str(processLocation+","+processCalled) in line:
            found=True
            break
    return found

def addToFile(fileLocation,processLocation,processCalled):
    file_obj=open(fileLocation,'a')
    file_obj.write(processLocation+","+processCalled+"\n")
    file_obj.close()

def killProcess(pid):
    os.popen('TASKKILL /PID '+str(pid)+' /F')

def getUserChoice(eventCategory,timeGenererated,type,processId,processCalled,processLocation):
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    allowedList = main_conf.get("Daemon", "allowedList")
    blockedList = main_conf.get("Daemon", "blockedList")
    my_app = MyForm()
    my_app.ui.textBox.setText("Suspicious activity has been detected!\nThe requester Process: {}\nThe destination object:{}\nType:{}\nTime:{}".format(processCalled,processLocation,type,timeGenererated))
    proc = my_app.show()
    app.exec_()
    signal = my_app.user_choice
    if signal == 0:
        addToFile(allowedList,processLocation,processCalled)
    if signal == 2:
        addToFile(blockedList,processLocation,processCalled)
        killProcess(processId)

def doAction(eventCategory,timeGenererated,type,processId,processCalled,processLocation):
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    allowedList= main_conf.get("Daemon", "allowedList")
    blockedList= main_conf.get("Daemon", "blockedList")
    if fileContains(allowedList,processLocation,processCalled):
        return
    elif fileContains(blockedList,processLocation,processCalled):
        killProcess(processId)
    else:
        getUserChoice(eventCategory,timeGenererated,type,processId,processCalled,processLocation)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    #read ini file
    main_conf_path = r".\iAmVM_conf.ini"
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)

    #create a list of the filenames and keys
    files_name_file = (main_conf.get("Paths", "fileNames"))
    reg_keys_filename = (main_conf.get("Paths", "regKeysPath"))
    files_name = open(files_name_file, 'r')
    reg_keys = open(reg_keys_filename, 'r')
    known_list=[]
    for file in files_name:
        file=file.rstrip()
        name=os.path.basename(file)
        known_list.append(name)
    for file in reg_keys:
        file=file.rstrip()
        name=os.path.basename(file)
        known_list.append(name)

    #define event listener
    server = 'localhost'
    logtype = 'Security'
    hand = win32evtlog.OpenEventLog(server,logtype)
    flags = win32evtlog.EVENTLOG_FORWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
    total = win32evtlog.GetNumberOfEventLogRecords(hand)
    while True:
        events = win32evtlog.ReadEventLog(hand, flags,0)
        if events:
            for event in events:
                id=event.EventID
                if (id==4656 or id==4664):
                        data_list = event.StringInserts
                        if (data_list):
                           for file in known_list:
                                   for data in data_list:
                                       if file in data and file in data_list[6]:
                                        eventCategory=event.EventCategory
                                        timeGenererated=event.TimeGenerated
                                        type=event.EventType
                                        processType=data_list[5].encode('utf-8')
                                        processIdHex=data_list[len(data_list)-3].encode('ascii','ignore')
                                        processId=int(processIdHex,16)
                                        processCalled=data_list[len(data_list)-2].encode('ascii','ignore')
                                        processLocation=data_list[6]
                                        #print 'Event Category:', event.EventCategory
                                        #print 'Time Generated:', event.TimeGenerated
                                        #print 'Event Type:', event.EventType
                                        #print "Kind: {}".format(processType)
                                        #print "Process that accessed: {}".format(processLocation)
                                        #print "Process initiated the call: {}".format(processCalled)
                                        #print "Process initiated ID: {}".format(processId)
                                        #print "***********************"
                                        doAction(eventCategory,timeGenererated,processType,processId,processCalled,processLocation)
                                        break

