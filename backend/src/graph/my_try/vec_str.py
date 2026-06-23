from pathlib import Path

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_ollama import OllamaEmbeddings

from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank


CHROMA_PATH = "chroma_db/compliance_db"

embeddings = OllamaEmbeddings(model="mxbai-embed-large:335m",)

def build_vector_store():

    docs = []

    pdf_folder = Path(
        "backend/data"
    )

    for pdf_file in pdf_folder.glob(
        "*.pdf"
    ):

        loader = PyPDFLoader(
            str(pdf_file)
        )

        loaded_docs = loader.load()

        for doc in loaded_docs:

            doc.metadata[
                "source"
            ] = pdf_file.name

        docs.extend(
            loaded_docs
        )

    splitter = (
        RecursiveCharacterTextSplitter(
            chunk_size=750,
            chunk_overlap=150
        )
    )

    chunks = splitter.split_documents(
        docs
    )

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print(
        f"Stored {len(chunks)} chunks"
    )

def get_reranked_retriever():
    db = Chroma(
    persist_directory=
    "chroma_db/compliance_db",

    embedding_function=
    embeddings)

    vector_retriever = (
        db.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 10
            }
        )
    )


    all_docs = db.get()

    documents = [
        Document(
            page_content=text
        )
        for text in all_docs["documents"]
    ]

    bm25_retriever = (
        BM25Retriever.from_documents(
            documents
        )
    )

    bm25_retriever.k =  10

    hybrid_retriever = (
        EnsembleRetriever(
            retrievers=[
                bm25_retriever,
                vector_retriever
            ],
            weights=[
                0.5,
                0.5
            ]
        )
    )

        

    # 1. Initialize the lightweight cross-encoder compressor
    # Set top_n to the final number of total chunks you want back
    compressor = FlashrankRerank(top_n=5)

    # 2. Wrap your hybrid_retriever with the compressor
    reranked_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, 
        base_retriever=hybrid_retriever
    )
    
    return reranked_retriever