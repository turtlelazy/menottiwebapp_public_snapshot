import os
import openai
import pinecone
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from keys import openai_key
from keys import pinecone_api_key

#init
directory = 'contents'
openai.api_key = (openai_key)

#load docs
def load_docs(directory):
  loader = DirectoryLoader(directory)
  documents = loader.load()
  return documents

#documents = load_docs(directory)
#print(len(documents))

#chunking docs
def split_docs(documents, chunk_size=1000, chunk_overlap=20):
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
  docs = text_splitter.split_documents(documents)
  return docs

#docs = split_docs(documents)
#print(len(docs))

#openai embeddings
embeddings = OpenAIEmbeddings(openai_api_key = openai_key)
print("got embeddings")
#embeddings = OpenAIEmbeddings()
# query_result = embeddings.embed_query("Hello world")
# print(len(query_result))

#pinecone vector search
pinecone.init(
    api_key=pinecone_api_key,
    environment="us-west1-gcp-free"
)

index_name = "langchain-demo-index"

# index = Pinecone.from_documents(docs, embeddings, index_name=index_name)
index = Pinecone.from_existing_index(index_name, embeddings)
print("got index")

#similar documents query which finds and crops items of importance
def get_similiar_docs(query, k=2, score=False):
  if score:
    similar_docs = index.similarity_search_with_score(query, k=k)
  else:
    similar_docs = index.similarity_search(query, k=k)
  return similar_docs

#utilizing chatGPT

# model_name = "text-davinci-003"
# model_name = "gpt-3.5-turbo"
model_name = "gpt-3.5-turbo"
#llm = OpenAI(model_name=model_name, openai_api_key = openai_key)
llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo',openai_api_key = openai_key)
chain = load_qa_chain(llm, chain_type="stuff")

# Up to this point, everything that needs to be initialized has been initialized


def get_answer(query):
  similar_docs = get_similiar_docs(query)
  answer = chain.run(input_documents=similar_docs, question=query)
  return answer

try:
  print(get_answer("What is the requirement for scaffolding?"))
except:
  print("Failed to initialize")

if __name__ == "__main__": #false if this file imported as module
  query = "When is a pre-fire safety plan required?"
  answer = get_answer(query)
  print(query)
  print(answer)
# print()
# query = "What are the facade project inspection requirements?"
# answer = get_answer(query)
# print(query)
# print(answer)

# query = "What is the requirement for scaffolding"
# docs = index.similarity_search(query)
# print(docs)
