import os
import os.path
import shutil
import _winreg as wreg
def create_files():
    "Creates File, where located at the file_name"
    files_name_file= "./Files.txt"
    files_name=open(files_name_file,'r')
    print("Creating Files...\n")
    for file in files_name:
        file=file.rstrip()
        if not os.path.isfile(file):
            dir_path = os.path.dirname(file)
            if not os.path.isdir(dir_path):
                try:
                    os.makedirs(dir_path)
                except OSError as exception:
                    print("Couldn't make dir " + repr(dir))
            f=open(file,'w+')
            f.close()      
            print(repr(file))
    print("Done!")
    return

def remove_files():
    "Remove Files, where located at the file_name"
    files_name_file= "./Files.txt"
    files_name=open(files_name_file,'r')
    print("Removing Files...\n")
    for file in files_name:
        file=file.rstrip()
        if os.path.isfile(file):
            os.remove(file)
            dir_path = os.path.dirname(file)
            try:
                os.removedirs(dir_path)
            except OSError as exception:
                pass
            print(file)
    print("Done!")
    return


def create_dummy_prcoess(filepath):
	"runs filepath as a process at system startup"
	src="./Dummy.exe"
	filename=os.path.splitext(os.path.basename(filepath))[0]
	reg_path="SOFTWARE\Microsoft\Windows\CurrentVersion\Run" 
	
	#copy file to filepath
	if os.path.exists(filepath):
             os.remove(filepath)
	shutil.copy2(src,filepath)
	
	#add to registry
	key=wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE,reg_path,0,wreg.KEY_ALL_ACCESS)		
	wreg.SetValueEx(key,filename,0,wreg.REG_SZ,filepath)
	wreg.CloseKey(key)
	print ("Created Process " + filepath)
	
	
if __name__ == '__main__':
	filepath="C:\Windows\System32\VBoxTray.exe"
	create_dummy_prcoess(filepath)
