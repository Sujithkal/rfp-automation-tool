import streamlit as st
import PyPDF2
import google.generativeai as genai
def clean_ui():
    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            margin-top: -80px;
        }
        </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

# Call it immediately
clean_ui()

# --- App Configuration ---
st.set_page_config(page_title="RFP Chat MVP", page_icon="📄")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# --- Helper Functions ---
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def get_gemini_response(api_key, context, question):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""You are an expert Proposal Writer. Use the context below to answer the user's question.
    CONTEXT: {context}
    QUESTION: {question}"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- Sidebar ---
with st.sidebar:
    st.header("Setup")
    
    # Try to load API Key from secrets or environment
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
            st.success("API Key loaded from secrets")
        else:
             api_key = st.text_input("Google Gemini API Key", type="password")
    except FileNotFoundError:
         api_key = st.text_input("Google Gemini API Key", type="password")

    uploaded_file = st.file_uploader("Upload RFP PDF", type=["pdf"])

    if uploaded_file and not st.session_state.pdf_text:
        with st.spinner("Extracting text..."):
            text = extract_text_from_pdf(uploaded_file)
            st.session_state.pdf_text = text
            st.success("RFP Uploaded & Processed!")
            
    if uploaded_file and st.session_state.pdf_text:
         st.info("PDF Content Loaded in Session.")

    if not api_key:
        st.warning("Please enter your Gemini API Key to chat.")

# --- Main Interface ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2910/2910795.png", width=60) # Free shield icon
with col2:
    st.markdown("# RFP Shield \n *Automated Risk Detection*")
st.write("Upload an RFP document and ask questions to get AI-assisted answers.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about the RFP..."):
    # Render user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check for prerequisites
    if not api_key:
        st.error("Missing Google Gemini API Key.")
    elif not st.session_state.pdf_text:
        st.error("Please upload a PDF document first.")
    else:
        # Generate Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_text = get_gemini_response(api_key, st.session_state.pdf_text, prompt)
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
st.divider()
st.caption("🔒 **Private Beta Mode** | Data processed via Google Gemini Enterprise API. Files are not stored permanently.")
st.caption("© 2025 Sujith Automation Services. Generated advice should be verified by a human expert.")                

