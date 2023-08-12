import streamlit as st
import pandas as pd
import plotly.express as px
import acc_clean

raw_data = 'raw_data/Rec_0811_135957.txt'
clean_data = acc_clean.clean(raw_data)

df = pd.read_csv(clean_data, sep='\t', header=1)
df.drop(['Unnamed: 18'], axis=1, inplace=True)

all_fig = px.line(df, x="Time", y=["ax", "ay", "az"])

ax_fig = px.line(
    df,
    x="Time",
    y="ax"
)

ay_fig = px.line(
    df,
    x="Time",
    y="ay"
)

az_fig = px.line(
    df,
    x="Time",
    y="az"
)

st.plotly_chart(all_fig)

# col1, col2, col3 = st.columns(3)
# with col1:
#     st.plotly_chart(ax_fig, use_container_width=False)
# with col2:
#     st.plotly_chart(ay_fig, use_container_width=False)
# with col3:
#     st.plotly_chart(az_fig, use_container_width=False)