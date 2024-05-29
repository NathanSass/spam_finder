import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAI  # Updated import statement based on warning
from crewai import Agent, Task, Crew
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)

# Load environment variables
load_dotenv(find_dotenv())

# Initialize OpenAI LLM with the API key
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7)

# Initialize tools
search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))  # Ensure API key is provided
web_rag_tool = WebsiteSearchTool(api_key=os.getenv("WEBSITE_SEARCH_API_KEY"))  # Ensure API key is provided

# Define the agent
researcher = Agent(
    role='Spam link verifier',
    goal='Provide validated results that a website exists and is not a scam or spam website',
    backstory='An expert analyst with a strong sense of duty to sniff out scams and explain how they know the link is legitimate',
    tools=[search_tool, web_rag_tool],
    verbose=True
)

# Define the task
message = "You just won the lottery! Visit www.t.co/lottery to claim your prize"
research = Task(
    description=f'Research a link for legitimacy. The message is: {message}',
    expected_output='A summary of the top 3 reasons why the link is either legitimate or not trustworthy',
    agent=researcher
)

# Create a crew to manage agents and tasks
crew = Crew(
    agents=[researcher],
    tasks=[research],
    verbose=True
)

# Start the crew
crew.kickoff()