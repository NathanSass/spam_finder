from typing import List
import json
import os
from typing import Any, Dict
from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAI  # Updated import statement based on warning
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, WebsiteSearchTool

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
        search_tool = SerperDevTool(
            api_key=os.getenv("SERPER_API_KEY")
        )  # Ensure API key is provided
        web_rag_tool = WebsiteSearchTool(
            api_key=os.getenv("WEBSITE_SEARCH_API_KEY")
        )  # Ensure API key is provided

        # Define the agent
        self.researcher = Agent(
            llm=llm,
            role="Spam link verifier",
            goal="Provide valid reasoning as to why a website could be considered illegitimate, not trustworthy or related to scam or spam",
            backstory="An expert analyst with a strong sense of duty to ensure users do not access websites that would compromise their safety on the internet",
            tools=[search_tool, web_rag_tool],
            verbose=True,
        )

    def verify_links(self, message: str):
        research = Task(
            description=f"Research a link for legitimacy. The message is: {message}",
            expected_output="""
                A JSON object with the following keys:
                - links: A list of links that have been checked
                - categories: For each harmful category that the link may be associated with, provide a confidence score between 0.0 and 1.0 with precision of 3.
                "categories": {
                    "advertising_and_promotion": 0.2367,
                    "phishing_and_fraud": 0.4812,
                    "financial_scam": 0.3158,
                    "malware_distribution": 0.0924,
                    "adult_content": 0.0075
                }
                - reasons: A list of the top three reasons why the link is not legitimate and the classification outcome
            """,
            agent=self.researcher,
        )

        # Create a crew to manage agents and tasks
        crew = Crew(agents=[self.researcher], tasks=[research], verbose=True)

        # Start the crew
        result = json.loads(crew.kickoff())
        scores = result["categories"]

        # Find the category with the highest score
        max_category = max(scores, key=scores.get)
        result["winning_category"] = max_category

        # self.persist_bad_links(result)
        return result

    def persist_bad_links(
        self, classification_result: Dict[str, Any]
    ):  # Change type annotation
        classification_output = (
            classification_result  # No need to parse JSON since it's already Dict
        )
        links = classification_output.get("links", "")
        category = classification_output.get("winning_category", "")
        if not category:
            print("No winning category found")
            return

        for link in links:
            print(f"Link: {link}")
            # self.save_bad_link(link, winning_category)

    def save_bad_link(self, link: str, winning_category: str):  # Change type annotation
        with open("store/bad_links.txt", "a") as file:
            file.write(f"{link} : {winning_category}\n")
