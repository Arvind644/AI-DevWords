import streamlit as st
import os
from datetime import datetime
from utils.blog_generator import BlogGenerator
from utils.tech_tracker import TechTracker
from utils.content_processor import ContentProcessor

# Page configuration
st.set_page_config(
    page_title="Technical Blog Generator",
    page_icon="📝",
    layout="wide"
)

# Initialize components
@st.cache_resource
def init_components():
    return BlogGenerator(), TechTracker(), ContentProcessor()

blog_generator, tech_tracker, content_processor = init_components()

# Sidebar
st.sidebar.title("⚙️ Configuration")
content_type = st.sidebar.selectbox(
    "Content Type",
    ["Blog Post", "Tutorial", "Technical Guide", "Trend Report"]
)

# Main content
st.title("📝 Technical Blog Generator")
st.markdown("Generate high-quality technical content powered by Exa AI")

# Input section
col1, col2 = st.columns(2)

with col1:
    topic = st.text_input("Topic or Technology", placeholder="e.g., Docker, Python, Machine Learning")
    
with col2:
    style = st.selectbox(
        "Content Style",
        ["Technical", "Tutorial", "Overview", "Deep Dive"]
    )

# Advanced options
with st.expander("Advanced Options"):
    col3, col4, col5 = st.columns(3)
    
    with col3:
        difficulty = st.select_slider(
            "Content Difficulty",
            options=["Beginner", "Intermediate", "Advanced"],
            value="Intermediate"
        )
    
    with col4:
        include_code = st.checkbox("Include Code Examples", value=True)
    
    with col5:
        output_format = st.selectbox(
            "Output Format",
            ["markdown", "html", "json"]
        )

# Generation
if st.button("Generate Content", type="primary"):
    if not topic:
        st.error("Please enter a topic")
    else:
        with st.spinner("Generating content..."):
            try:
                # Generate content based on type
                if content_type == "Blog Post":
                    content = blog_generator.generate_blog_post(topic, style)
                elif content_type == "Tutorial":
                    content = blog_generator.generate_tutorial(topic, difficulty)
                elif content_type == "Trend Report":
                    content = tech_tracker.generate_trend_report(topic)
                else:
                    content = blog_generator.generate_blog_post(topic, style)

                # Add metadata
                content = content_processor.add_metadata(content)

                # Process content
                formatted_content = content_processor.process_content(content, output_format)

                # Display results
                st.success("Content generated successfully!")
                
                # Preview section
                st.subheader("Preview")
                if output_format == "html":
                    st.markdown(formatted_content, unsafe_allow_html=True)
                else:
                    st.markdown(formatted_content)

                # Download button
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{topic.lower().replace(' ', '_')}_{timestamp}.{output_format}"
                st.download_button(
                    label="Download Content",
                    data=formatted_content,
                    file_name=filename,
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Error generating content: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Made with ❤️ using Exa AI</p>
    </div>
    """,
    unsafe_allow_html=True
) 