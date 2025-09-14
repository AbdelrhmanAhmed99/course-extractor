import streamlit as st
import json
import time
from test8 import extract_course_details
import os
from urllib.parse import urlparse

try:
    from firecrawl.firecrawl import FirecrawlApp as FirecrawlClient
except ImportError:
    from firecrawl import Firecrawl as FirecrawlClient

# -----------------------------
# Streamlit Setup
# -----------------------------
st.set_page_config(
    page_title="BoldStep.AI Course Extractor", 
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .course-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
    }
    
    .course-title {
        color: #2c3e50;
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .course-detail {
        background: rgba(255,255,255,0.8);
        padding: 8px 12px;
        border-radius: 8px;
        margin: 5px 0;
        font-size: 0.9rem;
    }
    
    .course-detail strong {
        color: #34495e;
    }
    
    .url-input-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #ddd;
    }
    
    .extraction-status {
        background: #e8f4fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        margin: 10px 0;
    }
    
</style>
""", unsafe_allow_html=True)

# -----------------------------
# BoldStep.AI Logo
# -----------------------------
def create_logo():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
                <div style="display: flex; gap: 5px;">
                    <div style="width: 20px; height: 20px; background: white; transform: rotate(45deg); 
                                box-shadow: 2px 2px 4px rgba(0,0,0,0.3);"></div>
                    <div style="width: 20px; height: 20px; background: white; transform: rotate(45deg); 
                                box-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin-top: 8px;"></div>
                </div>
                <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: bold; 
                           text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    BoldStep<span style="color: #ffd700; font-size: 2rem;">.AI</span>
                </h1>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def validate_url(url):
    """Validate if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def create_course_card(course, index):
    """Create a beautiful, detailed course card display"""
    course_json = json.dumps(course, indent=2, ensure_ascii=False)

    # Card container
    st.markdown(f"""
    <div class="course-card">
        <div class="course-title">🎓 {course.get('course_name', 'Unknown Course')}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Display all available course information
        if course.get('level'):
            st.markdown(f"**🎯 Level:** {course['level']}")
        if course.get('duration'):
            st.markdown(f"**⏰ Duration:** {course['duration']}")
        if course.get('fees'):
            st.markdown(f"**💰 Fees:** {course['fees']}")
        if course.get('intake_date'):
            st.markdown(f"**📅 Intake Date:** {course['intake_date']}")
        if course.get('requirements'):
            st.markdown(f"**📋 Requirements:** {course['requirements']}")
        if course.get('source_url'):
            st.markdown(f"**🔗 Source:** [View Original Page]({course['source_url']})")

        # Description inside expander
        if course.get('description'):
            with st.expander("📖 Course Description", expanded=False):
                st.markdown(course['description'])

    with col2:
        # Buttons: View Original & Download JSON
        if course.get('source_url'):
            st.link_button("🔗 View Original", course['source_url'], use_container_width=True)


    # Show raw JSON in an expander for debugging
    with st.expander(f"🛠️ Raw Data - {course.get('course_name', 'Course')}"):
        st.json(course)

# Initialize session state
if 'courses_data' not in st.session_state:
    st.session_state.courses_data = []

create_logo()

st.markdown("---")

# -----------------------------
# Main App
# -----------------------------
st.title("🎓 Course Extractor")
st.markdown("Extract detailed course information from university websites")

# Load API key
# Try to get API key from Streamlit secrets first, then environment variables
API_KEY = None
try:
    API_KEY = st.secrets.get("FIRECRAWL_API_KEY")
except:
    pass

if not API_KEY:
    API_KEY = os.getenv("FIRECRAWL_API_KEY")

if not API_KEY:
    st.error("❌ FIRECRAWL_API_KEY not found!")
    st.markdown("""
    **Please set your Firecrawl API key in one of these ways:**
    
    1. **Using Streamlit Secrets (Recommended):**
       - Edit `.streamlit/secrets.toml` file
       - Add: `FIRECRAWL_API_KEY = "your_api_key_here"`
    
    2. **Using Environment Variable:**
       - Set: `FIRECRAWL_API_KEY=your_api_key_here`
    
    **Get your API key from:** https://firecrawl.dev/
    """)
    st.stop()

fc = FirecrawlClient(api_key=API_KEY)

# -----------------------------
# URL Input Section
# -----------------------------
st.markdown("""
<div class="url-input-container">
    <h3 style="color: white; margin-bottom: 10px;">🔗 Enter Course URLs</h3>
    <p style="color: rgba(255,255,255,0.8); margin-bottom: 0;">
        Add one URL per line. We'll extract course details from each university page.
    </p>
</div>
""", unsafe_allow_html=True)

# URL input
url_input = st.text_area(
    "Course URLs (one per line):",
    height=150,
    placeholder="https://www.university.edu/courses/computer-science\nhttps://www.university.edu/courses/business-studies\n...",
    help="Enter university course page URLs, one per line"
)


# -----------------------------
# Extract Button (Always Visible)
# -----------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Extract Course Details", type="primary", use_container_width=True):
        if not url_input.strip():
            st.error("❌ Please enter URLs first")
            st.stop()
        
        urls = [url.strip() for url in url_input.strip().split('\n') if url.strip()]
        
        # Validate URLs
        valid_urls = []
        invalid_urls = []
        
        for url in urls:
            if validate_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        
        if invalid_urls:
            st.warning(f"⚠️ Found {len(invalid_urls)} invalid URLs:")
            for invalid_url in invalid_urls:
                st.write(f"❌ {invalid_url}")
        
        if not valid_urls:
            st.error("❌ No valid URLs found")
            st.stop()
        
        st.success(f"✅ Found {len(valid_urls)} valid URLs")
        
        # Create progress tracking
        progress_container = st.container()
        results_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Initialize results
        results = []
        seen = set()
        
        # Real-time results display
        with results_container:
            st.markdown("---")
            st.subheader("🔄 Live Results")
            results_placeholder = st.empty()
        
        # Process each course with real-time updates
        processed_count = 0
        for log, course in extract_course_details(fc, valid_urls):
            if course:  # Only count actual course extractions
                processed_count += 1
                # Update progress
                progress = processed_count / len(valid_urls)
                progress_bar.progress(progress)
                
                key = course.get("course_name", "").lower().strip()
                if key and key not in seen:
                    seen.add(key)
                    results.append(course)
                    
                    # Show the new course card immediately
                    with results_placeholder.container():
                        st.write(f"**✅ {len(results)} course(s) extracted so far:**")
                        
                        # Display all courses found so far (most recent first)
                        for idx, result_course in enumerate(reversed(results)):
                            create_course_card(result_course, len(results) - 1 - idx)
            
            if log:
                status_text.markdown(f"""
                <div class="extraction-status">
                    <strong>Processing ({processed_count}/{len(valid_urls)}):</strong> {log}
                </div>
                """, unsafe_allow_html=True)
        
        # Final completion message
        status_text.success(f"🎉 Extraction completed! Found {len(results)} unique courses.")
        
        # Store results in session state
        if results:
            st.session_state.courses_data = results
            

# -----------------------------
# Clear Results Button
# -----------------------------
if st.session_state.courses_data:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Previous Results", use_container_width=True):
            st.session_state.courses_data = []
            st.rerun()

# -----------------------------
# Results Display
# -----------------------------
if st.session_state.courses_data:
    results = st.session_state.courses_data
    
    
    # Clear results button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.courses_data = []
            st.rerun()
    
    st.markdown("---")
    
    # Display course cards
    st.subheader("📚 Extracted Courses")
    
    # Display all courses
    for i, course in enumerate(results):
        create_course_card(course, i)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p><strong>🚀 Powered by BoldStep.AI</strong></p>
    <p>Advanced Course Data Extraction Tool | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)