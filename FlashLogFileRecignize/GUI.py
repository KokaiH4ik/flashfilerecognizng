import PySimpleGUI as sg
import pandas as pd
import os.path
import subprocess
import sys
import multiprocessing
import time
import pickle

# First the window layout in 2 columns

data = {
    'PartNumber': [],
    'SerialNumber': [],
    'Status': [],
    'Error': []
}

file_list_column = [
    [
        sg.Text("Logs Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=['Chose Working Folder'], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]

# For now will only show the name of the file that was chosen
Data_List_column = [
    [sg.Text("PN: - Choose an PN on left", key="-PN-")],
    [sg.Text("PASS:",key="-PASS-")],
    [sg.Text("FAIL:",key="-FAIL-")],
    [sg.Text("SKIPPED:",key="-SKIPPED-")],
    #[sg.Text(size=(40, 1), key="-SKIPPED-")],
    [sg.Text("Pass Yield:",key="-Pass_Yield-")],
    #[sg.Text(size=(40, 1), key="-Pass_Yield-")],
    [sg.Text(" ",key="-Error-")],
    #[sg.Text(size=(40, 1), key="-Error-")],
]


PartNumbers_List_column = [
    [
        sg.Listbox(
            values=['Chose File on left'], enable_events=True, size=(40, 20), key="-PART LIST-"
        )
    ],
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(PartNumbers_List_column),
        sg.VSeperator(),
        sg.Column(Data_List_column),
    ]
]

window = sg.Window("Flash Data Viewer", layout)

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
        ]
        window["-FILE LIST-"].update(fnames)
    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            subprocess.run(["python", "filerecognizer.py", filename])
            with open('data.pkl', 'rb') as file:
                data = pickle.load(file)

            df = pd.DataFrame(data)

            window["-PART LIST-"].update(df['PartNumber'].unique())

        except:
            pass
    elif event == "-PART LIST-":
        try:
            PartNumber = (values["-PART LIST-"][0])
            window["-PN-"].update("PN: "+PartNumber)
            filtered_pass_df=df[(df['PartNumber'] == PartNumber) & (df['Status'] == 'OK')]
            count_ok_for_part_b = len(filtered_pass_df)
            window["-PASS-"].update("PASS: " + str(count_ok_for_part_b))
            filtered_failed_df=df[(df['PartNumber'] == PartNumber) & (df['Status'] == 'Failed')]
            count_failed_for_part_b = len(filtered_failed_df)
            window["-FAIL-"].update("FAIL: " + str(count_failed_for_part_b))
            filtered_skipped_df=df[(df['PartNumber'] == PartNumber) & (df['Status'] == 'Skipped')]
            count_skipped_for_part_b = len(filtered_skipped_df)
            window["-SKIPPED-"].update("SKIPPED: " + str(count_skipped_for_part_b))
            filtered_all_df=df[(df['PartNumber'] == PartNumber)]
            count_all_for_part_b=len(filtered_all_df)
            pass_yield=(count_ok_for_part_b/(count_all_for_part_b-count_skipped_for_part_b))*100
            window["-Pass_Yield-"].update("Pass_Yield: " + str(pass_yield)+"%")
            error_counts = filtered_failed_df['Error'].value_counts()
            if count_failed_for_part_b>0:
                window["-Error-"].update("Error: " + str(error_counts))
            else:
                window["-Error-"].update(" ")
        except:
            pass

window.close()