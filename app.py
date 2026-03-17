import streamlit as st
import yt_dlp
import pandas as pd
from groq import Groq
import time
import plotly.express as px
from datetime import datetime

# 1. Page Config
st.set_page_config(
    page_title="ViralVision AI - YouTube Topic Analyzer", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Professional Modern CSS with Animations
st.html("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0B0F1C 0%, #1A1F2F 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide default elements */
    header {display: none;}
    footer {display: none;}
    #MainMenu {display: none;}
    
    /* Custom Container */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Animated Gradient Text */
    .gradient-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        animation: fadeInUp 0.8s ease;
    }
    
    .gradient-subtitle {
        font-size: 1.1rem;
        color: #A0AEC0;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease;
    }
    
    /* Card Styles */
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    /* Input Field */
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 1rem !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667EEA !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Button Styles */
    .stButton>button {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        text-transform: none !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10, 15, 30, 0.95) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-content {
        padding: 2rem 1rem;
    }
    
    /* Metrics */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #A0AEC0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Table */
    .stTable {
        background: transparent !important;
    }
    
    .stTable table {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stTable th {
        background: rgba(102, 126, 234, 0.2) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    .stTable td {
        color: #E2E8F0 !important;
        padding: 1rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Text Area */
    .stTextArea>div>div>textarea {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: white !important;
        font-family: 'Inter', monospace !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%) !important;
    }
    
    /* Success/Error/Warning Messages */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 2rem 0;
    }
    
    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: rgba(102, 126, 234, 0.2);
        border-radius: 20px;
        font-size: 0.85rem;
        color: #A0AEC0;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
</style>
""")

# 3. Header Section with Animation
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.html("""
    <div style='text-align: center; margin: 2rem 0;'>
        <div class='gradient-title'>ViralVision AI</div>
        <div class='gradient-subtitle'>Uncover Viral Topics • Analyze Competitors • Generate Winning Ideas</div>
    </div>
    """)

# 4. Sidebar with Enhanced UI
with st.sidebar:
    st.html("""
    <div class='sidebar-content'>
        <div style='text-align: center; margin-bottom: 2rem;'>
            <span class='badge'>⚡ BETA v2.0</span>
        </div>
    """)
    
    st.markdown("### 🛠️ Configuration")
    
    groq_key = st.secrets.get("GROQ_API_KEY", "")
    
    if not groq_key:
        groq_key = st.text_input(
            "🔑 Groq API Key", 
            type="password",
            placeholder="Enter your API key",
            help="Get your API key from console.groq.com"
        )
    
    # Modern slider
    num_vids = st.slider(
        "📊 Videos to Analyze", 
        min_value=5, 
        max_value=50, 
        value=20,
        help="More videos = Better insights, but slower analysis"
    )
    
    # Additional options
    st.markdown("### 🎯 Analysis Options")
    
    niche = st.selectbox(
        "Content Niche",
        ["Business", "Technology", "Psychology", "History", "Entertainment", "Education"],
        help="Select your content category for better recommendations"
    )
    
    include_comments = st.checkbox("💬 Include sentiment analysis", value=False, disabled=True)
    
    st.html("""
    <hr>
    <div style='text-align: center; color: #718096; font-size: 0.9rem;'>
        Made with ❤️ by ViralVision Team
    </div>
    </div>
    """)

# 5. Main Content Area
col1, col2 = st.columns([3, 1])

with col1:
    channel_input = st.text_input(
        "",  # Empty label for cleaner look
        placeholder="Enter YouTube channel handle (e.g., @MrBeast)",
        key="channel_input"
    )

with col2:
    analyze_button = st.button("🚀 Generate Viral Blueprint", use_container_width=True)

# 6. Feature Highlights
if 'data' not in st.session_state:
    st.html("""
    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin: 2rem 0;'>
        <div class='card' style='text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 1rem;'>🎯</div>
            <h3 style='color: white; margin-bottom: 0.5rem;'>Competitor Analysis</h3>
            <p style='color: #A0AEC0; font-size: 0.9rem;'>Analyze top-performing videos from any channel</p>
        </div>
        <div class='card' style='text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 1rem;'>🧠</div>
            <h3 style='color: white; margin-bottom: 0.5rem;'>AI-Powered Insights</h3>
            <p style='color: #A0AEC0; font-size: 0.9rem;'>Get viral hooks and title suggestions</p>
        </div>
        <div class='card' style='text-align: center;'>
            <div style='font-size: 2rem; margin-bottom: 1rem;'>📈</div>
            <h3 style='color: white; margin-bottom: 0.5rem;'>Trend Detection</h3>
            <p style='color: #A0AEC0; font-size: 0.9rem;'>Identify patterns in viral content</p>
        </div>
    </div>
    """)

# 7. Execution Logic
def get_channel_data(search_query, num_vids):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch1:{search_query} channel", download=False)
            if not search_results or not search_results.get('entries'):
                return None, "Channel not found."
            
            first = search_results['entries'][0]
            url = first.get('channel_url') or first.get('url')
            name = first.get('uploader', 'Channel')
            
            with st.spinner(f"📡 Fetching videos from {name}..."):
                meta = ydl.extract_info(f"{url}/videos", download=False)
                vids = meta.get('entries', [])[:num_vids]
                
                data = []
                for v in vids:
                    if v.get('title'):
                        data.append({
                            "Title": v['title'],
                            "Views": v.get('view_count', 0),
                            "Likes": v.get('like_count', 0),
                            "Comments": v.get('comment_count', 0)
                        })
                
                return data, name
    except Exception as e:
        return None, str(e)

if analyze_button:
    if not groq_key:
        st.error("🔑 Please enter your Groq API key in the sidebar")
    elif not channel_input:
        st.warning("📝 Please enter a YouTube channel handle")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Phase 1: Data Collection
        status_text.text("Phase 1/3: Collecting channel data...")
        progress_bar.progress(25)
        
        data, name = get_channel_data(channel_input, num_vids)
        
        if data:
            # Phase 2: Data Analysis
            status_text.text("Phase 2/3: Analyzing video performance...")
            progress_bar.progress(50)
            time.sleep(1)  # Smooth transition
            
            df = pd.DataFrame(data)
            avg_views = df['Views'].mean()
            outliers = df[df['Views'] > (avg_views * 1.2)].sort_values(by='Views', ascending=False)
            
            # Display Results in Columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.html(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{len(data)}</div>
                    <div class='metric-label'>Total Videos Analyzed</div>
                </div>
                """)
            
            with col2:
                st.html(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{len(outliers)}</div>
                    <div class='metric-label'>Viral Candidates</div>
                </div>
                """)
            
            with col3:
                st.html(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{avg_views:,.0f}</div>
                    <div class='metric-label'>Average Views</div>
                </div>
                """)
            
            # Channel Header
            st.html(f"""
            <div style='margin: 2rem 0;'>
                <h2 style='color: white; font-size: 1.8rem;'>{name} Analysis</h2>
                <p style='color: #A0AEC0;'>Top performing videos identified</p>
            </div>
            """)
            
            # Display Top Videos
            if not outliers.empty:
                st.subheader("🔥 Top Performing Videos")
                st.table(outliers[['Title', 'Views']].head(10))
                
                # Phase 3: AI Analysis
                status_text.text("Phase 3/3: Generating AI insights...")
                progress_bar.progress(75)
                
                try:
                    client = Groq(api_key=groq_key)
                    titles_list = ", ".join(outliers['Title'].tolist()[:5])
                    
                    prompt = f"""As a YouTube content strategist, analyze these viral titles in the {niche} niche:
                    {titles_list}
                    
                    Provide:
                    1. 🎣 Common Hook Patterns (list 3 patterns found)
                    2. 💡 5 Viral Title Suggestions for {niche} content
                    3. 📝 3 Opening Hook Templates (30 words each)
                    4. 🔥 Trending Topics in this space
                    
                    Format with emojis and clear sections. Keep it actionable.
                    """
                    
                    with st.spinner("🤖 AI is generating insights..."):
                        chat = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.1-8b-instant",
                            temperature=0.7,
                            max_tokens=1000
                        )
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    
                    result = chat.choices[0].message.content
                    
                    # Display AI Results in Card
                    st.html("""
                    <hr>
                    <div style='margin: 2rem 0;'>
                        <h2 style='color: white; font-size: 1.8rem;'>🧠 AI Strategy Insights</h2>
                    </div>
                    """)
                    
                    with st.container():
                        st.markdown(result)
                        
                        # Export buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📋 Copy to Clipboard", use_container_width=True):
                                st.write("Copied! (Clipboard functionality requires additional setup)")
                        
                        with col2:
                            csv = outliers[['Title', 'Views']].to_csv(index=False)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv,
                                file_name=f"viral_{channel_input.replace('@', '')}_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    
                except Exception as e:
                    st.error(f"AI Error: {e}")
            else:
                st.info("No viral candidates found in this dataset")
        else:
            st.error(f"Error: {name}")
        
        # Clear progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()

# Footer
st.html("""
<hr>
<div style='text-align: center; padding: 2rem;'>
    <p style='color: #718096; font-size: 0.9rem;'>
        ViralVision AI • Advanced YouTube Topic Analysis • Powered by Groq AI
    </p>
</div>
""")
