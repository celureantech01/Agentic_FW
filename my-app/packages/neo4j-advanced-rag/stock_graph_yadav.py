from dotenv import load_dotenv
import os
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
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Tuple, List
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
import os
from langchain_community.graphs import Neo4jGraph
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
import pdb
pdb.set_trace()
load_dotenv()

# AURA_INSTANCENAME = os.environ["AURA_INSTANCENAME"]
NEO4J_URI = os.environ["bolt://localhost:7687"]
NEO4J_USERNAME = os.environ["neo4j"]
NEO4J_PASSWORD = os.environ["Goodjob@1"]
NEO4J_DATABASE = os.environ["neo4j"]
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)
#
OPENAI_API_KEY = os.getenv("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")
# OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")

# environ['OPENAI_API_KEY']= "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"
# environ['NEO4J_USERNAME']= "neo4j"
# environ['NEO4J_PASSWORD']= "Goodjob@1"
# environ['NEO4J_URI']= "bolt://localhost:7687"

#chat = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0, model="gpt-4o-mini")
chat = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")

#chat = ChatOpenAI(temperature=0)


kg = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    database=NEO4J_DATABASE,
)
pdb.set_trace()
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

# # read the wikipedia page for the Roman Empire
raw_documents = WikipediaLoader(query="The Roman empire").load()

loader = Docx2txtLoader("Stockdoc_v3.txt")

raw_documents = loader.load()

# # # # Define chunking strategy
text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
text_splitter = SemanticChunker(OpenAIEmbeddings())
documents = text_splitter.split_documents(raw_documents)
pdb.set_trace()
#print(documents)

llm_transformer = LLMGraphTransformer(llm=chat)
pdb.set_trace()
graph_documents = llm_transformer.convert_to_graph_documents(documents)

# store to neo4j
res = kg.add_graph_documents(
    graph_documents,
    include_source=True,
    baseEntityLabel=True,
)


# Hybrid Retrieval for RAG
# create vector index
vector_index = Neo4jVector.from_existing_graph(
    OpenAIEmbeddings(),
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="embedding",
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
        | ChatOpenAI(temperature=0)
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
        "question": "What is RSI and how can I use RSI to buy stocks",
    }
)

print(f"\n Results === {res_simple}\n\n")

