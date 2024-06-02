import os
import re
import json
from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAI
from crewai import Agent, Task, Crew
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)

"""
This agent will operate on a vague query and return formatted json which will be more easily parceable
for other agents.

Possible sources of query:
- a web extension that passes in some DOM elements, perhaps with minimal parsing. May include markup elements.
- an android app that passes in the result of the screen being read.
- etc.
"""
class QueryParsingAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv(find_dotenv())
        # Define the agent for classifying messages
        self.classifier = Agent(
            role='Message classifier',
            goal='Determine the source type of the message and clean it if necessary',
            backstory='An AI specialized in identifying the nature of communication and preparing it for further analysis',
            verbose=True
        )

    def parse_query(self, message: str):
        classification_task = Task(
            description=f'Classify the source type of the following message and clean it if necessary: "{message}"',
            expected_output='''
                A JSON object with the following keys:
                - message_type: The type of message (e.g. email, webpage, sms, iMessage, etc)
                - message: The cleaned message
                - links: A list of links found in the message
            ''',
            agent=self.classifier
        )

        # Create a crew to manage agents and tasks
        crew = Crew(
            agents=[self.classifier],
            tasks=[classification_task],
            verbose=True
        )

        # Start the crew
        result = crew.kickoff()
        return result
