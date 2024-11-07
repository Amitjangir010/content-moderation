import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path
import io
import os
import time

# Add project root to Python path
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

# Now import our modules
from src.models.text_classifier import TextModerator
from src.models.image_classifier import ImageModerator
from src.database.db import SessionLocal, ModerationLog

# Initialize models and trackers
text_mod = TextModerator()
image_mod = ImageModerator()

st.set_page_config(
    page_title="Content Moderation System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stButton>button { 
        width: auto;
        padding: 0.5rem 2rem;
    }
    .stTextArea>div>div>textarea {
        height: 150px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar with more info
with st.sidebar:
    st.title("🛡️ Content Moderation")
    st.markdown("### Navigation")
    page = st.radio(
        "Select Page",
        ["Content Moderation", "Analytics Dashboard"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### System Status")
    st.success("🟢 Models Loaded")
    st.info("📊 Analytics Ready")
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    try:
        db = SessionLocal()
        total = db.query(ModerationLog).count()
        st.metric("Total Processed", f"{total:,}")
        db.close()
    except:
        st.metric("Total Processed", "0")

if page == "Content Moderation":
    st.title("Content Moderation System")
    st.markdown("### Real-time content moderation for text and images")
    
    tab1, tab2 = st.tabs(["📝 Text Analysis", "🖼️ Image Analysis"])
    
    with tab1:
        col1, col2 = st.columns([2,1])
        with col1:
            text_input = st.text_area("Enter text to analyze:", height=100)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if st.button("Analyze Text", type="primary"):
                if not text_input:
                    st.warning("Please enter some text")
                    st.stop()
                    
                with st.spinner("Analyzing..."):
                    try:
                        result = text_mod.check_content(text_input)
                        
                        # Log to database
                        db = SessionLocal()
                        log_entry = ModerationLog(
                            content_type="text",
                            status=result["status"],
                            confidence=result["confidence"]
                        )
                        db.add(log_entry)
                        db.commit()
                        db.close()
                        
                        # Show results in a nice box
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        with col1:
                            emoji = "🚫" if result["status"] == "toxic" else "✅"
                            st.markdown(f"### Status: {emoji} {result['status'].title()}")
                        with col2:
                            st.markdown(f"### Confidence: {result['confidence']:.2%}")
                        st.progress(result["confidence"])
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    with tab2:
        st.markdown("### Upload an image for content moderation")
        col1, col2 = st.columns([2,1])
        with col1:
            uploaded_file = st.file_uploader(
                "Choose image file:",
                type=["png", "jpg", "jpeg"],
                help="Supported formats: PNG, JPG, JPEG"
            )
            if uploaded_file:
                st.image(uploaded_file, width=350)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing
            if uploaded_file and st.button("Analyze Image", type="primary"):
                with st.spinner("Processing image..."):
                    try:
                        result = image_mod.check_image(uploaded_file.getvalue())
                        
                        db = SessionLocal()
                        log_entry = ModerationLog(
                            content_type="image",
                            status=result["status"],
                            confidence=result["confidence"]
                        )
                        db.add(log_entry)
                        db.commit()
                        db.close()
                        
                        # Show results
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        with col1:
                            emoji = "🚫" if result["status"] == "unsafe" else "✅"
                            st.markdown(f"### Status: {emoji} {result['status'].title()}")
                        with col2:
                            st.markdown(f"### Confidence: {result['confidence']:.2%}")
                        st.progress(result["confidence"])
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

else:  # Analytics Dashboard
    st.title("Analytics Dashboard")
    
    try:
        db = SessionLocal()
        logs = pd.read_sql_query("SELECT * FROM moderation_logs", db.bind)
        logs['created_at'] = pd.to_datetime(logs['created_at'])
        
        # Metrics in a nice box
        st.markdown("### Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Requests", f"{len(logs):,}")
        with col2:
            avg_conf = logs['confidence'].mean() * 100
            st.metric("Avg Confidence", f"{avg_conf:.1f}%")
        with col3:
            toxic = (logs['status'].isin(['toxic', 'unsafe'])).mean() * 100
            st.metric("Harmful Content", f"{toxic:.1f}%")
        with col4:
            recent = len(logs[logs['created_at'] > datetime.now() - timedelta(hours=1)])
            st.metric("Last Hour", f"{recent:,}")
        
        # Charts in tabs
        tab1, tab2 = st.tabs(["📊 Distribution", "📈 Timeline"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(logs, names='status', title='Content Status')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.histogram(logs, x='confidence', color='status',
                                 title='Confidence Distribution',
                                 barmode='overlay')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown("### Activity Timeline")
            fig = px.line(
                logs.set_index('created_at').resample('1H').size().reset_index(),
                x='created_at', 
                y=0,
                title='Requests per Hour'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.markdown("### Recent Activity")
        recent_logs = logs.sort_values('created_at', ascending=False).head(10)
        
        # Convert confidence to percentage before display
        display_logs = recent_logs.copy()
        display_logs['confidence'] = display_logs['confidence'].apply(lambda x: f"{x*100:.1f}%")
        
        st.dataframe(
            display_logs[['content_type', 'status', 'confidence', 'created_at']],
            use_container_width=True
        )
        
        # Refresh button only in analytics
        col1, col2, col3 = st.columns([3,1,3])
        with col2:
            if st.button("🔄 Refresh Data", type="secondary"):
                st.rerun()
        
        # Add a simple CSV export with better formatting
        st.markdown("### Export Data")

        # Prepare data for export
        export_logs = logs.copy()
        export_logs['confidence'] = export_logs['confidence'].apply(lambda x: f"{x*100:.1f}%")
        export_logs['created_at'] = export_logs['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Add summary data
        summary_data = pd.DataFrame([
            ["Total Requests", len(logs)],
            ["Average Confidence", f"{logs['confidence'].mean()*100:.1f}%"],
            ["Toxic Content", f"{(logs['status'].isin(['Toxic Text', 'NSFW Image'])).mean()*100:.1f}%"],
            ["Safe Content", f"{(logs['status'].isin(['Safe Text', 'Safe Image'])).mean()*100:.1f}%"]
        ], columns=['Metric', 'Value'])

        # Combine data
        export_data = pd.concat([
            pd.DataFrame([["=== Summary ==="]], columns=['Summary']),
            summary_data,
            pd.DataFrame([["=== Detailed Logs ==="]], columns=['Details']),
            export_logs
        ])

        # Create CSV
        csv = export_data.to_csv(index=False)

        # Download button
        st.download_button(
            label="📥 Download Complete Report (CSV)",
            data=csv,
            file_name=f"content_moderation_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            help="Download complete moderation history with summary statistics"
        )

        # Add a danger zone section
        st.markdown("---")
        st.markdown("### ⚠️ Danger Zone")

        # Create a small container in the corner for reset button
        with st.container():
            col1, col2, col3 = st.columns([6,2,1])
            with col3:
                # In the reset button section, change to:
                if st.button("🗑️ Reset", type="secondary", help="Delete all logs and analytics"):
                    try:
                        # Reset database only
                        db = SessionLocal()
                        db.query(ModerationLog).delete()
                        db.commit()
                        db.close()
                        
                        st.success("All data reset successfully!")
                        time.sleep(1)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error resetting data: {str(e)}")
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")
    finally:
        db.close()