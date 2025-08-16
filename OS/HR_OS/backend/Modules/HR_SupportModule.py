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
from agno.knowledge.markdown import MarkdownKnowledgeBase

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TICKET_TABLE_ID = os.getenv('AIRTABLE_TICKET_TABLE_ID')

def get_all_tickets() -> list[dict]:
    """
    Get all records from the table

    Returns:
    - A list of dictionaries of records
    """
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TICKET_TABLE_ID)
    return table.all()

def add_ticket(data: dict):
    """
    Add a record to the table

    Args:
    - data (dict): A dictionary where keys are field names and values are the data to insert.
    """
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TICKET_TABLE_ID)
    table.create(data)

def update_ticket(record_id: str, data: dict):
    """
    Update a record in the table

    Args:
    - record_id (str): The id of the record to update
    - data (dict): A dictionary where keys are field names and values are the data to update.
    """
    api = Api(AIRTABLE_API_KEY)
    table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TICKET_TABLE_ID)
    table.update(record_id, data)

def create_hr_support_module():
    # Initializing Knowledge Base
    knowledge_base = MarkdownKnowledgeBase(
        path="CompanyKnowledge/company_data.md",
        vector_db=PgVector(
            table_name="company_data",
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

    HelpDeskAgent = Agent(
        name='Help Desk Agent',
        # model=xAI(id="grok-3-mini"),
        model=MistralChat(id='mistral-large-latest', api_key=os.getenv('MISTRAL_API_KEY')),
        description='You are a HelpDeskAgent assisting an HR manager in managing employee tickets and answering HR-related questions using the company knowledge base.',
        instructions=dedent('''
        You are a HelpDeskAgent assisting an HR manager in managing employee tickets and answering HR-related questions using the company knowledge base.

        You have access to the following tools:
        - add_ticket(data: dict): Add a new ticket with the provided data.
        - update_ticket(record_id: str, data: dict): Update an existing ticket by its record ID.
        - get_all_tickets() -> list[dict]: Retrieve a list of all existing tickets.

        IMPORTANT INSTRUCTIONS:

        1. Always start by calling `get_all_tickets()` to get the current state of all tickets.

        2. Ticket fields available for updates:
        - Full Name
        - Email
        - Department
        - Position
        - Ticket Subject
        - Ticket Status
        - Ticket Comment

        3. When adding a ticket:
        - Use `add_ticket(data: dict)` with all required fields.
        - Include any optional fields if the HR provides them.
        - After adding, call `get_all_tickets()` to verify the new ticket exists.

        4. When updating a ticket:
        - Only call `update_ticket(record_id, data)` if `data` contains at least one valid field from the list above.
        - Map HR requests to the correct field names. Example: If HR says "mark ticket as resolved", update `"status": "Resolved"`.
        - Do not call `update_ticket` with an empty dictionary. If unsure which fields to update, ask the HR for clarification.
        - After updating, call `get_all_tickets()` to verify the change.

        Example: Updating the status and adding a comment to a ticket
        record_id = "recOvMgtkfcfDMao4"  # The ticket ID to update
        data = {
            "status": "Rejected",
            "comments": "You are not eligible for the reimbursment."
        }
        update_ticket(record_id, data)

        5. When responding to HR questions:
        - Use the company knowledge base for accurate answers.
        - If an answer requires ticket data, retrieve it using `get_all_tickets()`.
        - Always confirm ticket actions before executing changes.

        6. Interaction style:
        - Be professional, friendly, and supportive.
        - If something is unclear or incomplete, kindly ask the HR for more details.
        - Ensure HR’s work is faster and easier by managing tickets accurately.

        Goal:
        Be a reliable HR assistant who can efficiently manage tickets and provide precise answers from the knowledge base, while verifying all updates in the ticket table.
        '''),
        tools=[ReasoningTools(add_instructions=True), add_ticket, update_ticket, get_all_tickets],
        # debug_mode=True,
        memory=memory,
        enable_agentic_memory=True,
        add_history_to_messages=True,
        knowledge=knowledge_base,
    )
    return HelpDeskAgent

# memory.clear()

# while True:
#     user_input = input("Enter a command: ")
#     if user_input == "exit":
#         break
#     HelpDeskAgent.print_response(user_input)