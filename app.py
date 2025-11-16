"""
Streamlit web interface for Professional Funding Proposal Generator
"""
import streamlit as st
import os
from typing import Dict, Optional
from config import FUNDER_REQUIREMENTS, DOCUMENT_TYPES
from document_analyzer import DocumentAnalyzer
from question_generator import QuestionGenerator
from document_generator import DocumentGenerator

# Page configuration
st.set_page_config(
    page_title="Professional Funding Proposal Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">📝 Professional Funding Proposal Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Win Grants from Fortune 500, Gates Foundation, World Bank, WHO & More</div>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        st.divider()
        
        # Funder selection
        st.subheader("Select Target Funder")
        funder_options = {v["name"]: k for k, v in FUNDER_REQUIREMENTS.items()}
        selected_funder_name = st.selectbox(
            "Choose your funder",
            options=list(funder_options.keys()),
            help="Select the organization you're applying to"
        )
        funder_type = funder_options[selected_funder_name]
        
        # Display funder info
        funder_info = FUNDER_REQUIREMENTS[funder_type]
        with st.expander("Funder Information"):
            st.write("**Focus Areas:**")
            for area in funder_info["focus_areas"]:
                st.write(f"- {area}")
            st.write(f"**Tone:** {funder_info['tone']}")
        
        st.divider()
        
        # Document type selection
        st.subheader("Select Document Type")
        doc_options = {v["name"]: k for k, v in DOCUMENT_TYPES.items()}
        selected_doc_name = st.selectbox(
            "Choose document type",
            options=list(doc_options.keys()),
            help="Select the type of document you need"
        )
        doc_type = doc_options[selected_doc_name]
        
        # Display document sections
        doc_info = DOCUMENT_TYPES[doc_type]
        with st.expander("Document Sections"):
            for section in doc_info["sections"]:
                st.write(f"- {section}")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📄 New Document", "🔍 Analyze Existing", "❓ Questions Only"])
    
    with tab1:
        st.header("Create New Document")
        st.write("Answer questions about your project to generate a professional proposal.")
        
        # Initialize session state
        if 'user_responses' not in st.session_state:
            st.session_state.user_responses = {}
        
        # Generate questions
        question_gen = QuestionGenerator(funder_type, doc_type)
        questions = question_gen.generate_questions()
        
        # Collect responses
        st.subheader("Project Information")
        
        for i, q in enumerate(questions):
            response = st.text_area(
                f"{i+1}. {q['category']}",
                value=st.session_state.user_responses.get(q['category'], ''),
                help=q['why'],
                height=100,
                key=f"question_{i}"
            )
            if response:
                st.session_state.user_responses[q['category']] = response
        
        # Generate button
        if st.button("🚀 Generate Document", type="primary"):
            if not os.getenv("OPENAI_API_KEY") and not api_key:
                st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
            elif not any(st.session_state.user_responses.values()):
                st.warning("⚠️ Please answer at least some questions before generating.")
            else:
                with st.spinner("Generating your professional document... This may take a minute."):
                    generator = DocumentGenerator(funder_type, doc_type)
                    generated_doc = generator.generate_document(st.session_state.user_responses)
                    
                    st.success("✅ Document generated successfully!")
                    st.text_area("Generated Document", generated_doc, height=600)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Document",
                        data=generated_doc,
                        file_name=f"{doc_type}_{funder_type}.txt",
                        mime="text/plain"
                    )
    
    with tab2:
        st.header("Analyze & Enhance Existing Document")
        st.write("Upload your existing document to identify gaps and get an enhanced version.")
        
        uploaded_file = st.file_uploader("Upload your document", type=['txt', 'docx', 'pdf'])
        
        if uploaded_file:
            # Read file content
            if uploaded_file.type == "text/plain":
                doc_text = str(uploaded_file.read(), "utf-8")
            else:
                st.warning("Currently only .txt files are supported. Please convert your document to .txt format.")
                doc_text = None
            
            if doc_text:
                # Analyze document
                if st.button("🔍 Analyze Document"):
                    analyzer = DocumentAnalyzer(funder_type, doc_type)
                    gaps = analyzer.analyze_text(doc_text)
                    report = analyzer.generate_gap_report(gaps)
                    
                    st.subheader("Gap Analysis Report")
                    st.text(report)
                    
                    # Store for enhancement
                    st.session_state.existing_doc = doc_text
                    st.session_state.gaps = gaps
                
                # Enhance document
                if 'existing_doc' in st.session_state:
                    st.divider()
                    st.subheader("Enhance Document")
                    
                    # Collect additional info for gaps
                    if st.session_state.get('gaps'):
                        critical_gaps = [g for g in st.session_state.gaps if g.severity == "critical"]
                        if critical_gaps:
                            st.write("**Please provide additional information to fill critical gaps:**")
                            additional_info = {}
                            for gap in critical_gaps[:5]:
                                additional_info[gap.section] = st.text_area(
                                    f"Information for: {gap.section}",
                                    help=gap.recommendation,
                                    key=f"gap_{gap.section}"
                                )
                            st.session_state.additional_info = additional_info
                    
                    if st.button("✨ Generate Enhanced Document", type="primary"):
                        if not os.getenv("OPENAI_API_KEY") and not api_key:
                            st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
                        else:
                            with st.spinner("Enhancing your document... This may take a minute."):
                                generator = DocumentGenerator(funder_type, doc_type)
                                
                                # Merge existing doc with additional info
                                enhanced_responses = st.session_state.get('additional_info', {})
                                
                                enhanced_doc = generator.generate_document(
                                    enhanced_responses,
                                    st.session_state.existing_doc
                                )
                                
                                # Generate change summary
                                change_summary = generator.generate_change_summary(
                                    st.session_state.existing_doc,
                                    enhanced_doc
                                )
                                
                                st.success("✅ Document enhanced successfully!")
                                
                                st.subheader("What Changed")
                                st.text(change_summary)
                                
                                st.subheader("Enhanced Document")
                                st.text_area("Enhanced Document", enhanced_doc, height=600, key="enhanced_doc")
                                
                                st.download_button(
                                    label="📥 Download Enhanced Document",
                                    data=enhanced_doc,
                                    file_name=f"enhanced_{doc_type}_{funder_type}.txt",
                                    mime="text/plain"
                                )
    
    with tab3:
        st.header("Get Questions Only")
        st.write("View all questions you'll need to answer to create a comprehensive proposal.")
        
        question_gen = QuestionGenerator(funder_type, doc_type)
        questions = question_gen.generate_questions()
        
        st.subheader(f"Questions for {selected_funder_name} - {selected_doc_name}")
        
        for i, q in enumerate(questions, 1):
            with st.expander(f"Question {i}: {q['category']}"):
                st.write(f"**Question:** {q['question']}")
                st.info(f"💡 **Why this matters:** {q['why']}")
        
        st.info("💡 **Tip:** Answer these questions thoroughly to create a winning proposal. The more detail you provide, the stronger your document will be.")


if __name__ == "__main__":
    main()

