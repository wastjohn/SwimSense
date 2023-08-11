"""
File: main.py

This file contains the data cleaning scripts for the swim accelerometer project.

Author: Will St. John
"""


def clean(filename: str) -> str:
    """Creates a tab delineated version of the raw accelerometer data with"_clean" appened to the name
    located in the clean_data directory.

    Note: A trailing tab and improperly formatted first line remain after the cleaning process. This can 
    be solved with pandas by starting the df at the second line in the file and removing the empty column
    at the end of the df.
     
    Args:
        filename (str): file location of raw accelerometer data
    """

    # clean file name logic
    loc = filename.split('/')
    last_loc = loc[-1].split('.')
    filename_clean = str('clean_data/'+ last_loc[0]) + '_clean.' + str(last_loc[1])
    
    # cleaning process
    dirty_file = open(filename, 'r')  # open dirty file to read
    clean_file = open(filename_clean, 'w')  # open clean file to write
    for i in dirty_file:  # changing spaces to tabs
        x = i.split(' ')
        while '' in x:
            x.remove('')
        y = ''
        for i in x:
            y += i + '\t'
        y_new = y[:-1]
        clean_file.write(y_new)
    clean_file.close()  # close the clean file
    dirty_file.close()  # close the dirty file
    return filename_clean

