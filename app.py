import streamlit as st
from query_data import query_rag
from populate_database import load_documents, split_documents, add_to_chroma, clear_database
import os

st.set_page_config(page_title="Document Q&A Assistant", page_icon="📚")

def main():
    st.title("📚 Document Q&A Assistant")
    
    # Sidebar for PDF upload and database management
    with st.sidebar:
        st.header("📁 Document Management")
        st.markdown("""
        ### Instructions
        1. Upload your PDF documents
        2. Click 'Process Documents' to analyze them
        3. Ask questions about your documents in the chat
        
        **Supported file types:** PDF
        """)
        
        # File uploader
        uploaded_files = st.file_uploader("Upload PDF files", type=['pdf'], accept_multiple_files=True)
        
        # Only show buttons when files are uploaded
        if uploaded_files:
            # Create two columns for the buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Process Documents", type="primary"):
                    if not os.path.exists("data"):
                        os.makedirs("data")
                    
                    with st.spinner("Saving documents..."):
                        for file in uploaded_files:
                            with open(os.path.join("data", file.name), "wb") as f:
                                f.write(file.getvalue())
                    
                    with st.spinner("Analyzing documents..."):
                        documents = load_documents()
                        chunks = split_documents(documents)
                        add_to_chroma(chunks)
                    st.success("✅ Documents processed successfully!")
            
            with col2:
                if st.button("Reset Database", type="secondary", help="Removes all documents and clears the database"):
                    try:
                        with st.spinner("Clearing database and documents..."):
                            success = clear_database()
                            if success:
                                st.success("Database and documents cleared!")
                                st.session_state.messages = []
                                st.experimental_rerun()  # Using experimental_rerun() for more reliable reload
                            else:
                                st.error("Failed to clear database. Please try restarting the application.")
                    except Exception as e:
                        st.error(f"Error clearing database: {e}")
                        st.info("If the error persists, please restart the application")

    # Main chat interface
    st.header("💬 Ask Questions About Your Documents")
    
    # Display current documents
    if os.path.exists("data"):
        files = [f for f in os.listdir("data") if f.endswith('.pdf')]
        if files:
            st.markdown("#### 📑 Currently loaded documents:")
            for file in files:
                st.markdown(f"- {file}")
        else:
            st.info("No documents loaded. Please upload PDFs using the sidebar.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                response = query_rag(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()