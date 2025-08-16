from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import os
import shutil
from pathlib import Path

# Importing agents
from Modules.RecruitmentModule import create_recruitment_module, create_prescreen_agent, get_all_candidates
from Modules.HR_SupportModule import create_hr_support_module
from Modules.FeedbackModule import create_feedback_module
from Modules.LnD_Module import create_lnd_module
from Modules.OnboardingModule import create_onboarding_module
from tools import ocr_pdf


# Creating FastAPI app
app = FastAPI()

# --------------------------
# Initialize all agents once
# --------------------------
recruitment_module = create_recruitment_module()
prescreen_agent = create_prescreen_agent()
hr_support_module = create_hr_support_module()
feedback_module = create_feedback_module()
lnd_module = create_lnd_module()
onboarding_module = create_onboarding_module()

agents = {
    'recruitment_module': recruitment_module,
    'prescreen_agent': prescreen_agent,
    'hr_support_module': hr_support_module,
    'feedback_module': feedback_module,
    'lnd_module': lnd_module,
    'onboarding_module': onboarding_module,
}

# --------------------------
# Pydantic model for request
# --------------------------
class MessageRequest(BaseModel):
    text: str

# --------------------------
# Dynamic chat endpoint
# --------------------------
@app.post("/chat/{agent_name}")
def chat(agent_name: str, request: MessageRequest):
    agent = agents.get(agent_name)
    if not agent:
        return {"error": f"Agent '{agent_name}' not found."}
    print('---->', request.text)
    # Call the agent's method to process the message
    reply = agent.run(request.text)
    return {"reply": reply.content}

# --------------------------
# File upload endpoints
# --------------------------

@app.post("/chat/{agent_name}/upload")
async def chat_with_file(
    agent_name: str, 
    file: UploadFile = File(...), 
    message: str = Form(...)
):
    """Handle file uploads for specific modules"""
    
    # Validate agent exists
    agent = agents.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found.")
    
    try:
        if agent_name == "recruitment_module":
            return await handle_recruitment_file_upload(file, message, agent)
        elif agent_name == "feedback_module":
            return await handle_feedback_file_upload(file, message, agent)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"File upload not supported for '{agent_name}'"
            )
    except Exception as e:
        print(f"Error processing file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

async def handle_recruitment_file_upload(file: UploadFile, message: str, agent):
    """Handle file uploads for recruitment module (resumes)"""
    
    # Validate file type for recruitment (PDF files only)
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension != '.pdf':
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only PDF files are allowed for recruitment module."
        )
    
    # Create directories if they don't exist
    resumes_dir = Path("Resumes")
    resumes_dir.mkdir(exist_ok=True)
    
    # Save uploaded file to Resumes directory
    file_path = resumes_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print(f"Saved resume file: {file_path}")
    
    # Process PDF with OCR if it's a PDF file and get the markdown path
    markdown_path = None
    if file_extension == '.pdf':
        try:
            ocr_pdf(str(file_path))
            print(f"OCR processing completed for: {file_path}")
            # The OCR function saves the markdown file in MarkdownResumes/ directory
            markdown_filename = file_path.stem + '.md'  # Get filename without extension and add .md
            markdown_path = Path("MarkdownResumes") / markdown_filename
            print(f"Markdown file should be at: {markdown_path}")
        except Exception as e:
            print(f"OCR processing failed: {str(e)}")
            # Continue even if OCR fails
    
    # Create the message for the agent with the appropriate path
    if markdown_path and markdown_path.exists():
        # Use markdown path if OCR was successful
        agent_message = f"Resume Path: {markdown_path}, {message}" if message else f"Resume Path: {markdown_path}"
    else:
        # Fallback to original file path for non-PDF files or if OCR failed
        agent_message = f"Resume Path: {file_path}, {message}" if message else f"Resume Path: {file_path}"
    
    print('---->', agent_message)
    
    # Send to recruitment agent
    reply = agent.run(agent_message)
    
    return {
        "reply": reply.content,
        "file_processed": str(file_path),
        "markdown_path": str(markdown_path) if markdown_path else None,
        "ocr_completed": file_extension == '.pdf' and markdown_path and markdown_path.exists()
    }

async def handle_feedback_file_upload(file: UploadFile, message: str, agent):
    """Handle file uploads for feedback module (CSV files)"""
    
    # Validate file type for feedback (only CSV files)
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension != '.csv':
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only CSV files are allowed for feedback module."
        )
    
    # Create directory if it doesn't exist
    feedback_dir = Path("FeedbackResults")
    feedback_dir.mkdir(exist_ok=True)
    
    # Save uploaded file to FeedbackResults directory
    file_path = feedback_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print(f"Saved feedback file: {file_path}")
    
    # Update the agent's CSV tools to include the new file
    absolute_file_path = file_path.resolve()
    
    # Access the agent's tools and update CSV files list
    for tool in agent.tools:
        if hasattr(tool, 'csvs'):
            tool.csvs = [absolute_file_path]
            print(f"Updated CSV tools with file: {absolute_file_path}")
            break
    
    # Create the message for the agent with file path info
    agent_message = f"Please analyze the uploaded CSV file: {file.filename}. {message}" if message else f"Please analyze the uploaded CSV file: {file.filename}."
    
    print('---->', agent_message)
    
    # Send to feedback agent
    reply = agent.run(agent_message)
    
    return {
        "reply": reply.content,
        "file_processed": str(file_path)
    }

# --------------------------
# Candidates dashboard endpoint
# --------------------------

@app.get("/candidates")
def get_candidates():
    """Get all candidates from Airtable for the dashboard"""
    try:
        candidates = get_all_candidates()
        return {"candidates": candidates}
    except Exception as e:
        print(f"Error fetching candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching candidates: {str(e)}")

# --------------------------
# PreScreen Bot chat endpoint
# --------------------------

@app.post("/prescreen")
def prescreen_chat(request: MessageRequest):
    """Chat endpoint specifically for PreScreen Bot (candidate-facing)"""
    try:
        print('----> PreScreen:', request.text)
        # Use the prescreen agent
        reply = prescreen_agent.run(request.text)
        return {"reply": reply.content}
    except Exception as e:
        print(f"Error in prescreen chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing prescreen chat: {str(e)}")