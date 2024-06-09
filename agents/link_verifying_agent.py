import json
import os
from dotenv import load_dotenv
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, WebsiteSearchTool
from score_evaluator.score_evaluator import ScoreEvaluator

"""
This agent is responsible for verifying the legitimacy of a link

If the link is not legitimate, the agent will save the link to a file.
Currently, we aren't doing anything with saved links. But in the future, we could use them
for training or for checking against the cache.
"""


class LinkVerifyingAgent:
    def __init__(self):
        # Initialize OpenAI LLM with the API key
        load_dotenv()
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY")
        )
        # llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7)

        # Initialize tools
        search_tool = SerperDevTool(
            api_key=os.getenv("SERPER_API_KEY")
        )  # Ensure API key is provided
        web_rag_tool = WebsiteSearchTool(
            api_key=os.getenv("WEBSITE_SEARCH_API_KEY")
        )  # Ensure API key is provided

        self.analyst = Agent(
            role="Security and Fraud Researcher",
            goal="Provide valid evidence and a decision based on the criteria provided",
            backstory="An expert researcher that can leverage web searches as needed to do thorough research",
            tools=[search_tool, web_rag_tool],
        )

        # Define the agent
        self.researcher = Agent(
            role="Security and Fraud Analyst",
            goal="Provide valid reasoning as to why a message could be considered illegitimate, not trustworthy or related to scam or spam",
            backstory="An expert analyst with a strong sense of duty to ensure users do not interact with emails that would compromise their safety on the internet",
        )

    def verify_links(self, message: str):
        # Content Analysis: Keywords and Phrases
        content_analysis_keywords = Task(
            description=f"Analyze the content for keywords and phrases associated with financial scams. Examples of common phrases are Urgent and confidential, exclusive opportunity, guaranteed returns, secret strategy, unclaimed funds, send wire transfer, Nigerian prince. The message is: {message}",
            expected_output="""
                        A JSON object with the following keys:
                        - evidence: List of reasons why this email may or may not be related to a financial scams
                        - decision: A statement indicating whether this email is or isn't attempting a financial scam
                    """,
            agent=self.researcher,
            async_execution=True,
        )

        # Content Analysis: Tone and Urgency
        content_analysis_tone = Task(
            description=f"Analyze the tone and urgency of the email. Identify phrases that create a sense of urgency or panic. Example phrases correlating to a high score are: 'You must act ASAP to avoid legal action', 'click here to review your late fees'. The message is: {message}",
            expected_output="""
                        A JSON object with the following keys:
                        - evidence: List of reasons why the email strikes urgency/panic or is normal in tone
                        - decision: A statement indicating whether this email is strinking unnecessary urgency.
                    """,
            agent=self.researcher,
            async_execution=True,
        )

        # Sender Analysis: Email Address Patterns
        sender_analysis_email = Task(
            description=f"Analyze the sender's email address for patterns indicating it may be used in financial scams. Look for suspicious email domains, free email services but acting as a known public entity, and patterns that may come across as scam tactics. Emails with legitimate domains but from no-reply or calendar-notification@google.com are often safe. The sender's email can be found in the message: {message}",
            expected_output="""
                        A JSON object with the following keys:
                        - evidence: List of reasons why this email address may or may not be suspicious
                        - decision: A statement indicating whether this email is or isn't associated with a scam
                    """,
            agent=self.researcher,
            async_execution=True,
        )

        # Sender Analysis: Impersonation of Trusted Entities
        sender_imitation_check = Task(
            description=f"Check if the sender is impersonating a known entity. Consider known entities and what their trusted email domain would be. The message and sender's email can be found in the message: {message}",
            expected_output="""
                        A JSON object with the following keys:
                        - evidence: A list of reasons why the sender could be impersonating a trusted entity or if its a trustworthy account
                        - decision: A statement indicating whether this email is attempting to be someone else, a junk email or from a personal email account (i.e.: gmail.com, live.com, etc)
                    """,
            agent=self.researcher,
            async_execution=True,
        )

        # Suspicious URLs
        link_analysis = Task(
            description=f"Analyze hyperlinks in the email for suspicious URLs. The message is: {message}",
            expected_output="""
                        A JSON object with the following keys:
                        - evidence: List of links in the message that would be identified as suspicious. If they are not suspicious, leave them out of the list.
                        - decision: A statement indicating whether this email contains suspicious links.
                    """,
            agent=self.researcher,
            async_execution=True,
        )

        # Contextual Inconsistencies: Grammar and Spelling Errors
        contextual_grammar_check = Task(
            description=f"Check the email for grammar and spelling errors that might indicate a scam. The message is: {message}",
            expected_output="""
                        A JSON object with the following keys:
                        - evidence: A list of sentences or phrases with notable errors
                        - decision: A statement indicating whether this email is written with mostly accurate spelling or grammar, or not.
                    """,
            agent=self.researcher,
            async_execution=True,
        )

        # Contextual Inconsistencies: Unusual Requests
        context_unusual_requests = Task(
            description=f"Identify unusual requests for personal or financial information in the email. The message is: {message}",
            expected_output="""
                        A JSON object with the following keys:
                        - evidence: List of unusual requests found in the email
                        - decision: A statement indicating whether this email contains unusual requests, or normal asks.
                    """,
            agent=self.researcher,
            async_execution=True,
        )

        # Cross-referencing External Data: Known Scam Databases
        external_scam_check = Task(
            description=f"Cross-reference the email content with previous instances of known online scams. Examples include: mystery inheritances, lottery or prize scams, or tax refund scams.  The message is: {message}",
            expected_output="""
                        A JSON object with the following keys:
                        - evidence: List of known scams that match the email content
                        - decision: A statement indicating whether this email is attempting to execute a scam or its just a normal ask.
                    """,
            agent=self.researcher,
            async_execution=True,
        )

        # Integrated Threat Intelligence
        threat_intelligence_check = Task(
            description=f"Using real-time threat intelligence feeds, analyze and cross-check the email against the latest scam tactics and emerging threats. The message is: {message}",
            expected_output="""
                        A JSON object with the following keys:
                        - evidence: List of the latest scam tactics and threats related to the email content
                        - decision: A statement indicating whether this email aligns with the latest scams or if it is unassuming.
                    """,
            agent=self.researcher,
            async_execution=True,
        )

        score_evaluator = ScoreEvaluator()
        threshold_score = score_evaluator.get_config()["scoring_system"]["thresholds"][
            "single_category"
        ]
        analyze = Task(
            description=f"Consider this email message that has arrived in your email inbox. You have some evidence and scores from other researchers on the likelihood of this email containing qualities of spam or scams. Provide a confidence score for each category based on your judgement on whether this email is harmful or malicious. Note that values equal or over {threshold_score} for any category will automatically mark the message as spam, so think thoroughly in your decision making process. Here is the message: {message}",
            expected_output="""
                A JSON object with the following keys:
                - links: A list of links in the message that have been checked
                - categories: For each harmful category that the link may be associated with, provide a confidence score between 0.0 and 1.0 with precision of 3.
                "categories": {
                    "advertising_and_promotion": 0.2367,
                    "phishing_and_fraud": 0.4812,
                    "financial_scam": 0.3158,
                    "malware_distribution": 0.0924,
                    "adult_content": 0.0075
                }
                - reasons: A list of the top three reasons why the message is not legitimate and the classification outcome.
            """,
            agent=self.researcher,
            context=[
                content_analysis_keywords,
                content_analysis_tone,
                threat_intelligence_check,
                external_scam_check,
                context_unusual_requests,
                contextual_grammar_check,
                link_analysis,
                sender_imitation_check,
                sender_analysis_email,
            ],
            async_execution=False,  # awaits all other tasks to complete for context
        )

        # Create a crew to manage agents and tasks
        crew = Crew(
            agents=[self.researcher],
            tasks=[
                content_analysis_keywords,
                content_analysis_tone,
                threat_intelligence_check,
                external_scam_check,
                context_unusual_requests,
                contextual_grammar_check,
                link_analysis,
                sender_imitation_check,
                sender_analysis_email,
                analyze,
            ],
        )
        # Start the crew
        result = json.loads(crew.kickoff())
        scores = result["categories"]

        # Find the category with the highest score
        max_category = max(scores, key=scores.get)
        result["winning_category"] = max_category
        result["is_spam"] = score_evaluator.is_spam(result["categories"])
        return result
