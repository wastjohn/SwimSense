import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="SwimSense Dashboard", page_icon=":swimmer:")

st.title("Welcome to SwimSense!")
st.write("Here is where you will process and analyze your swimming data")

with st.sidebar:
    st.header("File Upload")
    file = st.file_uploader("Upload your swimming data file", type="csv")


st.header("Data Preview")

# calulate offsets
df_offsets = pd.read_csv("data/offsets/offset0.csv", names=['t', 'ax', 'ay', 'az', 'gx', 'gy', 'gz'])
ax_offset = df_offsets["ax"].median()
ay_offset = df_offsets["ay"].median()
az_offset = df_offsets["az"].median()
gx_offset = df_offsets["gx"].median()
gy_offset = df_offsets["gy"].median()
gz_offset = df_offsets["gz"].median()

st.write("Offsets (taken from `data/offsets/offset0.csv`):")
st.write(f"ax: `{ax_offset:.2f}`, ay: `{ay_offset:.2f}`, az: `{az_offset:.2f}`")
st.write(f"gx: `{gx_offset:.2f}`, gy: `{gy_offset:.2f}`, gz: `{gz_offset:.2f}`")


if file:
    df = pd.read_csv(file, names=['t', 'ax', 'ay', 'az', 'gx', 'gy', 'gz'])
    df['t'] = df['t'] - df['t'][0]  # Normalize time to start from zero
    df['t'] = df['t'] / 1000  # Convert to seconds
    
    # Apply offsets
    df['ax'] -= ax_offset
    df['ay'] -= ay_offset
    df['az'] -= az_offset
    df['gx'] -= gx_offset
    df['gy'] -= gy_offset
    df['gz'] -= gz_offset

    st.dataframe(df)

    acc_options = st.multiselect("Select accelerometer data to plot", options=['ax', 'ay', 'az'])
    afig = px.line(df, x='t', y=acc_options, labels={"x": "Time [s]", "y": "Acceleration [m/s^2]"})
    st.plotly_chart(afig)

    gyro_options = st.multiselect("Select gyro data to plot", options=['gx', 'gy', 'gz'])
    gfig = px.line(df, x='t', y=gyro_options, labels={'x': "Time [s]", 'y': 'Rotation [rad/s]'})
    st.plotly_chart(gfig)

    




