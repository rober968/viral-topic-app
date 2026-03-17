import streamlit as st
import yt_dlp
import pandas as pd
from groq import Groq
import time

# 1. Page Config
st.set_page_config(page_title="AI Viral Topic Finder", page_icon="🎬")
st.title("🎬 YouTube Topic Searcher (Stealth Mode)")

# 2. Sidebar Settings
with st.sidebar:
    st.header("App Config")
    groq_key = st.text_input("Groq API Key", type="password")
    num_vids = st.slider("Analyze last X videos", 5, 50, 15)
    st.info("Tip: Keep 'Analyze' under 20 to avoid being flagged as a bot.")

# 3. Enhanced Scraper Function
def get_channel_data(search_query):
    # These settings help bypass "Sign in to confirm you're not a bot"
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        # STEALTH ARGS: Tells YT we are a TV/Embedded client
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
            # Step A: Search for the channel
            search_results = ydl.extract_info(f"ytsearch1:{search_query} channel", download=False)
            if not search_results or not search_results['entries']:
                return None, "Channel not found."
            
            first_result = search_results['entries'][0]
            channel_url = first_result.get('channel_url') or first_result.get('url')
            channel_name = first_result.get('uploader', 'Unknown Channel')
            
            # Step B: Get videos
            dict_meta = ydl.extract_info(f"{channel_url}/videos", download=False)
            videos = dict_meta['entries'][:num_vids]
            
            data = [{"title": v['title'], "views": v.get('view_count', 0)} for v in videos if v.get('title')]
            return data, channel_name
            
    except Exception as e:
        return None, f"Error: {str(e)}"

# 4. Main App UI
channel_name_input = st.text_input("Enter Channel Name or @Handle")

if st.button("Find Viral Topics"):
    if not groq_key:
        st.warning("Please enter your Groq API Key in the sidebar.")
    elif not channel_name_input:
        st.error("Please enter a name!")
    else:
        with st.spinner(f"Searching for '{channel_name_input}'..."):
            data, name_found = get_channel_data(channel_name_input)
            
            if data and isinstance(data, list):
                st.success(f"Connected to: {name_found}")
                df = pd.DataFrame(data)
                
                # Logic: Find outliers
                avg_views = df['views'].mean()
                outliers = df[df['views'] > avg_views].sort_values(by='views', ascending=False)
                
                # Display Results
                st.subheader("📊 Performance Data")
                st.dataframe(outliers[['title', 'views']])

                # AI Generation
                client = Groq(api_key=groq_key)
                top_titles = ", ".join(outliers['title'].tolist()[:5])
                
                prompt = (f"Analyze these viral YouTube titles: {top_titles}. "
                          "1. What is the emotional hook? "
                          "2. Suggest 5 new, clickable title ideas for a Class 8 student niche. "
                          "Keep suggestions in English and Bangla where appropriate.")
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                )
                
                st.divider()
                st.subheader("💡 AI Generated Blueprint")
                st.markdown(chat.choices[0].message.content)
            else:
                st.error(f"Failed to fetch data. {name_found}")
