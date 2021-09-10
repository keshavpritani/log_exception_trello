import time
import os
from log_exception import *
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
    re.search("exception",str,flags=re.IGNORECASE)

while 1:
    try:
        where = file.tell()
        line = file.readline()
        print(line[:120])
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
<<<<<<< HEAD
                if(checkException(line)):
                    flag=True
=======
                # if(re.search("exception",line,flags=re.IGNORECASE)):
                #     flag=True
>>>>>>> parent of d576500 (Added locking)
                while 1:
                    where = file.tell()
                    line = file.readline()
                    if(any(l_type in line for l_type in log_type)):
                        file.seek(get_file_last_pos() - 10)
                        break
<<<<<<< HEAD
                    if(checkException(line)):
                        line_arr = (re.split('[.() :$]', line))
                        exceptions_list = exceptions_list.union(set([match for match in line_arr if checkException(match)]))
=======
                    if(re.search("exception",line,flags=re.IGNORECASE)):
                        line_arr = (re.split('[.() :$]', line))
                        exceptions_list = exceptions_list.union(set([match for match in line_arr if re.search("exception",match,flags=re.IGNORECASE)]))
>>>>>>> parent of d576500 (Added locking)
                        flag=True
                    desc = desc + line
                if flag:
                    today = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    print(today, "- Exception -", exception)
                    #print("DESC -", desc)
<<<<<<< HEAD
                    threading.Thread(target=createCard, args=(program_name, exception, desc ,exceptions_list)).start()
=======
                    threading.Thread(target=log_exception.createCard, args=(program_name, exception, desc ,exceptions_list)).start()
            # else:
                # print("Not Found")
>>>>>>> parent of d576500 (Added locking)
    except Exception as e:
        print("try...catch block")
        print(e)
