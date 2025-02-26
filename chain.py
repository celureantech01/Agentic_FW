from typing import List, Union
# from dotenv import load_dotenv
import os
from langchain.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema
from langchain_community.graphs import Neo4jGraph
from langchain_core.messages import (
    AIMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_groq import ChatGroq
from langchain_core.prompts.prompt import PromptTemplate

from langchain.chains import GraphCypherQAChain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
import pdb
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

pdb.set_trace()
# load_dotenv()

# AURA_INSTANCENAME = os.environ["AURA_INSTANCENAME"]
# NEO4J_URI = os.environ["NEO4J_URI"]
# NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
# NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
# NEO4J_DATABASE = os.environ["NEO4J_DATABASE"]
# AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)
#
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")

# Hardcoded Neo4j connection parameters
AURA_INSTANCENAME = "Instance01"
NEO4J_URI = "neo4j+s://003b60a2.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "fTRrJ8c4IqStufne2cMF2A4c1sPMKaIBWJxij3slWPk"
NEO4J_DATABASE = "neo4j"
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)

# Hardcoded OpenAI credentials
OPENAI_API_KEY = "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"
#OPENAI_ENDPOINT =   # Not needed unless using Azure OpenAI



graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
)


# Connection to Neo4j
#graph = Neo4jGraph()

# Cypher validation tool for relationship directions
corrector_schema = [
    Schema(el["start"], el["type"], el["end"])
    for el in graph.structured_schema.get("relationships")
]
cypher_validation = CypherQueryCorrector(corrector_schema)

# LLMs
#cypher_llm = ChatOpenAI(model="gpt-4", temperature=0.0)
#qa_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

qa_llm = cypher_llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

# Generate Cypher statement based on natural language input
cypher_template = """Based on the Neo4j graph schema below, write a Cypher query that would answer the user's question:
{schema}

Question: {question}
Cypher query:"""  # noqa: E501

cypher_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Given an input question, convert it to a Cypher query. No pre-amble.",
        ),
        ("human", cypher_template),
    ]
)

cypher_response = (
    RunnablePassthrough.assign(
        schema=lambda _: graph.get_schema,
    )
    | cypher_prompt
    | cypher_llm.bind(stop=["\nCypherResult:"])
    | StrOutputParser()
)

response_system = """You are an assistant that helps to form nice and human 
understandable answers based on the provided information from tools.
Do not add any other information that wasn't present in the tools, and use 
very concise style in interpreting results!
"""

response_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=response_system),
        HumanMessagePromptTemplate.from_template("{question}"),
        MessagesPlaceholder(variable_name="function_response"),
    ]
)

def get_function_response(
        query: str, question: str
        ) -> List[Union[AIMessage, ToolMessage]]:
#    pdb.set_trace()
    print(str(query))
    context = graph.query(cypher_validation(query))
    TOOL_ID = "call_H7fABDuzEau48T10Qn0Lsh0D"
    messages = [
        AIMessage(
                content="",
                additional_kwargs={
                "tool_calls": [
                {
                "id": TOOL_ID,
                "function": {
                "arguments": '{"question":"' + question + '"}',
                "name": "GetInformation",
                },
                "type": "function",
                }
                ]
                },
                ),
        ToolMessage(content=str(context), tool_call_id=TOOL_ID),
    ]
    print(str(messages))
    return messages


chain = (
    RunnablePassthrough.assign(query=cypher_response)
    | RunnablePassthrough.assign(
        function_response=lambda x: get_function_response(x["query"], x["question"])
    )
    | response_prompt
    | qa_llm
    | StrOutputParser()
)

# Add typing for input


class Question(BaseModel):
    question: str


#original_query = "Based on Apple earning report do you recommend Apple Stock ? Give me step by step explanation on how did you reach to that conclusion"
#original_query="based on the apple financial results extract key parameters, indicators and calculations and synthesize the information to predict apple future stock price. Give me step by step explanation on how did you reach to that conclusion"
#original_query="What is Apple revenue. Give me step by step explanation on how did you reach to that conclusion"
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

The question is:
{question} 

Important: In the generated Cypher query, the RETURN statement must explicitly include the property values used in the query's filtering condition, alongside the main information requested from the original question.

"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)

original_query="Show me technical indicator which determine over bought and under bought signal for a stock"
#chain2 = GraphCypherQAChain.from_llm(ChatOpenAI(temperature=0), graph=graph, verbose=True, allow_dangerous_requests=True)
#chain2 = chain = GraphCypherQAChain.from_llm(cypher_prompt= CYPHER_GENERATION_PROMPT,llm=ChatOpenAI(temperature=0), graph=graph, verbose=True, allow_dangerous_requests=True)
pdb.set_trace()
res = chain.invoke({"question": original_query})
#print(str(res))
#res = chain2.invoke("Show me technical indicator which determine over bought and under bought signal for a stock")
pdb.set_trace()
print(str(res))
