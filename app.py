import streamlit as st
import yt_dlp
import pandas as pd
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="ViralFinder AI", page_icon="🎬", layout="centered")

# 2. Stable Black Theme CSS (Fixes White Screen & Syntax errors)
st.html("""
    <style>
    .stApp { background-color: #000000 !important; color: #FFFFFF !important; }
    header { visibility: hidden; }
    .stTextInput>div>div>input {
        background-color: #1A1A1A !important;
        color: white !important;
        border: 1px solid #333333 !important;
    }
    [data-testid="stSidebar"] { background-color: #0D0D0D !important; }
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        background-color: #2563EB !important;
        color: white !important;
        border: none;
        height: 3.5em;
        font-weight: bold;
    }
    .stTable { background-color: #000000 !important; color: white !important; }
    .stTextArea>div>div>textarea {
        background-color: #1A1A1A !important;
        color: #34D399 !important;
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

# 4. Scraper Logic (Fixed Syntax)
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
            if not search_results or not search_results.get('entries'):
                return None, "Channel not found."
            
            first = search_results['entries'][0]
            url = first.get('channel_url') or first.get('url')
            name = first.get('uploader', 'Channel')
            
            meta = ydl.extract_info(f"{url}/videos", download=False)
            # FIXED SYNTAX BELOW
            vids = meta.get('entries', [])[:num_vids]
            
            data = [{"Title": v['title'], "Views": v.get('view_count', 0)} for v in vids if v.get('title')]
            return data, name
    except Exception as e:
        return None, str(e)

# 5. Execution
channel_input = st.text_input("YouTube Handle", placeholder="@MagnatesMedia")

if st.button("Generate Viral Blueprint"):
    if not groq_key:
        st.error("Missing API Key in Secrets.")
    elif not channel_input:
        st.warning("Please enter a handle.")
    else:
        with st.spinner("Analyzing..."):
            data, name = get_channel_data(channel_input)
            if data:
                st.subheader(f"Insights for {name}")
                df = pd.DataFrame(data)
                avg = df['Views'].mean()
                outliers = df[df['Views'] > (avg * 1.1)].sort_values(by='Views', ascending=False)
                
                st.table(outliers)
                
                try:
                    client = Groq(api_key=groq_key)
                    titles_list = ", ".join(outliers['Title'].tolist()[:5])
                    
                    prompt = (f"Analyze: {titles_list}. 1. Identify Hook. 2. Suggest 5 new English titles for History/Business/Psychology. "
                              "3. 1-sentence English opening. STRICTLY NO BANGLA.")
                    
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.1-8b-instant", 
                    )
                    
                    result = chat.choices[0].message.content
                    st.divider()
                    st.subheader("Strategy (English)")
                    
                    st.text_area("Select all to copy:", value=result, height=350)
                    
                except Exception as e:
                    st.error(f"AI Error: {e}")
            else:
                st.error(f"Error: {name}")

st.divider()
st.caption("ViralFinder AI • v2.6 Stable")
