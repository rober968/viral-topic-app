import streamlit as st
import yt_dlp
import pandas as pd
from groq import Groq
import time

# 1. Page Config
st.set_page_config(page_title="ViralFinder AI", page_icon="🎬", layout="wide")

# Corrected CSS section - replaced 'unsafe_allow_status_code' with 'unsafe_allow_html'
st.markdown("""
    <style>
    .main {
        background-color: #0F172A;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #3B82F6;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #1E293B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 ViralFinder AI")
st.caption("Identify viral outliers and generate content strategies for Class 8 Students & Creators.")

# 2. Sidebar & Secret Handling (The "Auto-Look" Logic)
with st.sidebar:
    st.header("⚙️ App Settings")
    
    # Check if the key exists in Streamlit Secrets
    if "GROQ_API_KEY" in st.secrets:
        groq_key = st.secrets["GROQ_API_KEY"]
        st.success("✅ API Key loaded from Secrets!")
    else:
        # Fallback to manual input if Secrets are empty
        groq_key = st.text_input("Enter Groq API Key", type="password")
        st.warning("⚠️ Key not found in Secrets. Please enter it manually or add it to Streamlit Settings.")
    
    st.divider()
    num_vids = st.slider("Analyze last X videos", 5, 50, 20)
    st.info("Tip: Keeping this under 25 prevents YouTube from blocking the scraper.")

# 3. Scraper Function (Optimized for Realme C25s performance)
def get_channel_data(search_query):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'web_embedded'],
                'skip': ['dash', 'hls']
            }
        },
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search for the channel handle or name
            search_results = ydl.extract_info(f"ytsearch1:{search_query} channel", download=False)
            if not search_results or not search_results['entries']:
                return None, "Channel not found."
            
            first_result = search_results['entries'][0]
            channel_url = first_result.get('channel_url') or first_result.get('url')
            channel_name = first_result.get('uploader', 'Unknown Channel')
            
            # Fetch video list
            dict_meta = ydl.extract_info(f"{channel_url}/videos", download=False)
            videos = dict_meta['entries'][:num_vids]
            
            data = [{"title": v['title'], "views": v.get('view_count', 0)} for v in videos if v.get('title')]
            return data, channel_name
            
    except Exception as e:
        return None, f"Scraper Error: {str(e)}"

# 4. Main UI Logic
channel_input = st.text_input("YouTube Handle or Channel Name", placeholder="@JamesJani")

if st.button("🚀 Generate Viral Blueprint"):
    if not groq_key:
        st.error("Missing API Key! Please add it to Streamlit Secrets or the sidebar.")
    elif not channel_input:
        st.warning("Please enter a channel handle to begin.")
    else:
        with st.spinner(f"Scanning {channel_input}..."):
            data, name_found = get_channel_data(channel_input)
            
            if data:
                st.success(f"Connected to: {name_found}")
                df = pd.DataFrame(data)
                
                # Logic: Identify "Outliers" (Videos performing 20% better than average)
                avg_views = df['views'].mean()
                outliers = df[df['views'] > (avg_views * 1.2)].sort_values(by='views', ascending=False)
                
                # Display Results Table
                st.subheader("📊 Viral Outlier Data")
                st.dataframe(outliers[['title', 'views']], use_container_width=True)
                
                # AI Analysis with Groq (Llama 3)
                try:
                    client = Groq(api_key=groq_key)
                    top_titles = ", ".join(outliers['title'].tolist()[:5])
                    
                    # Prompt tailored for History/Business/Psychology niche
                    prompt = (f"Analyze these high-performing YouTube titles: {top_titles}. "
                              "1. Identify the 'Hook' (Curiosity, Fear, or Desire). "
                              "2. Based on this, suggest 5 new video titles for a niche channel about "
                              "History, Business stories, or Dark Psychology. "
                              "3. Write a 1-sentence opening hook in Bangla for each suggestion.")
                    
                    completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama3-8b-8192",
                    )
                    
                    st.divider()
                    st.subheader("🧠 AI-Generated Script Blueprint")
                    st.markdown(completion.choices[0].message.content)
                    
                except Exception as ai_err:
                    st.error(f"AI Error: {str(ai_err)}")
            else:
                st.error(f"Could not fetch data: {name_found}")

# 5. Footer for Mobile
st.divider()
st.caption("Built for Realme C25s • Powered by Llama 3 & yt-dlp")
