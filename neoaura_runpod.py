# from dotenv import load_dotenv
import os
import pdb

from langchain_community.graphs import Neo4jGraph
import sys
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
#from langchain_unstructured import UnstructuredLoader
# from langchain.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Tuple, List
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WikipediaLoader
from langchain.text_splitter import TokenTextSplitter
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer


from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
)
# import pdb
# pdb.set_trace()
# load_dotenv()
#
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

# print(f"Connected to {NEO4J_URI} as {NEO4J_USERNAME}")

#chat = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0, model="gpt-4o-mini")
chat = ChatOpenAI(temperature=0, model_name="gpt-4-turbo", openai_api_key=OPENAI_API_KEY)

#chat = ChatOpenAI(temperature=0)


kg = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
)
# pdb.set_trace()
#llm_transformer = LLMGraphTransformer(llm=chat)
#text = """
#Marie Curie, born in 1867, was a Polish and naturalised-French physicist and chemist who conducted pioneering research on radioactivity.
#She was the first woman to win a Nobel Prize, the first person to win a Nobel Prize twice, and the only person to win a Nobel Prize in two scientific fields.
#Her husband, Pierre Curie, was a co-winner of her first Nobel Prize, making them the first-ever married couple to win the Nobel Prize and launching the Curie family legacy of five Nobel Prizes.
#She was, in 1906, the first woman to become a professor at the University of Paris.
#"""
#documents = [Document(page_content=text)]
#graph_documents = llm_transformer.convert_to_graph_documents(documents)
##print(f"Nodes:{graph_documents[0].nodes}")
#print(f"Relationships:{graph_documents[0].relationships}")
#sys.exit(0)


loader = Docx2txtLoader("stockguide.docx")

raw_documents = loader.load()


# List of PDF file paths
# pdf_file_paths = [
#     "Form1095a_2024.pdf",
#     "nerutest.pdf"
# ]

# Initialize an empty list to store all documents
pdf_docs = []

# Loop through the PDF files and load each one
# for pdf_file in pdf_file_paths:
#     pdfLoader = UnstructuredFileLoader(pdf_file)
#     pdf_docs += pdfLoader.load()  # Append the loaded documents to the list


# pdfLoader = UnstructuredFileLoader("Form1095a_2024.pdf")
# pdf_docs = pdfLoader.load()

# alldocs = []
# alldocs.append(raw_documents)
# alldocs.append(pdf_docs)
alldocs = raw_documents + pdf_docs  # Combine lists into a single flat list




# llm_transformer = LLMGraphTransformer(llm=chat, node_properties=True,
#                                       relationship_properties = True)

llm_transformer = LLMGraphTransformer(llm=chat, node_properties=True)


# pdb.set_trace()

for ent in alldocs:
    print(f"Processing document: {type(ent)}")
    text_splitter = SemanticChunker(OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY))
    documents = text_splitter.split_documents([ent])
    #
    graph_documents = llm_transformer.convert_to_graph_documents(documents)

    # store to neo4j
    # res = kg.add_graph_documents(    yadav's code
    kg.add_graph_documents(
        graph_documents,
        include_source=True,
        baseEntityLabel=True,
    )


# Hybrid Retrieval for RAG
# create vector index
vector_index = Neo4jVector.from_existing_graph(
    OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding",
    username=NEO4J_USERNAME,
    url=NEO4J_URI,  # Pass Neo4j URI explicitly
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
    # auth=(NEO4J_USERNAME, NEO4J_PASSWORD)  # Pass authentication explicitly
)


# Extract entities from text
class Entities(BaseModel):
    """Identifying information about entities."""

    names: List[str] = Field(
        ...,
        description="All the person, organization, or business entities that "
        "appear in the text",
    )


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are extracting organization and person entities from the text.",
        ),
        (
            "human",
            "Use the given format to extract information from the following "
            "input: {question}",
        ),
    ]
)
entity_chain = prompt | chat.with_structured_output(Entities)


# Retriever
kg.query("CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")


def generate_full_text_query(input: str) -> str:
    """
    Generate a full-text search query for a given input string.

    This function constructs a query string suitable for a full-text search.
    It processes the input string by splitting it into words and appending a
    similarity threshold (~2 changed characters) to each word, then combines
    them using the AND operator. Useful for mapping entities from user questions
    to database values, and allows for some misspelings.
    """
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()


# Fulltext index query
def structured_retriever(question: str) -> str:
    """
    Collects the neighborhood of entities mentioned
    in the question
    """
    result = ""
    entities = entity_chain.invoke({"question": question})
    for entity in entities.names:
        print(f" Getting Entity: {entity}")
        response = kg.query(
            """CALL db.index.fulltext.queryNodes('entity', $query, {limit:2})
            YIELD node,score
            CALL {
              WITH node
              MATCH (node)-[r:!MENTIONS]->(neighbor)
              RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
              UNION ALL
              WITH node
              MATCH (node)<-[r:!MENTIONS]-(neighbor)
              RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id AS output
            }
            RETURN output LIMIT 50
            """,
            {"query": generate_full_text_query(entity)},
        )
        # print(response)
        result += "\n".join([el["output"] for el in response])
    return result




# Final retrieval step
def retriever(question: str):
    print(f"Search query: {question}")
    structured_data = structured_retriever(question)
    unstructured_data = [
        el.page_content for el in vector_index.similarity_search(question)
    ]
    final_data = f"""Structured data:
{structured_data}
Unstructured data:
{"#Document ". join(unstructured_data)}
    """
    print(f"\nFinal Data::: ==>{final_data}")
    return final_data


# Define the RAG chain
# Condense a chat history and follow-up question into a standalone question
_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question,
in its original language.
Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""  # noqa: E501
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)


def _format_chat_history(chat_history: List[Tuple[str, str]]) -> List:
    buffer = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))
    return buffer


_search_query = RunnableBranch(
    # If input includes chat_history, we condense it with the follow-up question
    (
        RunnableLambda(lambda x: bool(x.get("chat_history"))).with_config(
            run_name="HasChatHistoryCheck"
        ),  # Condense follow-up question and chat into a standalone_question
        RunnablePassthrough.assign(
            chat_history=lambda x: _format_chat_history(x["chat_history"])
        )
        | CONDENSE_QUESTION_PROMPT
        | ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
        | StrOutputParser(),
    ),
    # Else, we have no chat history, so just pass through the question
    RunnableLambda(lambda x: x["question"]),
)

template = """Answer the question based only on the following context:
{context}

Question: {question}
Use natural language and be concise.
Answer:"""
prompt = ChatPromptTemplate.from_template(template)

chain = (
    RunnableParallel(
        {
            "context": _search_query | retriever,
            "question": RunnablePassthrough(),
        }
    )
    | prompt
    | chat
    | StrOutputParser()
)

# TEST it all out!
res_simple = chain.invoke(
    {
        "question": "tell me about what is RSI",
    }
)

print(f"\n Results === {res_simple}\n\n")

