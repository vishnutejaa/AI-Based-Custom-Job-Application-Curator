from fastapi import FastAPI, UploadFile, Form
import os
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool, ScrapeWebsiteTool, PDFSearchTool, SerperDevTool
import fitz  # PyMuPDF

app = FastAPI()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process_application/")
async def process_application(
    file: UploadFile,
    github_url: str = Form(...),
    personal_writeup: str = Form(...),
    job_posting_url: str = Form(...)
):
    resume_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the uploaded file
    with open(resume_path, "wb") as f:
        f.write(await file.read())

    # Initialize tools
    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()
    read_resume = FileReadTool(file_path=resume_path)
    # Ensure file is properly opened in binary mode
    def extract_text_from_pdf(pdf_path):
        """ Extracts text from a PDF file safely """
        try:
            doc = fitz.open(pdf_path)
            text = "\n".join(page.get_text("text") for page in doc if page.get_text("text"))
            return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    # Extract text before passing to PDFSearchTool
    pdf_text = extract_text_from_pdf(resume_path)

    # Use extracted text instead of the file path
    semantic_search_resume = PDFSearchTool(pdf=pdf_text)
    # Define agents
    # Define agents with backstory included
    researcher = Agent(
        role="Job Researcher",
        goal="Analyze job postings and extract key skills, qualifications, and responsibilities.",
        tools=[scrape_tool, search_tool],
        verbose=True,
        backstory="You are an expert in job market analysis. Your role is to extract key information from job postings, helping candidates understand the required qualifications and skills."
    )

    profiler = Agent(
        role="Personal Profiler",
        goal="Analyze the candidate’s resume and GitHub profile to identify strengths and skills.",
        tools=[read_resume, semantic_search_resume],
        verbose=True,
        backstory="You specialize in analyzing resumes and professional profiles to highlight key strengths, skills, and experiences that align with job requirements."
    )

    resume_strategist = Agent(
        role="Resume Strategist",
        goal="Optimize the candidate’s resume to align with the job posting requirements.",
        tools=[read_resume, semantic_search_resume],
        verbose=True,
        backstory="You are an expert in resume optimization. Your task is to refine resumes, emphasizing relevant skills and experience to increase the candidate's chances of getting hired."
    )

    interview_preparer = Agent(
        role="Interview Preparer",
        goal="Generate interview questions based on the tailored resume and job requirements.",
        tools=[read_resume, semantic_search_resume],
        verbose=True,
        backstory="Your expertise lies in interview preparation. You create relevant interview questions and talking points to help candidates succeed in job interviews."
    )

    cv_writer = Agent(
        role="CV Writer",
        goal=(
            "Analyze job postings to extract key skills, qualifications, and responsibilities, "
            "helping candidates align their CVs with job requirements."
        ),
        tools=[scrape_tool, search_tool],
        verbose=True,
        backstory=(
            "As an expert in job market analysis, your role is to extract essential information "
            "from job postings, enabling candidates to better understand the qualifications and "
            "skills needed for their desired roles."
        )
    )



    # Define tasks with expected_output included
    research_task = Task(
        description=f"Analyze job posting {job_posting_url} to extract key skills and qualifications.",
        expected_output="A list of required skills, experiences, and qualifications for the job.",
        agent=researcher
    )

    profile_task = Task(
        description=f"Analyze the resume & GitHub ({github_url}) to extract key strengths and skills.",
        expected_output="A structured summary of the candidate's strengths, skills, and project experience.",
        agent=profiler
    )

    resume_task = Task(
        description="Tailor the resume to match the job posting, ensuring key skills are highlighted.",
        expected_output="An optimized resume that effectively aligns with the job posting.",
        context=[research_task, profile_task],
        agent=resume_strategist
    )

    interview_task = Task(
        description="Generate interview questions based on the tailored resume and job requirements.",
        expected_output="A set of key interview questions and talking points to help the candidate prepare.",
        context=[research_task, profile_task, resume_task],
        agent=interview_preparer
    )

    write_cv = Task(
    description=(
        "Analyze the job posting at {job_posting_url} to extract key skills, qualifications, "
        "and responsibilities. Use this information to craft a compelling and personalized "
        "cover letter that highlights the candidate’s relevant experience, skills, and motivation "
        "for applying."
    ),
    expected_output=(
        "A professionally written, tailored cover letter that aligns with the job requirements, "
        "showcases the candidate’s strengths, and follows industry best practices."
    ),
    agent=cv_writer  # Ensure the agent is trained to generate well-structured cover letters
)


    # Create crew and execute tasks
    job_application_crew = Crew(agents=[researcher, profiler, resume_strategist, interview_preparer, cv_writer], tasks=[research_task, profile_task, resume_task, interview_task, write_cv], verbose=True)

    result = job_application_crew.kickoff(inputs={"job_posting_url": job_posting_url, "github_url": github_url, "personal_writeup": personal_writeup})

    return {"message": "Processing complete", "result": result}
