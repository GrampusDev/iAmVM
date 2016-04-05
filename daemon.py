import win32evtlog
import ConfigParser
import os
if __name__ == '__main__':
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
                                        print 'Event Category:', event.EventCategory
                                        print 'Time Generated:', event.TimeGenerated
                                        print 'Source Name:', event.SourceName
                                        print 'Event ID:', event.EventID
                                        print 'Event Type:', event.EventType
                                        processType=data_list[5].encode('utf-8')
                                        processId=data_list[len(data_list)-3].encode('utf-8')
                                        processCalled=data_list[len(data_list)-2].encode('utf-8')
                                        print "Kind: {}".format(processType)
                                        processLocation=data_list[6]
                                        print "Process that accessed: {}".format(processLocation)
                                        print "Process initiated the call: {}".format(processCalled)
                                        print "Process initiated ID: {}".format(processId)
                                        print "***********************"
                                        break
