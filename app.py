import streamlit as st
import yt_dlp
import pandas as pd
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="ViralFinder AI", page_icon="🎬", layout="centered")

# 2. Force Black Theme CSS (Removes White Screen)
st.html("""
    <style>
    /* Force Background to Black */
    .stApp { 
        background-color: #000000 !important; 
        color: #FFFFFF !important; 
    }
    
    /* Hide Streamlit Header */
    header { visibility: hidden; }
    
    /* Input Boxes: Dark Gray with White Text */
    .stTextInput>div>div>input {
        background-color: #1A1A1A !important;
        color: white !important;
        border: 1px solid #333333 !important;
    }
    
    /* Sidebar: Deep Charcoal */
    [data-testid="stSidebar"] {
        background-color: #0D0D0D !important;
    }
    
    /* Buttons: Electric Blue for Visibility on Black */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        background-color: #2563EB !important;
        color: white !important;
        border: none;
        height: 3.5em;
        font-weight: bold;
    }
    
    /* Results Table */
    .stTable {
        background-color: #000000 !important;
        color: white !important;
    }
    
    /* Text Area for Copying */
    .stTextArea>div>div>textarea {
        background-color: #1A1A1A !important;
        color: #34D399 !important; /* Green text for a 'Terminal' look */
        border: 1px solid #333333 !important;
    }
    </style>
""")

st.title("ViralFinder AI")
st.caption("Content Strategy Engine • Black Edition")

# 3. Sidebar & Secrets
with st.sidebar:
    st.header("Settings")
    groq_key = st.secrets.get("GROQ_API_KEY", "")
    
    if groq_key:
        st.success("API Status: Online")
    else:
        groq_key = st.text_input("Enter Groq Key", type="password")
    
    num_vids = st.slider("Analyze Videos", 5, 30, 15)

# 4. Scraper Logic
def get_channel_data(search_query):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch1:{search_query} channel", download=False)
            if not search_results or not search_results['entries']:
                return None, "Channel not found."
            
            first = search_results['entries'][0]
            url = first.get('channel_url') or first.get('url')
            name = first.get('uploader', 'Channel')
            
            meta = ydl.extract_info(f"{url}/videos", download=False)
            vids = meta['entries'][:
