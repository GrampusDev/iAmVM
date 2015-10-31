import _winreg as wreg
import os
import random
import ctypes
import ConfigParser
from spoofmac.interface import (
    set_interface_mac,
    get_os_spoofer
)

# Main configuration file
main_conf_path = r".\iAmVM_conf.ini"


# Represents registry value
class RegValue:
    def __init__(self, val_name, val_type, val_data):
        self.name = val_name
        self.type = val_type
        self.data = val_data


def apply_reg_change(reg_key, reg_values):
    """
    Creates (or updates if already exist) reg_key values

    :param reg_key: Registry key to insert value to
    :param reg_values: New values for the key
    """
    for val in reg_values:
        wreg.SetValueEx(reg_key, val.name, 0, val.type, val.data)


# TODO: This function
def remove_reg_keys():
    try:
        wreg.DeleteKeyEx(wreg.HKEY_LOCAL_MACHINE,
                         "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Oracle VM VirtualBox Guest Additions",
                         (wreg.KEY_WOW64_64KEY + wreg.KEY_ALL_ACCESS), 0)
    except WindowsError as err:
        print "Failed to delete: ", err


def create_reg_keys():
    """
    Creates VM specific keys in the Registry
    """
    reg_conf = ConfigParser.ConfigParser()
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)

    # Get sections from already filtered reg file
    reg_conf.read(main_conf.get("Paths", "FilteredRegFile"))
    sections = reg_conf.sections()

    for sec in sections:
        sec_without_hklm = sec.replace("HKEY_LOCAL_MACHINE\\", "")

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
                print "Failed to create key :" + sec + '\n', e
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
                    reg_values.append(RegValue(opt, wreg.REG_DWORD, int(opt_data)))
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
            if '[HKEY' in line and ']' in line:
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
                #         (r"{" in line and r"}" in line) or \
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

        # Save old MAC
        main_conf.set('OldMacs', device, address.replace('-', ':'))

        new_mac = get_random_mac()
        set_interface_mac(device, new_mac, port)
    f = open(main_conf_path, 'w')
    main_conf.write(f)
    f.close()



def revert_to_physical_mac():
    """
    Revert to old MAC
    """
    main_conf = ConfigParser.ConfigParser()
    main_conf.read(main_conf_path)
    spoofer = get_os_spoofer()
    for port, device, address, current_address in spoofer.find_interfaces():
        old_mac = main_conf.get('OldMacs', device)
        set_interface_mac(device, old_mac, port)



# Main
if __name__ == '__main__':
    # Check if the script runs as admin
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        print "You should run it with as admin, exiting..."
    else:
        ans = raw_input('Welcome to iAmVM, choose option: \n'
                        '1. Transform to VM Registry\n'
                        '2. Transform back to physical PC\n'
                        '3. Filter reg file\n'
                        '4. Spoof to VM MAC\n'
                        '5. Revert to physical MAC\n'
                        '6. Exit\n\n'
                        '--> ')
        if ans == '1':
            print 'Transforming to VM...'
            create_reg_keys()
        elif ans == '2':
            print 'Transforming to physical...'
            # TODO: remove_reg_keys
            remove_reg_keys()
        elif ans == '3':
            print 'Filtering reg file...'
            filter_reg_file()
        elif ans == '4':
            print 'Changing MAC...'
            spoof_to_vm_mac()
        elif ans == '5':
            print 'Reverting MAC...'
            revert_to_physical_mac()
        else:
            print 'Have a nice day!'
