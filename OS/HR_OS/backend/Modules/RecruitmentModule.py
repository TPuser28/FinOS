import os
from pyairtable import Api
from agno.team import Team
from textwrap import dedent
from agno.agent import Agent
from datetime import datetime
from dotenv import load_dotenv
from agno.models.xai import xAI
from agno.memory.v2.memory import Memory
from agno.tools.calcom import CalComTools
# from agno.models.openai import OpenAIChat
from agno.models.mistral import MistralChat
from agno.vectordb.pgvector import PgVector
from agno.embedder.mistral import MistralEmbedder
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.knowledge.markdown import MarkdownKnowledgeBase

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_CANDIDATES_TABLE_ID = os.getenv('AIRTABLE_CANDIDATES_TABLE_ID')

def get_all_candidates() -> list[dict]:
    """
    Get all records from the table

    Returns:
    - A list of dictionaries of records
    """
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_CANDIDATES_TABLE_ID)
    return table.all()

def update_candidate(record_id: str, data: dict):
    """
    Update a record in the table

    Args:
    - record_id (str): The id of the record to update
    - data (dict): A dictionary where keys are field names and values are the data to update.
    """
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_CANDIDATES_TABLE_ID)
    table.update(record_id, data)

def add_candidate(data: dict):
    """
    Add a record to the table

    Args:
    - data (dict): A dictionary where keys are field names and values are the data to add.
    """
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_CANDIDATES_TABLE_ID)
    table.create(data)

def read_resume(resume_path):
    with open(resume_path, "r") as f:
        return f.read()

def create_recruitment_module():
    # Initializing Knowledge Base
    knowledge_base = MarkdownKnowledgeBase(
        path="CompanyKnowledge/job_descriptions.md",
        vector_db=PgVector(
            table_name="hr_knowledge",
            db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
            embedder=MistralEmbedder(api_key=os.getenv('MISTRAL_API_KEY')),
        ),
    )
    knowledge_base.load(recreate=True)

    # Initializing Memory
    memory = Memory(
        model=xAI(id="grok-3-mini"),
        # model=OpenAIChat(id='gpt-4o-mini'),
        db=SqliteMemoryDb(table_name="user_memories", db_file='Database/recruitment_memory.db'),
    )

    ResumeScreenerAgent = Agent(
        name='Resume Screener Agent',
        # model=OpenAIChat(id='gpt-4o-mini'),
        model=MistralChat(id='mistral-large-latest', api_key=os.getenv('MISTRAL_API_KEY')),
        role='Screens resumes of candidates',
        description='You are a resume screener agent asked to screen candidate resumes',
        instructions=dedent('''
        You are a resume screener agent.  

        You will receive:  
        - A path to one or more candidate resumes as Markdown file paths.  
        - A job title that the candidate applied to.

        You have access to the job descriptions in your knowledge base, always use it to get the job requirements the candidate needs to have.

        For each candidate:  
        1. Pass the resume file path to the `read_resume` tool, this will return the content of the resume as markdown.
        2. Parse the resume contents and evaluate how well the candidate matches the job requirements.  
        3. Apply the current scoring mechanism (see "Scoring Mechanism" section below) to generate a score out of 100.  
        4. If multiple resumes or candidate descriptions are given, evaluate each one separately.  
        5. Generate a comparative ranking of all candidates based on their scores.  

        Key points:  
        - Always process *all* resumes/descriptions provided.  
        - Be objective and consistent in scoring.  
        - Identify missing or weak points in the candidate profile compared to the job requirements.  
        - The scoring mechanism can be updated or replaced without altering the rest of the instructions.

        IMPORTANT: 
            - If the manager chooses and decides to add a candidate, call the `add_candidate(data: dict)` tool to add the candidate to the table.
            - The fields to be passed to the `add_candidate(data: dict)` tool are:
                - Full Name
                - Email
                - Department
                - Position
            - If any issue occurs, call the `get_all_candidates` tool to get the current state and field types of the table and check if the candidate is already in the table.

        ---

        Scoring Mechanism (default):
        - **Skills Match** – 40 points: Match between required skills in JD and candidate skills. Deduct proportionally for missing skills.  
        - **Experience Match** – 30 points: Relevance of past roles, industries, and responsibilities to the JD.  
        - **Education & Certifications** – 15 points: Alignment with required or preferred education and certifications.  
        - **Achievements & Impact** – 10 points: Measurable results, leadership, awards, or significant contributions.  
        - **Formatting & Clarity** – 5 points: Resume is well-organized, easy to read, and professional.  

        Score = sum of points from all categories (0–100).
        '''),
        expected_output=dedent('''
        If one candidate is provided:  
        - Candidate Name (if available)  
        - Candidate Email (if available)  
        - Score (0–100) based on the defined scoring mechanism  
        - Category breakdown (skills, experience, education, achievements, formatting)  
        - Summary of qualifications, relevant experience, and skills  
        - Notable strengths  
        - Areas for improvement or missing skills  
        - Recommendation: "Proceed", "Maybe", or "Reject"  

        If multiple candidates are provided:  
        - Table or ordered list of candidates ranked from highest to lowest score  
        - Score for each candidate (0–100) with category breakdowns  
        - Short summary for each candidate  
        - Comparative observations (why top candidates ranked higher)  
        - Rejection recommendations for candidates below a chosen score threshold  
        '''),
        tools=[read_resume, add_candidate, get_all_candidates],
        knowledge=knowledge_base,
        # debug_mode=True,
        # enable_agentic_memory=True,
        # add_history_to_messages=True,
        # memory=memory,
    )

    InterviewSchedulerAgent = Agent(
        name='Interview Scheduler Agent',
        model=MistralChat(id='mistral-large-latest', api_key=os.getenv('MISTRAL_API_KEY')),
        role='Schedules interviews for candidates',
        description='You are an interview scheduler agent asked to scheduel interviews for candidates based on HR availability',
        instructions=dedent(f'''
        You are an interview scheduler agent helping an HR manage interviews with candidates. Today is {datetime.now()}.

        Your responsibilities include:  
        1. **Finding available time slots**: Check the HR's calendar for open slots within specified dates or ranges.  
        2. **Creating new bookings**: Schedule interviews for candidates based on provided date, time, and duration, ensuring there are no conflicts with existing bookings.  
        3. **Managing existing bookings**: View, reschedule, or cancel interviews as requested.  
        4. **Getting booking details**: Retrieve complete details of a scheduled interview, including candidate name, date, time, and meeting link/location.  

        Rules:  
        - Always verify if the requested scheduling date and time are available.  
        - If a requested date/time is unavailable, respond politely and provide alternative available slots.  
        - Confirm all actions (creation, rescheduling, or cancellation) before finalizing.  
        - Handle all dates and times using the correct time zone provided.  
        - Maintain clear, concise, and professional communication in all interactions.  
        '''),
        tools=[CalComTools(user_timezone="Africa/Casablanca", api_key=os.getenv('CAL_API_KEY'), event_type_id=30)],
        # debug_mode=True,
        # enable_agentic_memory=True,
        # add_history_to_messages=True,
        # memory=memory,
    )

    HRManagerAgent = Team(
        name='HR Manager Agent',
        model=MistralChat(id='mistral-large-latest', api_key=os.getenv('MISTRAL_API_KEY')),
        mode='coordinate',
        members=[InterviewSchedulerAgent, ResumeScreenerAgent],
        description='You are an HR Manager Agent that assists the HR department by delegating resume screening and interview scheduling tasks to specialized agents.',
        instructions=dedent('''
        You are the Team Leader in a coordinate-mode HR team.

        Members:
        1. ResumeScreenerAgent → Screens resumes, scores candidates, and ranks them according to job requirements from the knowledge base.
        2. InterviewSchedulerAgent → Manages interview bookings, including creating, rescheduling, canceling, and viewing details.

        How to decide which member to call:
        - If the request is about evaluating, scoring, comparing, or ranking candidates based on resumes, call ResumeScreenerAgent.  
        Example input:
            Resume Path: ../MarkdownResumes/ayoubankote_cv.md, Job Position: AI Engineer
        - If the request is about booking, rescheduling, canceling, or viewing interviews, call InterviewSchedulerAgent.  
        Example input:
            Create a new booking for tomorrow at 12:00 PM to 12:30 PM, for the candidate: testemail@gmail.com named Test Name
        - If the HR request involves both screening a candidate and then scheduling an interview (for example, after a “Proceed” recommendation), first call ResumeScreenerAgent, then pass the chosen candidate’s details to InterviewSchedulerAgent.

        Output rules:
        - Always present outputs cleanly and precisely, matching the expected output format of the agent that handled the task.
        - If multiple agents were called for a single HR request, merge their results into one cohesive response while keeping each part clearly labeled.
        - Never invent or alter the agents’ outputs; your role is to coordinate, not to change their content.

        Your priorities:
        1. Correctly interpret the HR request.
        2. Assign the task to the right agent(s).
        3. Ensure all relevant input details are passed exactly as required.
        4. Return the agent outputs in a clear, professional format suitable for direct HR use.
        '''),
        memory=memory,
        enable_agentic_memory=True,
        add_history_to_messages=True,
        add_member_tools_to_system_message=False,
        enable_agentic_context=True,
        share_member_interactions=True,
    )
    return HRManagerAgent

def create_prescreen_agent():
    # Initializing Knowledge Base
    knowledge_base = MarkdownKnowledgeBase(
        path="CompanyKnowledge/job_descriptions.md",
        vector_db=PgVector(
            table_name="hr_knowledge",
            db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
            embedder=MistralEmbedder(api_key=os.getenv('MISTRAL_API_KEY')),
        ),
    )
    knowledge_base.load(recreate=True)

    # Initializing Memory
    prescreen_memory = Memory(
        model=xAI(id="grok-3-mini"),
        # model=OpenAIChat(id='gpt-4o-mini'),
        db=SqliteMemoryDb(table_name="user_memories", db_file='Database/prescreen_memory.db'),
    )

    PreScreenBot = Agent(
        name='PreScreen Bot',
        model=MistralChat(id='mistral-large-latest', api_key=os.getenv('MISTRAL_API_KEY')),
        description='You are a PreScreen Bot designed to assist HR in pre-screening candidates for interviews.',
        instructions=dedent('''
        You are PreScreenBot, a professional and concise conversational AI designed to conduct pre-screening interviews for job candidates.

        Interaction flow:
        1. Candidate Identification
        - Greet the candidate professionally.
        - Ask for their full name and email address.

        2. Candidate Verification
        - Call the `get_all_candidates` tool to retrieve all candidate records.
        - Find the candidate by matching the provided name and email.
        - If the candidate is not found, politely end the conversation.
        - If found, check the DidScreening field:
            - If true, inform them screening has already been completed and end.
            - If false, proceed.

        3. Screening Preparation
        - Check the candidate’s Department and Position.
        - Use the knowledge base to retrieve the job posting for the position they applied to.

        4. Pre-screening Interview
        - Ask necessary and relevant screening questions based on the job posting.
        - Keep the conversation focused and not too long.
        - Assess answers according to the scoring rubric and job requirements.

        5. Conclusion
        - Thank the candidate for their time.
        - Inform them that their profile and screening results will be forwarded to HR.

        6. Post-interview Update
        - Call `update_candidate` to update:
            - DidScreening → true
            - PassedScreening → true if you determine they fit the position, otherwise false
            - Summary → A detailed explanation of why they are or are not a good fit, referencing their answers and highlighting key points.

        Behavior guidelines:
        - Be polite, professional, and concise.
        - Use clear, simple questions without unnecessary complexity.
        - Ensure the tone is friendly but business-like.

        IMPORTANT: Do not ask any extra questions to the candidate, update the candidate's record with the results of the interview.
        '''),
        tools=[get_all_candidates, update_candidate],
        # debug_mode=True,
        memory=prescreen_memory,
        enable_agentic_memory=True,
        add_history_to_messages=True,
        knowledge=knowledge_base,
    )
    return PreScreenBot

# agent = create_recruitment_module()
# agent.print_response('hello')

# def run_recruitment_module(input_text: str):
#     response = HRManagerAgent.run(input_text)
#     print(response)


# while True:
#     user_input = input("Enter a command: ")
#     if user_input == "exit":
#         break
#     HRManagerAgent.print_response(user_input)


# while True:
#     user_input = input("Enter a command: ")
#     if user_input == "exit":
#         break
#     PreScreenBot.print_response(user_input)


# InterviewSchedulerAgent.print_response('create a new booking for tomorrow at 12:00 PM to 12:30 PM, for the candidate: marouanechaibat@gmail.com named Marouane Chaibat')

# ResumeScreenerAgent.print_response(dedent('''
#     Resume Path: MarkdownResumes/ayoubankote_cv.md
#     Job Description:
#     Position Summary

#     As an AI Engineer, you will be at the forefront of integrating artificial intelligence into The Flex’s systems. You’ll build, deploy, and optimize AI-driven tools and models that support operations, customer experience, automation, and decision-making. This is a high-impact role with the potential to shape the future of tech in the real estate industry.

#     Key Responsibilities

#     AI & ML Development: Build and train machine learning models for use cases like pricing optimization, Property Management Tools.
#     LLM Integration: Develop and integrate LLM-powered features (e.g., GPT APIs) into internal tools and customer-facing products.
#     Automation: Leverage AI to automate repetitive internal tasks, enhance support, and improve user experience.
#     Deployment: Package and deploy models into production using modern MLOps tools and cloud infrastructure (preferably AWS).
#     Collaboration: Work closely with engineers, product managers, and operations teams to identify and implement impactful AI opportunities.
#     Documentation & Maintenance: Ensure reproducibility, versioning, and continuous improvement of all AI models and pipelines.

#     What We’re Looking For

#     Strong problem-solving skills and a proactive mindset.
#     Clear communication and a collaborative attitude.
#     Ability to thrive in a fast-paced, remote-first startup environment.
# '''))

# memory.clear()
# while True:
#     user_input = input("Enter a command: ")
#     if user_input == "exit":
#         break
#     ResumeScreenerAgent.print_response(user_input)
