import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import UnstructuredMarkdownLoader
import glob
import os
import time
from dotenv import load_dotenv
# 1. Initialize Pinecone
load_dotenv()
index_name = "plantie"
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
folder_path = "C:\\Users\\Bejoy Sumanam\\Desktop\\plantietalkie\\docs"
#Read excel file and convert into a csv for an vector store
excel_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
docs = []
for file in excel_files:
    df = pd.read_excel(file)
    table = df.to_markdown()
    #save table as markdown
    with open(file.replace(".xlsx", ".md"), "w", encoding="utf-8") as f:
        f.write(table)
    loader = UnstructuredMarkdownLoader(file.replace(".xlsx", ".md"))
    docs.extend(loader.load())


# 2. Create a vector store
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)
 
vectorstore  = PineconeVectorStore.from_documents(docs, embeddings, index_name=index_name)
