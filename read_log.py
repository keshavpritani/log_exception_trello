import time
import os
import log_exception
import re
import threading
from datetime import datetime

# Set the filename and open the file
filename = '/var/log/messages'
file = open(filename, 'r')

# Find the size of the file and move to the end
def get_file_last_pos():
    st_results = os.stat(filename)
    return st_results[6]

file.seek(get_file_last_pos())

log_type = ("ERROR", "WARN", "INFO", "DEBUG")

def checkException(str):
    return re.search("exception",str,flags=re.IGNORECASE)

while 1:
    try:
        where = file.tell()
        line = file.readline()
        #print(line)
        #print("Keshav")
        if not line:
            time.sleep(0.01)
            file.seek(where)
        else:
            str_to_find = " ERROR "
            index = line.find(str_to_find)
            #print(line)
            if(index != -1):
                program_name = line.split()[4]
                #print(program_name)
                index = index+len(str_to_find)
                index1 = line.find("-", index)
                exception = line[index:index1]
                desc = line[index1+2:]
                flag=False
                exceptions_list=set()
                if(checkException(line)):
                    flag=True
                while 1:
                    where = file.tell()
                    line = file.readline()
                    if(any(l_type in line for l_type in log_type)):
                        file.seek(get_file_last_pos() - 10)
                        break
                    if(checkException(line)):
                        line_arr = (re.split('[.() :$]', line))
                        exceptions_list = exceptions_list.union(set([txt for txt in line_arr if checkException(txt)]))
                        flag=True
                    desc = desc + line
                if flag:
                    today = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    print(today, "- Exception -", exception)
                    #print("DESC -", desc)
                    threading.Thread(target=log_exception.createCard, args=(program_name, exception, desc ,exceptions_list)).start()
    except Exception as e:
        print("try...catch block")
        print(e)