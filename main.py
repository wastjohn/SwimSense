"""
File: main.py

This file contains the data cleaning and visualization scripts for the swim accelerometer project.

-------------------IDEAS-------------------
Current: tkinter gui to display the data
Pros: familiar with the syntax
Cons: might not be the most efficient way of displaying the data; cant host on github pages

Potential: website hosted on github
Pros: assuming this were to get implemented on the team, would allow for ease of access by sending out a link
Cons: less familiar with the syntax
-------------------------------------------

Author: Will St. John
"""

import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from tkVideoPlayer import TkinterVideo
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def clean(filename: str) -> str:
    """Creates a table delineated version of the raw accelerometer data with"_clean" appened to the name.
     
    Args:
        filename (str): file location of raw accelerometer data
    """

    # clean file name logic
    loc = filename.split('/')
    last_loc = loc[-1].split('.')
    filename_clean = str(last_loc[0]) + '_clean.' + str(last_loc[1])
    
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


class viewer:
    """
    A tkinter gui that serves as the primary visualization of the swim accelerometer data. The primary features of this project are:
        1) video of the swimmer using the accelerometer, below which is a
        2) vis of accelerometer data
    
    The video should come with a video player that allows the user to travel around the different frames of the video. A line in the 
    progress bar of the video should be synced with a line in the vis of the accelerometer data, allowing the user to match moments in 
    the video with data points in the accelerometer.
    """
    def __init__(self) -> None:
        # creating the root frame
        self.rootwin = tk.Tk()
        self.rootwin.title('Swim Accelerometer Viewer')

        # creating the video frame
        self.video_frame = tk.Frame(master=self.rootwin)
        self.video_frame.pack()

        # creating the data vis frame
        self.graph_frame = tk.Frame(master=self.rootwin)
        self.graph_frame.pack()

        # creating the videoplayer
        self.videoplayer = TkinterVideo(master=self.video_frame, scaled=True)
        self.videoplayer.pack(expand=True, fill='both')

        # displaying the data vis
        self.data_test = tk.Label(master=self.graph_frame, text="Data Test")
        self.data_test.pack(expand=True, fill='both')

        # exit button creation
        self.exit_button = tk.Button(text="Exit", command=self.exit, master=self.rootwin)
        self.exit_button.pack()

    # initializing the gui
    def run(self):
        self.rootwin.mainloop()

    # exiting the program
    def exit(self):
        self.rootwin.destroy()

    # cleaning a file
    filename = 'data/Rec_0706_190508.txt'  # raw data file location
    clean_filename = clean(filename)  # cleaning the file

    # reading the cleaned data and removing blank column
    df = pd.read_csv(clean_filename, delimiter='\t', header=1)
    df.drop(['Unnamed: 18'], axis=1, inplace=True)

    # plotting the data
    ax = df.plot(x='Time', y=['ax'], kind='line', legend=True, grid=True, xlabel='Time', ylabel='Acceleration')
    ay = df.plot(x='Time', y=['ay'], kind='line', legend=True, grid=True, xlabel='Time', ylabel='Acceleration')
    az = df.plot(x='Time', y=['az'], kind='line', legend=True, grid=True, xlabel='Time', ylabel='Acceleration')
    a = df.plot(x='Time', y=['ax','ay','az'], kind='line', legend=True, grid=True, xlabel='Time', ylabel='Acceleration')

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter(df['ax'], df['ay'], df['az'])

    plt.show()

# running the gui
myGui = viewer()
myGui.run()
