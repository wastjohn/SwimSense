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
    # Do stuff in the dashboard tab
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


    # calculate pitch, roll, and yaw
    

    st.dataframe(df)

    acc_options = st.multiselect("Select accelerometer data to plot", options=['ax', 'ay', 'az'], key="accel_options")
    afig = px.line(df, x='t', y=acc_options, labels={"x": "Time [s]", "y": "Acceleration [m/s^2]"})
    st.plotly_chart(afig, key="accel_plot_dash")

    gyro_options = st.multiselect("Select gyro data to plot", options=['gx', 'gy', 'gz'], key="gyro_options")
    gfig = px.line(df, x='t', y=gyro_options, labels={'x': "Time [s]", 'y': 'Rotation [rad/s]'})
    st.plotly_chart(gfig, key="gyro_plot_dash")

    
    st.write("---")

    # finding and saving a swim
    st.header("Swim Detection")
    with st.expander("Swim Detection", expanded=True):
        st.write("This section will allow you to find and save swims from your data.")

        col1, col2 = st.columns(2)
        lb = col1.number_input("Lower Time Bound")
        ub = col2.number_input("Upper Time Bound")

        st.write("Selected time range")
        mask = (df['t'] >= lb) & (df['t'] <= ub)
        fig = px.line(df[mask], x='t', y=acc_options, labels={"x": "Time [s]", "y": "Acceleration [m/s^2]"})
        st.plotly_chart(fig, key="accel_plot_range")

        swimmer = st.text_input("Swimmer Initials", value="WJ")
        new_file = file.name.split('.')[0] + "_onlyswim.csv"
        if st.button("Save Swim"):
            swim_df = df[mask]
            swim_df.to_csv(f"data/swims/{swimmer}/{new_file}", index=False)
            st.success(f"Swim saved successfully as `data/swims/{swimmer}/{new_file}`")


