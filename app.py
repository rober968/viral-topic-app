import streamlit as st
import yt_dlp
import pandas as pd
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="ViralFinder AI", page_icon="🎬", layout="centered")

# Classic Minimal UI Styling
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #F8FAFC;
    }
    /* Clean Cards for Data */
    .stDataFrame, .stTable {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
    }
    /* Minimalist Primary Button */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        height: 3em;
        background-color: #1E293B;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #334155;
        color: white;
    }
    /* Input Fields */
    .stTextInput>div>div>input {
        background-color: white;
        color: #1E293B;
        border: 1px solid #CBD5E1;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("ViralFinder AI")
st.write("Analyze YouTube trends and generate English content blueprints.")

# 2. Sidebar & Secret Handling
with st.sidebar:
    st.header("Configuration")
    if "GROQ_API_KEY" in st.secrets:
        groq_key = st.secrets["GROQ_API_KEY"]
        st.success("API Key Loaded")
    else:
        groq_key = st.text_input("Groq API Key", type="password")
    
    num_vids = st.slider("Video Scan Limit", 5, 50, 15)

# 3. Scraper Function
def get_channel_data(search_query):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'extractor_args': {'youtube': {'player_client': ['tv', 'web_embedded']}},
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch1:{search_query} channel", download=False)
            if not search_results or not search_results['entries']:
                return None, "Channel not found."
            first_result = search_results['entries'][0]
            channel_url = first_result.get('channel_url') or first_result.get('url')
            channel_name = first_result.get('uploader', 'Unknown')
            dict_meta = ydl.extract_info(f"{channel_url}/videos", download=False)
            videos = dict_meta['entries'][:num_vids]
            data = [{"Title": v['title'], "Views": v.get('view_count', 0)} for v in videos if v.get('title')]
            return data, channel_name
    except Exception as e:
        return None, f"Error: {str(e)}"

# 4. Main UI Logic
channel_input = st.text_input("Channel Handle", placeholder="@MagnatesMedia")

if st.button("Generate Analysis"):
    if not groq_key:
        st.error("Please provide an API Key.")
    elif not channel_input:
        st.warning("Enter a channel handle.")
    else:
        with st.spinner("Processing..."):
            data, name_found = get_channel_data(channel_input)
            if data:
                st.info(f"Analyzing: {name_found}")
                df = pd.DataFrame(data)
                avg_views = df['Views'].mean()
                outliers = df[df['Views'] > (avg_views * 1.1)].sort_values(by='Views', ascending=False)
                
                st.subheader("Top Performing Content")
                st.dataframe(outliers, use_container_width=True, hide_index=True)
                
                try:
                    client = Groq(api_key=groq_key)
                    top_titles = ", ".join(outliers['Title'].tolist()[:5])
                    
                    prompt = (f"Analyze these YouTube titles: {top_titles}. "
                              "1. Identify the 'Hook'. "
                              "2. Suggest 5 new titles for History/Business/Psychology. "
                              "3. Provide a 1-sentence English opening for each. "
                              "Output strictly in English.")
                    
                    completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.1-8b-instant", 
                    )
                    
                    ai_output = completion.choices[0].message.content
                    st.divider()
                    st.subheader("Content Strategy")
                    st.markdown(ai_output)

                    # --- Copy to Clipboard Implementation ---
                    st.divider()
                    # Using a simple HTML/JS snippet for the copy function
                    copy_code = f"""
                    <script>
                    function copyToClipboard() {{
                        const text = `{ai_output}`;
                        navigator.clipboard.writeText(text).then(() => {{
                            alert("Results copied to clipboard!");
                        }});
                    }}
                    </script>
                    <button onclick="copyToClipboard()" style="
                        width: 100%;
                        background-color: #10B981;
                        color: white;
                        border: none;
                        padding: 10px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-weight: bold;
                    ">📋 Copy Strategy to Clipboard</button>
                    """
                    st.components.v1.html(copy_code, height=60)

                except Exception as ai_err:
                    st.error(f"AI Error: {str(ai_err)}")
            else:
                st.error(f"Error: {name_found}")

st.divider()
st.caption("ViralFinder AI • Classic Minimal Design")
