import streamlit as st
import requests

def get_citation(citations, citation):
    for key, value in citations.items():
        if value == citation:
            return key

# Streamlit app title
st.title("Quill Highlight and Citation")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Quill editor component
text_input = st.text_area("Enter text here:", height=200, key="text_input")

# Initialize count and citations in session state
if "count" not in st.session_state:
    st.session_state.count = 0

if "citations" not in st.session_state:
    st.session_state.citations = {}

# Get citation button
if st.button("Get Citation"):
    # Call backend function and get citation
    backend_url = "http://127.0.0.1:5000/"  # Replace with the actual URL of your backend
    response = requests.post(backend_url, json={"text": text_input})
    
    if response.status_code == 200:
        citation = response.json().get("citation", "")
         
        if (st.session_state.citations == {}) or (citation not in st.session_state.citations.values()):
            st.session_state.count += 1
            st.session_state.citations[f'{st.session_state.count}'] = citation
            st.write(f"{text_input} [{st.session_state.count}]")
            
        else: 
            k = get_citation(st.session_state.citations, citation)
            st.write(f"{text_input} [{k}]")
        
        st.session_state.messages.append({"role": "user", "content": f"{text_input} [{st.session_state.count}]"})
        
        st.write("Bibliography")
        for key, value in st.session_state.citations.items():
            text = f'{key}. {value}'
            st.write(f"\t\t{text}.")
            
    elif response.status_code == 404:
        st.session_state.messages.append({"role": "user", "content": f"{text_input} [Paper Not Found."})
        st.write("Paper Not Found.")
        
        st.write("Bibliography")
        for key, value in st.session_state.citations.items():
            text = f'{key}. {value}'
            st.write(f"\t\t{text}.")
               
    else:
        st.error("Error fetching citation from the backend. Please try again.")
