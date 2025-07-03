import streamlit as st
import PyPDF2
from io import BytesIO
from model import send_to_ollama

# Set page config
st.set_page_config(
    page_title="PDF LLM Processor",
    page_icon="📄",
    layout="wide"
)

st.title("📄 PDF Upload & LLM Output")
st.markdown("Upload a PDF file and view the LLM analysis below.")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 PDF Upload")

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF file to process"
    )

    # Display PDF info if uploaded
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(f"File size: {len(uploaded_file.getvalue())} bytes")

        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.getvalue()))
            num_pages = len(pdf_reader.pages)
            st.info(f"Number of pages: {num_pages}")

            full_text = ""
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                full_text += page.extract_text() + "\n"

            st.session_state.extracted_text = full_text
            st.session_state.num_pages = num_pages

            with st.expander("📖 View Extracted Text", expanded=False):
                st.text_area(
                    "PDF Content",
                    value=full_text[:2000] +
                    "..." if len(full_text) > 2000 else full_text,
                    height=300,
                    disabled=True
                )

        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")

with col2:
    st.header("🤖 LLM Output")

    if 'llm_output' not in st.session_state:
        st.session_state.llm_output = ""

    llm_output_display = st.text_area(
        "LLM Analysis/Response",
        value=st.session_state.llm_output,
        placeholder="LLM output will appear here...\n\nClick 'Process PDF' to analyze the uploaded document.",
        height=400,
        help="This box will contain the LLM's analysis of the uploaded PDF",
        disabled=True
    )

    col2a, col2b = st.columns(2)

    with st.sidebar:
        st.header("⚙️ Settings")

        model_choice = st.selectbox(
            "Select LLM Model",
            ["llama3.2",
             "qwen2.5vl:latest",
             "scb10x/llama3.1-typhoon2-8b-instruct:latest",
             "mistral:7b",
             "gemma3:27b",
             "qwen2.5vl:32b"],
            help="Choose which LLM to use for processing"
        )

        temperature = st.slider(
            "LLM Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in LLM responses"
        )

        system_role = st.text_area(
            "System Role (Optional)",
            placeholder="You are a helpful assistant that analyzes documents...",
            height=100,
            help="Optional system role to guide the LLM's behavior"
        )

        prompt_prefix = st.text_area(
            "Prompt Prefix",
            value="Extract Test case from this document:",
            height=80,
            help="Please extract the test cases from the following document"
        )

        st.markdown("---")
        st.markdown("**Note:** Ensure Ollama is running locally")

    with col2a:
        if st.button("🔄 Process PDF", type="primary", disabled=uploaded_file is None):
            if uploaded_file is not None and hasattr(st.session_state, 'extracted_text'):
                with st.spinner("Processing with LLM..."):
                    try:

                        llm_response = send_to_ollama(
                            text=st.session_state.extracted_text,
                            model=model_choice,
                            system_role=system_role if system_role.strip() else None,
                            prompt_prefix=prompt_prefix,
                            temp=temperature
                        )

                        # Store the response in session state
                        st.session_state.llm_output = llm_response

                        st.success("✅ PDF processed successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error processing with LLM: {str(e)}")
                        st.error(
                            "Make sure Ollama is running and the selected model is available.")

    with col2b:
        if st.button("🗑️ Clear Output"):
            st.session_state.llm_output = ""
            st.rerun()

# Display processing info if available
if hasattr(st.session_state, 'extracted_text') and st.session_state.llm_output:
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        st.metric("Document Pages", st.session_state.num_pages)

    with col_info2:
        word_count = len(st.session_state.extracted_text.split())
        st.metric("Word Count", f"{word_count:,}")

    with col_info3:
        char_count = len(st.session_state.extracted_text)
        st.metric("Character Count", f"{char_count:,}")
