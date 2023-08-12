"""
File: st.main.py

This script create the visualization of the accelerometer data using streamlit. The app consists of 2 pages. 
The first page is the visualization of the data. This page could consist of 3 sections. The first section is 
an introductory section on what to expect and how to use the app's features. The second sections is a file 
upload button that allows the user to upload a clean version of the accelerometer data. The third section is
the visualization section. This section contains a video of the acceleration recording, along with an x, y, 
and z visualization of the respective acceleration vs time data. The goal is to sync each plot to the video,
allowing for a seemless comparison between the quality of swimming provided by the video and the quanitative
values associated with the acceleration at the corresponding time.

The second page will be used primarily for processing raw data and creating clean data products that can be 
used on the main page. The goal of this section is to streamline the process of creating individualized 
clean data products so that each swimmer knows what data is theirs to use.

Author: Will St. John
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import acc_clean

##################################
###### Introductory Section ######
##################################
st.set_page_config(layout="wide")
st.title("Swim Accelerometer Visualizations")
st.write("Welcome! This page will allow you to compare the quality of your swimming ability with quantitative values obtained from your accelerometer session.")

st.header("Instructions")
st.write("The use of this app is fairly straightforward. Using swim video file and corresponding accelerometer data file, upload the two files to the app using the corresponding upload buttons below")

st.subheader("Upload Swim Video and Accelerometer Data File")

with st.container():
    video_col, data_col = st.columns(2)
    with video_col:
        video_file = st.file_uploader(label="Swim Video")
    with data_col:
        data_file = st.file_uploader(label="Swim Accelerometer Data txt File")
st.divider()

if video_file is not None:
    st.video(video_file)
else:
    st.write("Video file will appear here")


if data_file is not None:
    df = pd.read_csv(data_file, sep='\t', header=1)

    df_len = len(df['Time'])
    
    domain_spread = st.slider(label="domain spread", min_value=3, max_value=10)
    slider_value = st.slider(label='slider',min_value=0, max_value=df_len-1)

    df2 = pd.DataFrame()
    time = []
    ax = []
    ay = []
    az = []
    for i in range(-domain_spread,domain_spread+1):
        time.append(df["Time"][slider_value+i])
        ax.append(df["ax"][slider_value+i])
        ay.append(df["ay"][slider_value+i])
        az.append(df["az"][slider_value+i])

    df2["Time"] = time
    df2["ax"] = ax
    df2["ay"] = ay
    df2["az"] = az
    
    all_fig = px.line(df, x="Time", y=["ax", "ay", "az"])
    ax_fig = px.line(df2, x="Time", y="ax")
    ay_fig = px.line(df2, x="Time", y="ay")
    az_fig = px.line(df2, x="Time", y="az")

    st.plotly_chart(all_fig, use_container_width=True)

    colx, coly, colz = st.columns(3)
    with colx:
        st.plotly_chart(ax_fig, use_container_width=True)
    with coly:
        st.plotly_chart(ay_fig, use_container_width=True)
    with colz:
        st.plotly_chart(az_fig, use_container_width=True)



# Cleaning the data
# raw_data = 'raw_data/Rec_0811_135957.txt'
# clean_data = acc_clean.clean(raw_data)

# df = pd.read_csv(clean_data, sep='\t', header=1)
# df.drop(['Unnamed: 18'], axis=1, inplace=True)


