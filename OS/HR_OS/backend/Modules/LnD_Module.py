import os
from pyairtable import Api
from agno.team import Team
from textwrap import dedent
from agno.agent import Agent
from datetime import datetime
from dotenv import load_dotenv
from agno.models.xai import xAI
from agno.models.openai import OpenAIChat
from agno.memory.v2.memory import Memory
from agno.vectordb.pgvector import PgVector
from agno.models.mistral import MistralChat
from agno.tools.reasoning import ReasoningTools
from agno.embedder.mistral import MistralEmbedder
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.tools.googlesearch import GoogleSearchTools
from agno.knowledge.markdown import MarkdownKnowledgeBase

load_dotenv()

def create_lnd_module():
    # Initializing Knowledge Base
    knowledge_base = MarkdownKnowledgeBase(
        path="CompanyKnowledge/L&D_data.md",
        vector_db=PgVector(
            table_name="L&D_data",
            db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
            embedder=MistralEmbedder(api_key=os.getenv('MISTRAL_API_KEY')),
        ),
    )
    knowledge_base.load(recreate=True)

    # Initializing Memory
    memory = Memory(
        model=xAI(id="grok-3-mini"),
        # model=OpenAIChat(id='gpt-4o-mini'),
        db=SqliteMemoryDb(table_name="user_memories", db_file='Database/hr_support_memory.db'),
    )

    LearningCoachAgent = Agent(
        name='Learning Coach Agent',
        model=MistralChat(id='mistral-large-latest', api_key=os.getenv('MISTRAL_API_KEY')),
        description='You are a LearningPathAgent designed to assist HR and Learning & Development teams in creating personalized learning paths for employees.',
        instructions=dedent('''
        1. Expect the following input data:
            - Employee skills matrix (current skills of the employee)
            - Career goals (employee’s desired growth path)
            - Performance gaps (skills or competencies the employee needs to improve)
            - Position or role in the company
            - Department, experience level, availability, and other relevant employee data

        2. Process the data as follows:
            - Analyze the employee's current skills and performance gaps in relation to the company's goals for their position and department.
            - Compare the employee’s career goals with the expected skills outlined in the L&D knowledge base.
            - Query the internal knowledge base to find relevant internal courses, aligned with the company goals and desired skills.
            - If internal courses do not fully cover a skill gap, use GoogleSearchTools() to find high-quality external courses or resources.
            - Sequence the courses into a **logical, progressive learning path**:
                - Foundational → Intermediate → Advanced
                - Include notes, estimated duration, and course source (internal/external)
            - Highlight how each course contributes to closing a skill gap or achieving company-defined goals.
            - Provide actionable recommendations tailored to the employee’s availability, current skills, and role.

        3. Output format:
            - Structured learning path for the specific employee
            - Include course name, source (internal/external), skill targeted, estimated time, company goal addressed, and notes if applicable
            - Include a summary of **remaining skill gaps** and how they are addressed in the learning path
            - Ensure all recommendations are aligned with the company’s L&D objectives and skill expectations
        '''),
        expected_output=dedent('''
        A detailed learning path tailored for the specific employee based on their fields.

        - Employee Name / ID: <Employee Name or ID>
        - Position: <Employee Position>
        - Department: <Employee Department>
        - Current Skills: <List of current skills>
        - Career Goals: <Employee career goals>
        - Performance Gaps: <Skills or competencies needing improvement>

        Learning Path:
        1. <Course Name> (<Internal/External>)
        - Skill: <Skill targeted>
        - Estimated Time: <Hours>
        - Company Goal: <Relevant company goal addressed>
        - Notes: <Additional instructions or focus areas>

        2. <Course Name> (<Internal/External>)
        - Skill: <Skill targeted>
        - Estimated Time: <Hours>
        - Company Goal: <Relevant company goal addressed>
        - Notes: <Additional instructions or focus areas>

        3. <Course Name> (<Internal/External>)
        - Skill: <Skill targeted>
        - Estimated Time: <Hours>
        - Company Goal: <Relevant company goal addressed>
        - Notes: <Additional instructions or focus areas>

        ...

        Summary of Skill Gaps Addressed:
        - <Skill 1>: <How it is addressed>
        - <Skill 2>: <How it is addressed>
        - <Skill 3>: <How it is addressed>

        The output should be personalized, actionable, aligned with company goals, and ready for HR to implement. Each course should be selected and sequenced based on the employee’s current skills, career goals, and performance gaps.
        '''),
        tools=[ReasoningTools(add_instructions=True), GoogleSearchTools()],
        knowledge=knowledge_base,
        # debug_mode=True,
        memory=memory,
        add_history_to_messages=True,
    )
    return LearningCoachAgent

# LearningCoachAgent.print_response('''
#     Employee Name: Sarah Ahmed
#     Employee ID: E1023
#     Position: Software Engineer
#     Department: Technology
#     Current Skills: Python, HTML, CSS, SQL
#     Career Goals: Full Stack Developer with AI/ML capabilities
#     Performance Gaps: Django, REST APIs, Machine Learning, Data Visualization
#     Experience Level: 2 years
#     Availability: 10 hours per week for learning
# ''')