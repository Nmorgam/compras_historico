#!/usr/bin/env python
# coding: utf-8

# In[3]:


import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# In[ ]:


st.title('NBA Player Stats Explorer')

st.markdown("""
This app performs simple webscrapping of NBA players stats data!
* **Pyhton libraries:** base64, pandas, streamlit
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/)
""")

st.sidebar.header('User Input Features')
selected_year= st.sidebar.selectbox('Year', list(reversed(range(1950,2020))))

#Web scraping of NBA player stats

@st.cache_data
def load_data(year):
    url= "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html= pd.read_html(url, header=0)
    df= html[0]
    raw= df.drop(df[df.Age=='Age'].index) #delete repeating headers in content
    raw= raw.fillna(0)
    playerstats= raw.drop(['Rk'], axis=1)
    return playerstats
playerstats= load_data(selected_year)

#Sidebar - Team selection
sorted_unique_team= sorted(playerstats['Team'].dropna().unique(), key=str)
selected_team= st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

#Sidebar -Position selection
unique_pos=['C','PF','SF','PG','SG']
selected_pos= st.sidebar.multiselect('Position', unique_pos, unique_pos)

#Filtering data
df_selected_team= playerstats[(playerstats['Team'].isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]

st.header('Display Player Stats of Selected Team(s)')
st.write('Data Dimension: ' + str(df_selected_team.shape[0]) + ' rows and ' + str(df_selected_team.shape[1]) + ' columns.')
st.dataframe(df_selected_team)

#Download NBA player stats data
#https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv= df.to_csv(index=False)
    b64= base64.b64encode(csv.encode()).decode() #strings <-> bytes conversions
    href= f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

#Heatmap
if st.button('Intercorrelation Heatmpa'):
    st.header('Intercorrelation Matrix Heatmap')
    df_selected_team.to_csv('output.csv', index=False)
    df= pd.read_csv('output.csv')

    corr= playerstats.corr(numeric_only=True)
    mask= np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, fmt=".2f", ax=ax)
    st.pyplot(fig)


