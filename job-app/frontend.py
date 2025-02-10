import streamlit as st
import requests
import json

st.set_page_config(page_title="Job Application AI", layout="wide")

# 🎨 Title & Instructions
st.title("🚀 AI-Powered Job Application Assistant")
st.write(
    "Upload your resume, enter your GitHub URL, and a short bio. "
    "This tool will tailor your resume and generate interview questions."
)

# 📄 File Upload & Input Fields
uploaded_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])
github_url = st.text_input("🔗 GitHub URL")
personal_writeup = st.text_area("📝 Short Bio")
job_posting_url = st.text_input("💼 Job Posting URL")

# 🚀 Submit Button
if st.button("📤 Submit for Processing"):
    if uploaded_file and github_url and personal_writeup and job_posting_url:
        files = {"file": uploaded_file.getvalue()}
        data = {
            "github_url": github_url,
            "personal_writeup": personal_writeup,
            "job_posting_url": job_posting_url,
        }
        
        with st.spinner("⏳ Processing your job application..."):
            response = requests.post("http://127.0.0.1:8000/process_application/", files=files, data=data)

        if response.status_code == 200:
            st.success("✅ Processing complete! Your results are below.")

            # 📑 Display Results in Expandable Sections
            result = response.json()

            st.markdown("## 📌 **Tailored Resume & Interview Prep Results**")

            # 🎯 Extracting Key Sections
            if "result" in result:
                result_data = result["result"]

                # 📌 Job Analysis Results
                with st.expander("📑 **Job Posting Analysis**"):
                    st.write("🔍 **Extracted Job Requirements**")
                    st.json(result_data.get("job_requirements", "No data available."))

                # 👤 Candidate Profile
                with st.expander("👤 **Candidate Profile Summary**"):
                    st.write("📝 **Profile Based on Resume & GitHub:**")
                    st.json(result_data.get("profile_summary", "No data available."))

                # 📄 Tailored Resume
                with st.expander("📄 **Optimized Resume**"):
                    st.write("🎯 **Suggested Resume Edits:**")
                    st.text(result_data.get("optimized_resume", "No data available."))

                # 🎤 Interview Questions
                with st.expander("🎤 **Interview Preparation**"):
                    st.write("🗣 **Key Interview Questions & Talking Points:**")
                    st.text(result_data.get("interview_questions", "No data available."))

            else:
                st.error("⚠️ Unexpected response format from the server.")

        else:
            st.error("❌ Error processing request. Please try again.")

    else:
        st.error("⚠️ Please fill out all fields before submitting!")




# import streamlit as st
# import requests

# st.title("AI-Powered Job Application Assistant")
# st.write("Upload your resume, enter your GitHub URL, and a short bio.")

# # Input fields
# uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
# github_url = st.text_input("GitHub URL")
# personal_writeup = st.text_area("Short Bio")
# job_posting_url = st.text_input("Job Posting URL")

# if st.button("Submit"):
#     if uploaded_file and github_url and personal_writeup and job_posting_url:
#         files = {"file": uploaded_file.getvalue()}
#         data = {"github_url": github_url, "personal_writeup": personal_writeup, "job_posting_url": job_posting_url}
#         response = requests.post("http://127.0.0.1:8000/process_application/", files=files, data=data)

#         if response.status_code == 200:
#             st.success("Processing complete!")
#             st.json(response.json())
#         else:
#             st.error("Error processing request.")
#     else:
#         st.error("Please fill out all fields!")
