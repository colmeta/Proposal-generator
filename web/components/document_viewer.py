"""Document viewer component"""
import streamlit as st
from typing import Dict, Any, List, Optional
from web.utils.helpers import (
    format_date, format_file_size, sanitize_filename,
    show_error, show_success, show_info
)
from web.utils.api_client import get_api_client
import io


def render_document_viewer(document_id: Optional[str] = None, proposal_id: Optional[str] = None):
    """Render document viewer
    
    Args:
        document_id: Optional specific document ID to view
        proposal_id: Optional proposal ID to filter documents
    """
    st.header("📄 Document Viewer")
    
    api_client = get_api_client()
    
    # Get documents
    try:
        if document_id:
            # Get specific document
            document = api_client.get_document(document_id)
            documents = [document]
        elif proposal_id:
            # Get documents for proposal
            docs_response = api_client.list_documents(proposal_id=proposal_id)
            documents = docs_response.get('documents', [])
        else:
            # Get all documents
            docs_response = api_client.list_documents()
            documents = docs_response.get('documents', [])
    except Exception as e:
        show_error(f"Failed to load documents: {str(e)}")
        return
    
    if not documents:
        show_info("No documents found. Generate a proposal to create documents.")
        return
    
    # Document selection
    if len(documents) > 1 and not document_id:
        st.subheader("Select Document")
        doc_options = {f"{doc.get('title', 'Untitled')} - {format_date(doc.get('created_at'))}": doc.get('id') 
                      for doc in documents}
        selected_doc_name = st.selectbox("Choose a document", options=list(doc_options.keys()))
        selected_doc_id = doc_options[selected_doc_name]
        document = next((d for d in documents if d.get('id') == selected_doc_id), documents[0])
    else:
        document = documents[0]
    
    # Display document information
    render_document_info(document)
    
    # Document content
    st.divider()
    render_document_content(document, api_client)
    
    # Version history if available
    if document.get('versions') or document.get('version'):
        st.divider()
        render_version_history(document, api_client)


def render_document_info(document: Dict[str, Any]):
    """Render document information section
    
    Args:
        document: Document data dictionary
    """
    st.subheader("Document Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Title:** {document.get('title', 'Untitled')}")
        st.write(f"**Type:** {document.get('document_type', 'N/A')}")
        st.write(f"**Status:** {document.get('status', 'N/A')}")
        if document.get('proposal_id'):
            st.write(f"**Proposal ID:** `{document.get('proposal_id')}`")
    
    with col2:
        st.write(f"**Created:** {format_date(document.get('created_at'))}")
        if document.get('updated_at'):
            st.write(f"**Updated:** {format_date(document.get('updated_at'))}")
        if document.get('file_size'):
            st.write(f"**Size:** {format_file_size(document.get('file_size', 0))}")
        if document.get('version'):
            st.write(f"**Version:** {document.get('version')}")
    
    # Metadata
    if document.get('metadata'):
        with st.expander("View Metadata"):
            st.json(document.get('metadata'))


def render_document_content(document: Dict[str, Any], api_client):
    """Render document content
    
    Args:
        document: Document data dictionary
        api_client: API client instance
    """
    st.subheader("Document Content")
    
    document_id = document.get('id')
    
    # Format selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        view_format = st.radio(
            "View Format",
            options=['Preview', 'PDF', 'DOCX', 'Text'],
            horizontal=True
        )
    
    with col2:
        if st.button("🔄 Refresh Content"):
            st.rerun()
    
    with col3:
        if st.button("📋 Copy to Clipboard"):
            st.info("Copy functionality not yet implemented")
    
    # Display content based on format
    try:
        if view_format == 'Preview':
            # Try to get text preview
            if document.get('content'):
                st.text_area(
                    "Document Preview",
                    document.get('content'),
                    height=600,
                    disabled=True
                )
            elif document.get('preview'):
                st.markdown(document.get('preview'))
            else:
                show_info("Preview not available. Please download the document.")
        
        elif view_format == 'PDF':
            try:
                pdf_bytes = api_client.download_document(document_id, format='pdf')
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=sanitize_filename(f"{document.get('title', 'document')}.pdf"),
                    mime="application/pdf"
                )
                # Display PDF preview
                st.pdf(pdf_bytes)
            except Exception as e:
                show_error(f"Failed to load PDF: {str(e)}")
        
        elif view_format == 'DOCX':
            try:
                docx_bytes = api_client.download_document(document_id, format='docx')
                st.download_button(
                    label="📥 Download DOCX",
                    data=docx_bytes,
                    file_name=sanitize_filename(f"{document.get('title', 'document')}.docx"),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                show_info("DOCX files cannot be previewed in the browser. Please download to view.")
            except Exception as e:
                show_error(f"Failed to load DOCX: {str(e)}")
        
        elif view_format == 'Text':
            try:
                # Try to get text version
                if document.get('content'):
                    st.text_area(
                        "Document Text",
                        document.get('content'),
                        height=600,
                        disabled=True
                    )
                else:
                    show_info("Text version not available.")
            except Exception as e:
                show_error(f"Failed to load text: {str(e)}")
    
    except Exception as e:
        show_error(f"Failed to load document content: {str(e)}")
    
    # Download options
    st.divider()
    st.subheader("Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            pdf_bytes = api_client.download_document(document_id, format='pdf')
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=sanitize_filename(f"{document.get('title', 'document')}.pdf"),
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF: {str(e)}")
    
    with col2:
        try:
            docx_bytes = api_client.download_document(document_id, format='docx')
            st.download_button(
                label="📥 Download DOCX",
                data=docx_bytes,
                file_name=sanitize_filename(f"{document.get('title', 'document')}.docx"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"DOCX: {str(e)}")
    
    with col3:
        if st.button("🖨️ Print", use_container_width=True):
            st.info("Use your browser's print function (Ctrl+P / Cmd+P)")


def render_version_history(document: Dict[str, Any], api_client):
    """Render document version history
    
    Args:
        document: Document data dictionary
        api_client: API client instance
    """
    st.subheader("Version History")
    
    versions = document.get('versions', [])
    if not versions and document.get('version'):
        # Single version document
        versions = [document]
    
    if not versions:
        show_info("No version history available.")
        return
    
    # Sort versions by creation date (newest first)
    versions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    for i, version in enumerate(versions):
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                version_num = version.get('version', i + 1)
                st.write(f"**Version {version_num}**")
                if version.get('title'):
                    st.write(version.get('title'))
                if version.get('description'):
                    st.caption(version.get('description'))
            
            with col2:
                st.write(f"Created: {format_date(version.get('created_at'))}")
                if version.get('file_size'):
                    st.write(f"Size: {format_file_size(version.get('file_size', 0))}")
            
            with col3:
                version_id = version.get('id')
                if version_id:
                    try:
                        pdf_bytes = api_client.download_document(version_id, format='pdf')
                        st.download_button(
                            label="📥 Download",
                            data=pdf_bytes,
                            file_name=sanitize_filename(f"{version.get('title', 'document')}_v{version_num}.pdf"),
                            mime="application/pdf",
                            key=f"download_v{version_num}"
                        )
                    except Exception as e:
                        st.error(f"Download failed: {str(e)}")
            
            if i < len(versions) - 1:
                st.divider()


def render_document_comparison(document1_id: str, document2_id: str, api_client):
    """Render side-by-side document comparison
    
    Args:
        document1_id: First document ID
        document2_id: Second document ID
        api_client: API client instance
    """
    st.header("📊 Document Comparison")
    
    try:
        doc1 = api_client.get_document(document1_id)
        doc2 = api_client.get_document(document2_id)
    except Exception as e:
        show_error(f"Failed to load documents: {str(e)}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Document 1: {doc1.get('title', 'Untitled')}")
        st.write(f"Version: {doc1.get('version', 'N/A')}")
        st.write(f"Created: {format_date(doc1.get('created_at'))}")
        
        if doc1.get('content'):
            st.text_area(
                "Content",
                doc1.get('content'),
                height=400,
                disabled=True,
                key="doc1_content"
            )
    
    with col2:
        st.subheader(f"Document 2: {doc2.get('title', 'Untitled')}")
        st.write(f"Version: {doc2.get('version', 'N/A')}")
        st.write(f"Created: {format_date(doc2.get('created_at'))}")
        
        if doc2.get('content'):
            st.text_area(
                "Content",
                doc2.get('content'),
                height=400,
                disabled=True,
                key="doc2_content"
            )
    
    # Comparison actions
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            pdf_bytes = api_client.download_document(document1_id, format='pdf')
            st.download_button(
                label="📥 Download Document 1 (PDF)",
                data=pdf_bytes,
                file_name=sanitize_filename(f"{doc1.get('title', 'document1')}.pdf"),
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Download failed: {str(e)}")
    
    with col2:
        try:
            pdf_bytes = api_client.download_document(document2_id, format='pdf')
            st.download_button(
                label="📥 Download Document 2 (PDF)",
                data=pdf_bytes,
                file_name=sanitize_filename(f"{doc2.get('title', 'document2')}.pdf"),
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Download failed: {str(e)}")


