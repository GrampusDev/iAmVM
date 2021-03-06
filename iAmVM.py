import _winreg as wreg
import os
import shutil
import random
import ctypes
import ConfigParser
import subprocess
import sys
import socket
import logging
import win32file, win32pipe, win32con, win32api, win32gui, winerror
from PyQt4 import QtCore, QtGui
from iAmVM_GUI import Ui_Form

from spoofmac.interface import (
    set_interface_mac,
    get_os_spoofer
)

GUI_MODE = 1
CMD_MODE = 0
DETACHED_PROCESS = 0x00000008

mode = GUI_MODE  # Change to relevant running mode


# Main configuration file
main_conf_path = r".\iAmVM_conf.ini"
BUFFER_SIZE = 1024


class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setStyle(QtGui.QStyleFactory.create("plastique"))
        # self.setStyleSheet("background-image: url(./iAmVM_Background2.jpg); background-repeat: no-repeat; background-position: center;")

        self.ui.pushButton.clicked.connect(self.transform_to_vm_click)
        self.ui.pushButton_2.clicked.connect(self.transform_to_physical_click)
        self.ui.pushButton_3.clicked.connect(self.filter_reg_click)
        self.ui.pushButton_4.clicked.connect(self.spoof_to_vm_mac_click)
        self.ui.pushButton_5.clicked.connect(self.create_vboxtray_windows_click)
        self.ui.pushButton_6.clicked.connect(self.create_vm_files_click)
        self.ui.pushButton_7.clicked.connect(self.create_pseudo_devices)
        self.ui.pushButton_8.clicked.connect(self.create_vm_processes_click)
        self.ui.pushButton_9.clicked.connect(self.add_audits_click)
        self.ui.pushButton_10.clicked.connect(self.exit_click)
        self.ui.pushButton_11.clicked.connect(self.network_defence_click)
        self.ui.pushButton_12.clicked.connect(self.daemon_click)

    def transform_to_vm_click(self):
        self.ui.textEdit.setText("Transforming to VM...")
        # create_reg_keys()
        self.ui.textEdit.setText("Done Transforming to VM")

    def transform_to_physical_click(self):
        self.ui.textEdit.setText("Transforming to Physical...")
        # back_to_physical()
        self.ui.textEdit.setText("Done Transforming to Physical")

    def filter_reg_click(self):
        self.ui.textEdit.setText("Filtering the registry file...")
        # filter_reg_file()
        self.ui.textEdit.setText("Done Filtering the registry file")

    def spoof_to_vm_mac_click(self):
        self.ui.textEdit.setText("Spoofing to VM MAC...")
        # spoof_to_vm_mac()
        self.ui.textEdit.setText("Done Spoofing to VM MAC")

    def create_vm_files_click(self):
        self.ui.textEdit.setText("Creating VM files...")
        # create_files()
        self.ui.textEdit.setText("Done Creating VM files")

    def create_pseudo_devices(self):
        self.ui.textEdit.setText("Create pseudo devices...")
        # create_pseudo_devices()
        self.ui.textEdit.setText("Done Creating pseudo devices")

    def create_vm_processes_click(self):
        self.ui.textEdit.setText("Creating VM processes...")
        # create_dummy_process()
        self.ui.textEdit.setText("Done Creating VM processes")

    def create_vboxtray_windows_click(self):
        self.ui.textEdit.setText("Creating fake windows...")
        # create_vboxtray_windows()
        self.ui.textEdit.setText("Done Creating fake windows")

    def add_audits_click(self):
        self.ui.textEdit.setText("Adding auditing...")
        # run_powershell()
        self.ui.textEdit.setText("Done Adding auditing")

    def network_defence_click(self):
        self.ui.textEdit.setText("Sending message to DGW to set up network defence...")
        response = ''
        # response = start_network_defence()
        self.ui.textEdit.setText(response)

    def daemon_click(self):
        self.ui.textEdit.setText("Starting daemon...")
        subprocess.Popen("pythonw daemon.py", creationflags=DETACHED_PROCESS)
        self.ui.textEdit.setText("Daemon started")

    def exit_click(self):
        self.close()


# Represents registry value
class RegValue:
    def __init__(self, val_name, val_type, val_data):
        self.name = val_name
        self.type = val_type
        self.data = val_data


def get_os():
    """
    Return system OS name.
    :return: string
    """
    if sys.platform.startswith('linux'):
        return 'Linux'
    elif sys.platform.startswith('win'):
        return 'Windows'


def start_network_defence():
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    host = main_conf.get("Network", "defaultgateway")
    port = main_conf.get("Network", "port")
    local_os = get_os()
    if local_os == 'Windows':
        msg = 'Linux'
    else:
        msg = 'Windows'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.send(msg)
    data = s.recv(BUFFER_SIZE)
    s.close()
    return data


def apply_reg_change(reg_key, reg_values):
    """
    Creates (or updates if already exist) reg_key values

    :param reg_key: Registry key to insert value to
    :param reg_values: New values for the key
    """
    for val in reg_values:
        wreg.SetValueEx(reg_key, val.name, 0, val.type, val.data)


def back_to_physical():
    # Registry
    try:
        wreg.DeleteKeyEx(wreg.HKEY_LOCAL_MACHINE,
                         "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Oracle VM VirtualBox Guest Additions",
                         (wreg.KEY_WOW64_64KEY + wreg.KEY_ALL_ACCESS), 0)
    except WindowsError as err:
        print "Failed to delete: ", err

    remove_pseudo_devices()  # Pseudo devices
    remove_files()  # Remove VBOX files
    revert_to_physical_mac()  # Change to the original MAC
    # Destroy VBoxTray window
    if hwnd != 0:
        win32gui.DestroyWindow(hwnd)


def create_reg_keys():
    """
    Creates VM specific keys in the Registry
    """
    reg_conf = ConfigParser.ConfigParser()
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)

    # Get sections from already filtered reg file
    reg_conf.read(main_conf.get("Paths", "FilteredRegFile"))
    reg_keys_path = open(main_conf.get("Paths", "regKeysPath"),"w+", 0)
    sections = reg_conf.sections()

    for sec in sections:
        sec_without_hklm = sec.replace("HKEY_LOCAL_MACHINE\\", "")
        # write the keys for later use in auditing
        sec_for_powershell = sec.replace("HKEY_LOCAL_MACHINE\\", "HKLM:\\")
        reg_keys_path.write(sec_for_powershell + '\n')
        # Open the key, and if doesn't exist create it
        try:
            reg_key = wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE, sec_without_hklm, 0,
                                   (wreg.KEY_WOW64_64KEY + wreg.KEY_ALL_ACCESS))
        except WindowsError:
            try:
                reg_key = wreg.CreateKeyEx(wreg.HKEY_LOCAL_MACHINE,
                                           sec_without_hklm, 0,
                                           (wreg.KEY_WOW64_64KEY + wreg.KEY_ALL_ACCESS))
            except WindowsError as e:
                logging.debug("Failed to create key :" + sec + '\n' + e.strerror)
                # Move on to the next key
                continue

        reg_values = []
        # For each value under the key section
        for opt in reg_conf.options(sec):
            opt_val = reg_conf.get(sec, opt)
            # Check value type
            if 'dword' in opt_val:
                # Get data without the type
                opt_data = opt_val.split(':')[1]
                opt = opt.strip('"')
                try:
                    reg_values.append(RegValue(opt, wreg.REG_DWORD, int(opt_data, 16)))
                except Exception as e:
                    print e
                    continue
            else:
                opt_data = opt_val.strip('"')
                opt = opt.strip('"')
                reg_values.append(RegValue(opt, wreg.REG_SZ, opt_data))

        # Apply registry changes
        apply_reg_change(reg_key, reg_values)
    try:
        # Create some extra keys that are not covered
        reg_key = wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE, "HARDWARE\\DESCRIPTION\\System", 0,
                               (wreg.KEY_WOW64_64KEY + wreg.KEY_ALL_ACCESS))
        wreg.SetValueEx(reg_key, "SystemBiosVersion", 0, wreg.REG_SZ, "VBOX")
        wreg.SetValueEx(reg_key, "VideoBiosVersion", 0, wreg.REG_SZ, "VIRTUALBOX")
        wreg.SetValueEx(reg_key, "SystemBiosDate", 0, wreg.REG_SZ, "06/23/99")
    except Exception as e:
        print e


def filter_reg_file():
    """
    Filters exported reg file from Registry to VM specific keys
    """
    # Read raw registry file that is saved in UTF-8 format
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    filename_path = main_conf.get("Paths", "RawRegFile")
    reg_file = open(filename_path, 'r')
    reg_file.readline()
    reg_file.readline()
    content = reg_file.readlines()
    section = []
    is_write = 0
    is_hex = 0
    is_undesired_section = 0
    # Iterate over all registry keys
    with open(main_conf.get("Paths", "FilteredRegFile"), "w") as dest_file:
        for line in content:
            if '[HKEY_LOCAL_MACHINE' in line and ']' in line:
                # if r"\{" in line and r"}" in line or '[HKEY_USERS' in line or \
                #        'HardwareConfig' in line:
                #    is_undesired_section = 1
                #    is_write = 0
                #    continue
                # else:
                is_undesired_section = 0
                # If previous key contains values that are VM specific than write him to dest file
                if is_write:
                    dest_file.writelines(section)
                # Start new key section
                section = [line]
                is_write = 0
            elif is_undesired_section == 0:
                # if r"c:\\windows\\system32" in line.lower() or \
                #         'PnpLockdownFiles' in line or \
                #         (r"{" in line and r"}" in line) or or\
                #         line.startswith('@'):
                #     continue

                # We not interested in binary values
                if '=hex' not in line and not is_hex:
                    section.append(line)
                # If last binary value read then turn is_hex = 0
                elif '=hex' not in line and is_hex and '"=' in line:
                    is_hex = 0
                    section.append(line)
                else:
                    is_hex = 1
                    continue
            # Check if this key section contains VM specific info
            if ('vbox' in line.lower()) or ('virtualbox' in line.lower()) or ('oracle' in line.lower()):
                is_write = 1


def get_random_mac():
    """
    Returns random Virtual Box specific MAC address
    """
    mac = [0x08, 0x00, 0x27,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join('{0:02X}'.format(o) for o in mac)


def spoof_to_vm_mac():
    """
    Spoof current mac to Virtual Box specific MAC address
    """
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    spoofer = get_os_spoofer()
    if not main_conf.has_section('OldMacs'):
        main_conf.add_section('OldMacs')
    for port, device, address, current_address in spoofer.find_interfaces():
        try:
            # Save old MAC
            main_conf.set('OldMacs', device, address.replace('-', ':'))

            new_mac = get_random_mac()
            set_interface_mac(device, new_mac, port)
        except Exception as e:
            logging.warning(e)
            print e
    try:
        f = open(main_conf_path, 'w')
        main_conf.write(f)
        f.close()
    except IOError as e:
        logging.warning(e)
        print e


def revert_to_physical_mac():
    """
    Revert to old MAC
    """
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    spoofer = get_os_spoofer()
    for port, device, address, current_address in spoofer.find_interfaces():
        try:
            old_mac = main_conf.get('OldMacs', device)
            set_interface_mac(device, old_mac, port)
        except Exception as e:
            logging.warning(e)
            print e


def create_files():
    "Creates File, where located at the file_name"
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    files_name_file = (main_conf.get("Paths", "fileNames"))
    files_name = open(files_name_file, 'r')
    print("Creating Files...\n")
    for file_name in files_name:
        try:
            file_name = file_name.rstrip()
            if not os.path.isfile(file_name):
                dir_path = os.path.dirname(file_name)
                if not os.path.isdir(dir_path):
                    try:
                        os.makedirs(dir_path)
                    except OSError:
                        logging.warning("Couldn't make dir " + repr(dir))
                        print("Couldn't make dir " + repr(dir))
                f = open(file_name, 'w+')
                f.close()
                print(repr(file_name))
        except Exception as e:
            logging.warning(e)
            print e
    print("Done!")
    return


def remove_files():
    "Remove Files, where located at the file_name"
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    files_name_file = (main_conf.get("Paths", "fileNames"))
    files_name = open(files_name_file, 'r')
    print("Removing Files...\n")
    for file_name in files_name:
        try:
            file_name = file_name.rstrip()
            if os.path.isfile(file_name):
                os.remove(file_name)
                dir_path = os.path.dirname(file_name)
                try:
                    os.removedirs(dir_path)
                except OSError as exception:
                    pass
                print(file_name)
        except Exception as e:
            logging.warning(e)
            print e
    print("Done!")
    return


def create_dummy_process():
    "runs filepath as a process at system startup"
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    src = (main_conf.get("Paths", "processExec"))
    process_list_file = (main_conf.get("Paths", "processList"))
    process_list = open(process_list_file, 'r')
    for filepath in process_list:
        try:
            filepath = filepath.strip()
            filename = os.path.splitext(os.path.basename(filepath))[0]
            reg_path = "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

            # copy file to filepath
            if os.path.exists(filepath):
                os.remove(filepath)
            shutil.copy2(src, filepath)

            # add to registry
            key = wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE, reg_path, 0, wreg.KEY_ALL_ACCESS)
            wreg.SetValueEx(key, filename, 0, wreg.REG_SZ, filepath)
            wreg.CloseKey(key)
            subprocess.Popen(filepath, creationflags=DETACHED_PROCESS)
            print ("Created Process " + filepath)
        except Exception as e:
            logging.warning(e)


def run_powershell():
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    script_name = (main_conf.get("Paths", "psScript"))
    psScript = os.path.abspath(script_name)
    cmd = "powershell -ExecutionPolicy Bypass -Command \"" + psScript + " Install\""
    print cmd
    proc = subprocess.call(cmd, shell=True)


def create_pseudo_devices():
    global pipe1
    global pipe2
    try:
        pipe1 = win32pipe.CreateNamedPipe("\\\\.\\pipe\VBoxMiniRdDN", win32pipe.PIPE_ACCESS_DUPLEX,
                                          win32pipe.PIPE_TYPE_MESSAGE,
                                          win32pipe.PIPE_UNLIMITED_INSTANCES,
                                          65536, 65536, 10, None)
        pipe2 = win32pipe.CreateNamedPipe("\\\\.\\pipe\VBoxTrayIPC", win32pipe.PIPE_ACCESS_DUPLEX,
                                          win32pipe.PIPE_TYPE_MESSAGE,
                                          win32pipe.PIPE_UNLIMITED_INSTANCES,
                                          65536, 65536, 10, None)
    except Exception as e:
        logging.warning(e)
    # f = win32file.CreateFile("\\.\\VBoxTrayIPC", win32file.GENERIC_READ,
    #                          win32file.FILE_SHARE_READ, None, win32file.CREATE_NEW, 0, None)


def remove_pseudo_devices():
    if pipe1 != 0:
        pipe1.close()
    if pipe2 != 0:
        pipe2.close()


def create_vboxtray_windows():
    # Register the Window class.
    wc = win32gui.WNDCLASS()
    hinst = wc.hInstance = win32api.GetModuleHandle(None)
    wc.lpszClassName = "VBoxTrayToolWndClass"
    wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
    wc.hCursor = win32api.LoadCursor(0, win32con.IDC_ARROW)
    wc.hbrBackground = win32con.COLOR_WINDOW

    # Don't blow up if class already registered to make testing easier
    try:
        classAtom = win32gui.RegisterClass(wc)
    except win32gui.error, err_info:
        if err_info.winerror != winerror.ERROR_CLASS_ALREADY_EXISTS:
            raise

    # Create the Window.
    style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
    hwnd = win32gui.CreateWindow(wc.lpszClassName, "VBoxTrayToolWnd", style, 0, 0,
                                 win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0,
                                 hinst, None)
    win32gui.UpdateWindow(hwnd)

# Main
if __name__ == '__main__':
    # Change working directory to script directory
    try:
        os.chdir(os.path.dirname(sys.argv[0]))
    except Exception as e:
        logging.warning(e)
    logging.basicConfig(filename='iAmLog.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
    # Check if the script runs as admin
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        print "You should run it as admin, exiting..."
        exit(1)
    pipe1 = 0
    pipe2 = 0
    hwnd = 0
    if mode == GUI_MODE:
        logging.info("Running GUI..")
        app = QtGui.QApplication(sys.argv)
        my_app = MyForm()
        my_app.show()
        sys.exit(app.exec_())
    else:
        while True:
            ans = raw_input('Welcome to iAmVM, choose option: \n'
                            '1. Transform to VM Registry\n'
                            '2. Transform back to physical PC\n'
                            '3. Filter reg file\n'
                            '4. Spoof to VM MAC\n'
                            '5. Create VM files\n'
                            '6. Create Processes\n'
                            '7. Add Audits and create services \n'
                            '8. Create pseudo devices \n'
                            '9. Start monitor \n'
                            '10. Create fake windows \n'
                            '11. Exit\n\n'
                            '--> ')
            if ans == '1':
                print 'Transforming to VM...'
                # create_reg_keys()
            elif ans == '2':
                print 'Transforming to physical...'
                # back_to_physical()
            elif ans == '3':
                print 'Filtering reg file...'
                # filter_reg_file()
            elif ans == '4':
                print 'Changing MAC...'
                # spoof_to_vm_mac()
            elif ans == '5':
                print 'Creating VM files...'
                # create_files()
            elif ans == '6':
                print 'Creating dummy processes...'
                # create_dummy_process()
            elif ans == '7':
                print 'Adding audits and creating services...'
                # run_powershell()
            elif ans == '8':
                print 'Creating pseudo devices...'
                # create_pseudo_devices()
            elif ans == '9':
                print 'Daemon started'
                # os.popen("pythonw daemon.py")
            elif ans == '10':
                print 'Creating fake windows...'
                # create_vboxtray_windows()
            else:
                print 'Have a nice day!'
                exit(1)
