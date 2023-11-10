import os

import openai
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.embeddings import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain.schema.messages import SystemMessage
from langchain.tools import ShellTool

# from tools.google import GoogleSearchTool
# from tools.web import BrowseWebSiteTool

# from langchain.tools.google_search.tool import GoogleSearchResults
# from langchain.utilities import GoogleSearchAPIWrapper


AZURE_OPENAI_DEPLOYMENT_GPT4 = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT4")
AZURE_OPENAI_DEPLOYMENT_EMBEDDING = os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING")


def create_agent(system_message=None, streaming=False, verbose=False):
    if openai.api_type == "azure":
        llm = AzureChatOpenAI(
            model="gpt-4",
            temperature=0,
            azure_deployment=AZURE_OPENAI_DEPLOYMENT_GPT4,
            streaming=streaming,
            cache=False,
            verbose=verbose,
        )
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=AZURE_OPENAI_DEPLOYMENT_EMBEDDING
        )
    else:
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            streaming=streaming,
            cache=False,
            verbose=verbose,
        )
        embeddings = OpenAIEmbeddings()

    tools = [
        ShellTool(),
    ]
    agent = create_conversational_retrieval_agent(
        llm,
        tools,
        system_message=SystemMessage(content=system_message),
        verbose=verbose,
    )
    return agent
