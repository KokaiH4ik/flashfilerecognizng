import re
import pandas as pd
import sys
import subprocess
import multiprocessing
import time
import pickle


#
#debug log_file_path = ''
log_file_path = sys.argv[1]
line_number=0
# Table creation
data = {
    'PartNumber': [],
    'SerialNumber': [],
    'Status': [],
    'Error': []
}

log_data = []

def send_data(data):
    with multiprocessing.Manager() as manager:
        shared_data = manager.dict(data)
        gui_process = multiprocessing.Process(target=send_to_gui, args=(shared_data,))
        gui_process.start()
        gui_process.join()

# Opening and reading the log file
with open(log_file_path, 'r') as file:
    log_data = file.readlines()

# Function for extracting information from a log line
def extract_info(line,line_number,log_data):
    match_serial = re.search(r'\sA0(\w+):', line)
    Done=False
    Done_error_data=False
    status=' '
    error=' '

    serial_number = 'A0'+ match_serial.group(1) if match_serial else None
    if match_serial: 
        match_status = re.search(serial_number + ': (\w+)', line)
        status = match_status.group(1) if match_status else None
        part_number = serial_number[:8]
    if status == 'Failed':
        #error=serial_number+': '
        nest_match = re.search(r'Nest (\d+)', line)
        nest_failed= 'Nest '+ nest_match.group(1)
        while Done==False:
            line=log_data[line_number]
            if nest_failed in line and 'Failed:' in line:
                line_number=line_number+1
                line=log_data[line_number]
                while Done_error_data==False:
                    line=log_data[line_number]
                    if 'with duration:' in line:
                        Done=True
                        Done_error_data=True
                    else:
                        error=error+line.replace('\n', '')
                        line_number=line_number+1

            else:
                line_number=line_number+1
    elif status == 'OK' or status == 'Skipped':
        error = 'No Error'
    if serial_number ==None:
            part_number=None
            status=None
            error=None
    return part_number, serial_number, status, error 

# Processing log lines and filling the table
for line in log_data:
    part_number, serial_number, status, error = extract_info(line,line_number, log_data)
    line_number=line_number+1
    
    if serial_number:
        data['SerialNumber'].append(serial_number)
    if part_number:
        data['PartNumber'].append(part_number)
    if status:
        data['Status'].append(status)
    if error:
        data['Error'].append(error)

# Output of the resulting table
print(data)

df = pd.DataFrame(data)

# Counting the number of identical values in the 'PartNumber' column
part_number_counts = df['PartNumber'].value_counts()
status_counts = df['Status'].value_counts()
error_counts = df['Error'].value_counts()


# Results output
print(part_number_counts)
print(status_counts)
print(error_counts)

with open('data.pkl', 'wb') as file:
    pickle.dump(data, file)