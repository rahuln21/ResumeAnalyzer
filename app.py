import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF for PDF extraction
import os
import re

# Set up Google Gemini API Key
GOOGLE_API_KEY = "AIzaSyCOOhdVFeixN0H9AtqAmuku62igVgWgWs0"
genai.configure(api_key=GOOGLE_API_KEY)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text("text")
    return text

# Function to analyze resume against job description
def analyze_resume(resume_text, job_desc):
    prompt = f"""
    You are an experienced HR with technical expertise in roles such as Data Science, AI Engineer, Software Developer, etc.
    Your task is to review the provided resume and compare it with the job description.
    
    Resume: {resume_text}

    Job Description: {job_desc}

    Please provide a detailed evaluation:
    -  Provide a structured evaluation:
    - ✅ Match Percentage (0-100%) 
    - 📌 Key Strengths
    - ⚠ Weaknesses & Skill Gaps
    - 📈 Suggested Skills to Improve
    - 🎓 Recommended Courses
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def extract_match_percentage(text):
    match = re.search(r'(\d{1,3})%', text)
    if match:
        return min(int(match.group(1)), 100)  # Ensure it doesn't exceed 100%
    return None

# Streamlit UI
st.set_page_config(page_title="ATS Resume Analyzer", layout="wide")
st.title("📄 ATS Resume Analyzer")
st.write("Upload your resume and enter a job description to analyze your fit.")

col1,col2=st.columns([1,1])

with col1:
	uploaded_file = st.file_uploader("Upload Resume (PDF format only)", type=["pdf"])

with col2:
	job_description = st.text_area("Enter Job Description",placeholder="Paste the Job description here...")

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
analyze_button = st.button("🔍 Analyze Resume")
st.markdown("</div>", unsafe_allow_html=True)

if analyze_button and uploaded_file and job_description:
    # Extract text from uploaded file
    with st.spinner("Extracting text..."):
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            st.error("Unsupported file type!")
            resume_text = None

    if resume_text:
        # Generate analysis
        with st.spinner("Analyzing resume..."):
            analysis = analyze_resume(resume_text, job_description)
            match_percentage = extract_match_percentage(analysis)
        st.subheader("📊 Resume Analysis Report")
    if match_percentage is not None:
        st.markdown(f"###🔥 Match Score: **{match_percentage}%**")
        st.progress(match_percentage/100)
        st.markdown(analysis,unsafe_allow_html=True)
        st.download_button(
                label="📥 Download Report",
                data=analysis,
                file_name="resume_analysis.txt",
                mime="text/plain"
            )
    else:
        st.error("Error extracting text from the resume!")

# Run Streamlit app: `streamlit run app.py`
