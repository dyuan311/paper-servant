from typing import Optional, List
from agno.agent import Agent
from agno.models.openai import OpenAILike
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.embedder.openai import OpenAIEmbedder
from tools.wiki_tools import WikiTools
from tools.file_tools import FileTools
import os
from dotenv import load_dotenv

load_dotenv()

def get_knowledge_agent(model_id: str = "gpt-4o"):
    """
    Returns an Agent configured to manage and retrieve general AI knowledge.
    Uses Vector Database (LanceDB) for semantic search over papers and notes.
    """
    
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL_ID", model_id)
    
    # 1. Configure Vector DB (Local LanceDB)
    # We use OpenAIEmbedder for high quality embeddings. 
    # Make sure OPENAI_API_KEY is set or provide api_key explicitly if needed.
    # If using a local LLM, consider using OllamaEmbedder instead.
    embedder_api_key = os.getenv("OPENAI_API_KEY") or api_key # Fallback to general key
    
    vector_db = LanceDb(
        table_name="paper_knowledge",
        uri="knowledge/lancedb", # Store DB locally in project
        embedder=OpenAIEmbedder(
            id="text-embedding-3-small", 
            api_key=embedder_api_key
        )
    )

    # 2. Create Knowledge Base
    # We point it to the 'papers/' directory to index all PDFs
    # We can also add 'knowledge/wiki' if we want to index markdown files separately
    knowledge_base = PDFKnowledgeBase(
        path="papers/", 
        vector_db=vector_db,
        reader=PDFReader(chunk=True, chunk_size=1000, chunk_overlap=200),
        # num_documents=5 # Limit for testing, remove in production
    )
    
    # Note: In a real production app, you might want to call knowledge_base.load() 
    # only when new files are added, not on every agent initialization.
    # For now, we assume the user might manually trigger a "reindex" or we do it lazily.
    # To avoid startup delay, we DO NOT call knowledge_base.load() here automatically 
    # unless we check for existence.
    
    def reindex_vector_db() -> str:
        """
        Manually trigger the re-indexing of the PDF knowledge base.
        """
        try:
            knowledge_base.load(recreate=False)
            return "Successfully re-indexed the knowledge base with latest PDFs."
        except Exception as e:
            return f"Error re-indexing: {str(e)}"

    return Agent(
        name="爱尔奎特 (Knowledge)",
        model=OpenAILike(
            id=model_name,
            api_key=api_key,
            base_url=base_url
        ),
        # Add Knowledge Base
        knowledge=knowledge_base,
        # Enable RAG: Add retrieved context to prompt
        add_context=True, 
        search_knowledge=True,
        read_chat_history=True,
        
        tools=[WikiTools(), FileTools(), reindex_vector_db],
        description="You are the Librarian and Knowledge Manager of the Paper Servant system.",
        instructions=[
            "You have access to a Vector Database containing all downloaded papers.",
            "You have two main responsibilities:",
            "1. **Answer General Questions**: Based on the existing knowledge (Vector DB, wiki, paper notes, Q&A history).",
            "2. **Maintain Knowledge Base (Wiki)**: Store definitions of fundamental concepts.",
            
            "**Indexing Instruction**:",
            "If the user asks to 're-index' or 'load' the knowledge base, use the `reindex_vector_db` tool.",
            
            "**Workflow 1: Answering General Questions**",
            "   - If the user asks a question:",
            "     a. The system will AUTOMATICALLY search the Vector DB and provide relevant context from papers.",
            "     b. You should also check `knowledge/wiki/` using `search_wiki` for manually curated concepts.",
            "     c. Synthesize an answer combining the Vector DB context and Wiki info.",
            "     d. **CITATION RULE**: When using information, explicitly state the source (e.g., 'According to the retrieval from paper 1706.03762...' or 'Based on Wiki entry...').",
            "     e. If the answer is not in the knowledge base, use your general LLM knowledge, but prioritize stored information.",
            
            "**Workflow 2: Maintaining the Wiki**",
            "   - If you are asked to explain a specific concept (e.g., 'What is an RNN?') OR if you provide a definition in your answer:",
            "     a. Check if the concept already exists in the wiki using `search_wiki`.",
            "     b. If it does NOT exist or needs updating, use `write_wiki_entry` to save a detailed definition.",
            "     c. **SOURCE MANDATE**: You MUST provide the `source` parameter when writing a wiki entry.",
            "     d. The definition should be clear, concise, and in Markdown format.",
            "     e. Ensure the concept name is used as the filename (handled by the tool).",
            
            "**Language**: Use professional Chinese unless requested otherwise."
        ],
        markdown=True,
    )
