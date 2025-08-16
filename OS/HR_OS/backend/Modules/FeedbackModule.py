import os
from pathlib import Path
from pyairtable import Api
from agno.team import Team
from textwrap import dedent
from agno.agent import Agent
from datetime import datetime
from dotenv import load_dotenv
from agno.models.xai import xAI
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.models.mistral import MistralChat
from agno.tools.csv_toolkit import CsvTools
from agno.tools.reasoning import ReasoningTools
from agno.embedder.mistral import MistralEmbedder
from agno.memory.v2.db.sqlite import SqliteMemoryDb

load_dotenv()

def create_feedback_module():
    # Initializing Memory
    memory = Memory(
        model=xAI(id="grok-3-mini"),
        # model=OpenAIChat(id='gpt-4o-mini'),
        db=SqliteMemoryDb(table_name="user_memories", db_file='Database/feedback_memory.db'),
    )

    csv_tools = CsvTools(csvs=[], row_limit=100)

    EngagementSurveyAgent = Agent(
        name='Engagement Survey Agent',
        model=MistralChat(id='mistral-large-latest', api_key=os.getenv('MISTRAL_API_KEY')),
        description='You are an Engagement Survey Agent designed to analyze employee feedback data from surveys. You leverage sentiment analysis, trend detection, and benchmarking to identify strengths, areas for improvement, and actionable recommendations that align with organizational goals.',
        instructions=dedent('''
        You are an EngagementSurveyAgent tasked with analyzing employee survey data to provide a clear, professional, and actionable report.

        You have access to the `csv_tools` tool, which you can use to read and process the provided employee survey results CSV file. This file contains raw responses from employees, along with demographic information, historical data, and benchmark references.

        Your responsibilities:
        1. Load and understand the CSV data structure.
        2. Perform sentiment analysis on qualitative responses.
        3. Calculate and summarize overall engagement levels.
        4. Identify trends across time, departments, and demographics.
        5. Compare results against benchmarks if available.
        6. Highlight top strengths and top areas for improvement.
        7. Suggest actionable, practical recommendations for leadership.
        8. Flag any critical issues that require immediate attention.
        9. Organize the analysis in a professional, clear, and easy-to-read format.

        IMPORTANT: Analyze the given CSV file and provide a report, without asking any questions.

        Focus on delivering value-driven insights that can be acted upon, not just raw statistics.
        '''),
        expected_output=dedent('''
        A well-structured, professional engagement survey report containing:

        1. **Executive Summary**
        - High-level overview of key findings.
        - General sentiment trend.

        2. **Sentiment Analysis**
        - Percentage of positive, neutral, and negative responses.
        - Common themes from qualitative feedback.

        3. **Engagement Scores**
        - Overall engagement rating.
        - Scores broken down by department, role, or demographic groups.

        4. **Trend Analysis**
        - Changes compared to historical survey results.
        - Patterns over time.

        5. **Benchmark Comparison**
        - How results compare to internal/external benchmarks.

        6. **Strengths**
        - Top 3 areas where the organization performs best.

        7. **Areas for Improvement**
        - Top 3 challenges or weaknesses identified.

        8. **Actionable Recommendations**
        - Clear, practical steps to address improvement areas.
        - Suggestions aligned with company goals.

        9. **Alerts/Notifications**
        - Immediate issues requiring leadership attention.

        All findings should be presented in clear, concise, and visually understandable text format, ready for leadership review.
        '''),
        tools=[ReasoningTools(add_instructions=True), csv_tools],
        memory=memory,
        debug_mode=True,
        enable_agentic_memory=True,
        add_history_to_messages=True,
    )
    return EngagementSurveyAgent

# def run_feedback_module(path_to_csv: str):
#     csv_tools.csvs = [Path(path_to_csv)]
#     EngagementSurveyAgent.print_response('''
#     Analyze the data of the employee survey and provide a report.
#     ''')

# run_feedback_module('../FeedbackResults/EmployeeSatisfactionSurvey.csv')
