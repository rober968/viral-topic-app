import streamlit as st
import yt_dlp
import pandas as pd
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="ViralFinder AI", page_icon="🎬", layout="centered")

# Safe Minimal CSS (Using st.html for 2026 stability)
st.html("""
    <style>
    .stApp { background-color: #FFFFFF; }
    header { visibility: hidden; }
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        background-color: #000000;
        color: white;
        border: none;
        height: 3em;
    }
    .stTextInput>div>div>input {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
    }
    </style>
""")

st.title("ViralFinder AI")
st.write("Clean. Minimal. Professional.")

# 2. Sidebar & Secrets
with st.sidebar:
    st.header("Settings")
    # Using .get to prevent crash if key is missing
    groq_key = st.secrets.get("GROQ_API_KEY", "")
    
    if groq_key:
        st.success("System: Online")
    else:
        groq_key = st.text_input("Enter Groq Key", type="password")
    
    num_vids = st.slider("Scan Depth", 5, 30, 15)

# 3. Scraper
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
            vids = meta['entries'][:num_vids]
            
            data = [{"Title": v['title'], "Views": v.get('view_count', 0)} for v in vids if v.get('title')]
            return data, name
    except Exception as e:
        return None, str(e)

# 4. App Logic
channel_input = st.text_input("YouTube Handle", placeholder="@MagnatesMedia")

if st.button("Run Analysis"):
    if not groq_key:
        st.error("Missing API Key.")
    elif not channel_input:
        st.warning("Please enter a handle.")
    else:
        with st.spinner("Scanning..."):
            data, name = get_channel_data(channel_input)
            if data:
                st.subheader(f"Data for {name}")
                df = pd.DataFrame(data)
                avg = df['Views'].mean()
                # Find videos 10% above average
                outliers = df[df['Views'] > (avg * 1.1)].sort_values(by='Views', ascending=False)
                
                st.table(outliers)
                
                try:
                    client = Groq(api_key=groq_key)
                    titles = ", ".join(outliers['Title'].tolist()[:5])
                    
                    prompt = (f"Analyze: {titles}. 1. Identify Hook. 2. Suggest 5 new English titles. "
                              "3. 1-sentence English opening. NO BANGLA.")
                    
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.1-8b-instant", 
                    )
                    
                    result = chat.choices[0].message.content
                    st.divider()
                    st.subheader("English Content Strategy")
                    
                    # 📋 SAFE COPY AREA
                    st.text_area("Select and Copy below:", value=result, height=350)
                    
                except Exception as e:
                    st.error(f"AI Error: {e}")
            else:
                st.error(f"Search Error: {name}")

st.divider()
st.caption("ViralFinder AI • v2.1 Stable")
