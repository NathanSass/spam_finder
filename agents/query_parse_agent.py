import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

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
        load_dotenv()
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"]
        )
        # Define the agent for classifying messages
        self.classifier = Agent(
            role="Message classifier",
            goal="Determine the source type of the message and clean it if necessary",
            backstory="An AI specialized in identifying the nature of communication and preparing it for further analysis",
        )

    def parse_query(self, message: str):
        classification_task = Task(
            description=f'Classify the source type of the following message and clean it if necessary: "{message}"',
            expected_output="""
                A JSON object with the following keys:
                - message_type: The source type of message - one of EMAIL, WEBPAGE, SMS, IMESSAGE
                - message: The cleaned message (removal of unnecessary HTML tags)
                - links: A list of links/URLs found in the message
                - sender: Email address of the original sender
            """,
            agent=self.classifier,
        )

        # Create a crew to manage agents and tasks
        crew = Crew(agents=[self.classifier], tasks=[classification_task])

        # Start the crew
        result = crew.kickoff()
        print(result)
        return result
