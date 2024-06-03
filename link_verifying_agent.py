from typing import List
import json
import os
from typing import Any, Dict
from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAI  # Updated import statement based on warning
from crewai import Agent, Task, Crew
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)
"""
This agent is responsible for verifying the legitimacy of a link

If the link is not legitimate, the agent will save the link to a file.
Currently, we aren't doing anything with saved links. But in the future, we could use them
for training or for checking against the cache.
"""
class LinkVerifyingAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv(find_dotenv())

        # Initialize OpenAI LLM with the API key
        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7)

        # Initialize tools
        search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))  # Ensure API key is provided
        web_rag_tool = WebsiteSearchTool(api_key=os.getenv("WEBSITE_SEARCH_API_KEY"))  # Ensure API key is provided

        # Define the agent
        self.researcher = Agent(
            role='Spam link verifier',
            goal='Provide validated results that a website exists and is not a scam or spam website',
            backstory='An expert analyst with a strong sense of duty to sniff out scams and explain how they know the links are legitimate',
            tools=[search_tool, web_rag_tool],
            verbose=True
        )


    
    def verify_links(self, message: str):
        research = Task(
            description=f'Research a link for legitimacy. The message is: {message}',
            expected_output='''
                A JSON object with the following keys:
                - links: A list of links that have been checked
                - scams: A list of scams that the link may be a part of ex. ["scam", "phishing", etc]
                - reasons: A list of the top 3 reasons why the link is either legitimate or not trustworthy
            ''',
            agent=self.researcher
        )

        # Create a crew to manage agents and tasks
        crew = Crew(
            agents=[self.researcher],
            tasks=[research],
            verbose=True
        )

        # Start the crew
        result =  crew.kickoff()
        self.persist_bad_links(json.loads(result))
        return result

    
    def persist_bad_links(self, classification_result: Dict[str, Any]):  # Change type annotation
        classification_output = classification_result  # No need to parse JSON since it's already Dict
        links = classification_output.get("links", "")
        scams = classification_output.get("scams", "")
        if not scams:
            print("No scams found")
            return
        
        for link in links:
            print(f"Link: {link}")
            self.save_bad_link(link, scams)

    def save_bad_link(self, link: str, scams: List[str]):  # Change type annotation
        with open("store/bad_links.txt", "a") as file:
            file.write(f"{link} : {scams}\n")

