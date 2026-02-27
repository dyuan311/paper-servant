from typing import Optional, List
from agno.agent import Agent
from agno.models.openai import OpenAILike
# Try to import InMemoryDb as suggested by user
try:
    from agno.db.in_memory import InMemoryDb
except ImportError:
    # Fallback or maybe it's in a different path, but let's assume user is right
    # If this fails, we might need another fix, but let's try to follow instructions.
    pass

from agents.paper_fetcher import get_paper_fetcher_agent
from agents.organizer_agent import get_organizer_agent
from agents.reader_agent import get_reader_agent
from agents.qa_agent import get_qa_agent
from agents.knowledge_agent import get_knowledge_agent
from tools.system_tools import SystemTools
from tools.metadata_tools import MetadataTools
import os
from dotenv import load_dotenv

load_dotenv()

def get_router_agent(model_id: str = "gpt-4o", max_tool_calls: Optional[int] = None):
    """
    Returns the Router Agent which delegates tasks to other specialized agents.
    
    Args:
        model_id (str): The ID of the LLM model to use.
        max_tool_calls (Optional[int]): The maximum number of tool calls allowed per run. 
                                      Set this to prevent infinite loops (e.g., 10). 
                                      If None, uses default behavior (usually unlimited or framework default).
    """
    
    # Configure OpenAILike model
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL_ID", model_id)
    
    # Initialize specialized agents
    fetcher_agent = get_paper_fetcher_agent(model_id=model_name)
    organizer_agent = get_organizer_agent(model_id=model_name)
    reader_agent = get_reader_agent(model_id=model_name)
    qa_agent = get_qa_agent(model_id=model_name)
    knowledge_agent = get_knowledge_agent(model_id=model_name)
    
    # Initialize tools
    system_tools = SystemTools()
    metadata_tools = MetadataTools()
    
    # Create a team of agents or use tools to delegate

    def fetch_papers(query: str, num_papers: int = 5, sort_by: str = "relevance") -> str:
        """
        Use this tool to search, download, and store metadata for papers from ArXiv.
        
        Args:
            query (str): The topic or keywords to search for (e.g., "Agentic AI", "LLM reasoning").
            num_papers (int): The number of papers to fetch. Defaults to 5.
            sort_by (str): Sort criterion. Options: "relevance" (default), "submittedDate" (for latest/newest), "lastUpdatedDate".
            
        Returns:
            str: A summary of the action taken.
        """
        print(f"DEBUG: Router delegating to Fetcher Agent: query='{query}', num={num_papers}, sort_by='{sort_by}'")
        
        sort_instruction = ""
        if sort_by == "submittedDate":
            sort_instruction = "Sort the results by submittedDate (latest first)."
        elif sort_by == "lastUpdatedDate":
            sort_instruction = "Sort the results by lastUpdatedDate."
            
        response = fetcher_agent.run(
            f"Search for top {num_papers} most relevant papers about '{query}'. {sort_instruction} "
            "Download them, get citation counts, and save their metadata locally. "
            "Finally, list the titles and citation counts."
        )
        return response.content

    def organize_papers() -> str:
        """
        Use this tool to categorize and organize all downloaded papers into folders based on their research direction.
        It creates symbolic links in 'papers/categorized/' without moving the original files.
        
        Returns:
            str: A summary of the organization process.
        """
        print(f"DEBUG: Router delegating to Organizer Agent")
        response = organizer_agent.run("Organize all papers into categories.")
        return response.content

    def read_paper(paper_identifier: str) -> str:
        """
        Use this tool to read a specific paper and generate a detailed reading note.
        
        Args:
            paper_identifier (str): The identifier of the paper (e.g., ArXiv ID "1706.03762" or Title "Attention Is All You Need").
            
        Returns:
            str: The generated reading note or a summary of the reading process.
        """
        print(f"DEBUG: Router delegating to Reader Agent: paper='{paper_identifier}'")
        response = reader_agent.run(f"Read the paper identified by '{paper_identifier}' and generate a detailed note.")
        
        # Explicitly remind the Router about the context
        return (f"Reading process for paper '{paper_identifier}' completed. "
                f"Reader Agent output:\n{response.content}\n\n"
                f"SYSTEM REMINDER: The current active paper is '{paper_identifier}'. "
                f"If the user asks 'open the note' or 'what is it about' next, refer to '{paper_identifier}'.")

    def ask_paper_question(paper_identifier: str, question: str) -> str:
        """
        Use this tool to ask a question about a specific paper.
        
        Args:
            paper_identifier (str): The identifier of the paper (e.g., ArXiv ID "1706.03762" or Title).
            question (str): The question about the paper.
            
        Returns:
            str: The answer to the question.
        """
        print(f"DEBUG: Router delegating to QA Agent: paper='{paper_identifier}', question='{question}'")
        response = qa_agent.run(f"For paper '{paper_identifier}', answer this question: {question}")
        return response.content

    def ask_general_question(question: str) -> str:
        """
        Use this tool to ask a general question about AI concepts or knowledge, NOT specific to a single paper.
        
        Args:
            question (str): The general question (e.g., "What is RNN?", "Explain Transformer architecture").
            
        Returns:
            str: The answer or definition.
        """
        print(f"DEBUG: Router delegating to Knowledge Agent: question='{question}'")
        response = knowledge_agent.run(f"Answer this general question using stored knowledge: {question}")
        return response.content

    def save_concept_to_wiki(concept: str, definition: str, source: str = "User Input") -> str:
        """
        Use this tool to explicitly save a concept definition to the wiki knowledge base.
        
        Args:
            concept (str): The concept name (e.g., "Transformer").
            definition (str): The detailed definition/explanation.
            source (str): The origin of this knowledge (default: "User Input").
            
        Returns:
            str: Success message.
        """
        print(f"DEBUG: Router delegating to Knowledge Agent (Wiki update): concept='{concept}', source='{source}'")
        response = knowledge_agent.run(f"Save the following definition to the wiki for concept '{concept}' (Source: {source}):\n\n{definition}")
        return response.content
        
    def check_local_paper(query: str) -> str:
        """
        Use this tool to check if a paper is already downloaded locally.
        
        Args:
            query (str): The search term (e.g., paper title, ArXiv ID).
            
        Returns:
            str: JSON list of matching papers from metadata, OR a list of filenames if metadata search fails.
        """
        # This function is kept for backward compatibility but the main logic is now handled by the UI tool
        # 'list_local_papers' which is more robust.
        print(f"DEBUG: Router checking local papers: query='{query}'")
        return metadata_tools.find_paper(query)

    def list_local_papers() -> str:
        """
        Use this tool when the user wants to see what papers are available locally, or when a specific paper cannot be found.
        It lists all PDF files in the 'papers/' directory.
        
        Returns:
            str: A formatted list of all local PDF files.
        """
        print(f"DEBUG: Router listing all local papers")
        try:
            papers_dir = "papers"
            if not os.path.exists(papers_dir):
                return "Error: papers directory not found."
            
            files = [f for f in os.listdir(papers_dir) if f.endswith(".pdf")]
            
            if not files:
                return "No PDF papers found in local directory."
                
            file_list_str = "\n".join([f"- {f}" for f in files])
            return (f"Here are the PDF files found in '{papers_dir}':\n\n{file_list_str}\n\n"
                    "INSTRUCTION: Ask the user which one they would like to read or open.")
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def open_note(paper_identifier: str = None) -> str:
        """
        Use this tool to open the reading note of a specific local paper.
        
        Args:
            paper_identifier (str, optional): The identifier of the paper (e.g., ArXiv ID or Title).
                                            If the user says "the paper" or "the note" without specifying,
                                            you MUST infer this from the conversation history (e.g., the last read paper).
                                            If you cannot infer it, ask the user.
            
        Returns:
            str: Success message or a list of existing notes if not found.
        """
        if not paper_identifier:
            return "Error: No paper identifier provided. Please specify which paper's note you want to open."
            
        print(f"DEBUG: Router opening note locally: paper='{paper_identifier}'")
        
        # 1. First try direct open
        result = system_tools.open_note(paper_identifier)
        if not result.startswith("Error: No reading note found") and not result.startswith("Error: Notes directory does not exist"):
             return result
            
        # 2. If not found, list all files in papers/notes/ directory
        try:
            notes_dir = "papers/notes"
            if not os.path.exists(notes_dir):
                return "Error: papers/notes directory not found. Please create notes first using read_paper."
                
            files = [f for f in os.listdir(notes_dir) if f.endswith(".md")]
            
            # Return raw file list for LLM to process
            return f"Note not found via direct search. Here is the list of ALL note files in '{notes_dir}':\n{files}\n\nPlease check this list carefully. If you find a file that matches '{paper_identifier}' (e.g. partial ID match), use that filename as the paper_identifier to retry opening."
        except Exception as e:
            return f"Error listing notes: {str(e)}"

    def open_pdf(paper_identifier: str) -> str:
        """
        Use this tool to open a PDF file in the system's default viewer.
        
        Args:
            paper_identifier (str): The identifier of the paper (e.g., ArXiv ID "1706.03762" or filename).
            
        Returns:
            str: Success message.
        """
        print(f"DEBUG: Router opening PDF locally: paper='{paper_identifier}'")
        return system_tools.open_pdf(paper_identifier)

    # Note: For Agno framework, we don't need explicit DB setup for simple in-memory history
    # The Agent class handles history internally if add_history_to_context is True.
    # We will rely on the default in-memory behavior of Agno Agent.
    
    # Prepare db if available
    db_instance = None
    try:
        db_instance = InMemoryDb()
    except NameError:
        pass



    def reindex_knowledge_base() -> str:
        """
        Use this tool to manually trigger a re-indexing of the Knowledge Base (Vector DB).
        This should be done after downloading new papers to make them searchable.
        
        Returns:
            str: Status message.
        """
        print(f"DEBUG: Router triggering Knowledge Base re-indexing")
        # We need to get the knowledge agent and call load() on its knowledge base
        # Since we don't have direct access to the 'knowledge_base' object here, 
        # we can delegate this task to the Knowledge Agent via a special instruction.
        
        response = knowledge_agent.run("Please re-index the knowledge base now. Load all documents from the papers directory into the vector database.")
        return response.content

    agent_kwargs = {
        "name": "苍崎青子 (Router)",
        "model": OpenAILike(
            id=model_name,
            api_key=api_key,
            base_url=base_url
        ),
        "add_history_to_context": True,
        "num_history_runs": 5,
        "tools": [fetch_papers, organize_papers, read_paper, ask_paper_question, ask_general_question, save_concept_to_wiki, open_pdf, check_local_paper, list_local_papers, open_note, reindex_knowledge_base],
        "description": "You are the main Router Agent for the Paper Servent system.",
        "instructions": [
            "You are the interface between the user and the specialized agents.",
            "Your goal is to understand the user's intent and route the request to the appropriate tool.",
            "Currently, you have access to the following tools:",
            " - `fetch_papers`: Search/download papers.",
            " - `organize_papers`: Organize papers into categories.",
            " - `read_paper`: Generate a detailed reading note for a specific paper.",
            " - `ask_paper_question`: Ask a question about a SPECIFIC paper. Use this if the user mentions 'in this paper', 'paper X', or implies a specific context.",
            " - `ask_general_question`: Ask a general knowledge question (e.g., 'What is X?', 'Explain Y'). Use this for definitions or broad topics.",
            " - `save_concept_to_wiki`: Use this if the user explicitly asks to save a definition to the knowledge base.",
            " - `open_pdf`: Open a PDF file locally using the system viewer. Trigger this when user says 'open', 'show', or 'view' a paper.",
            " - `check_local_paper`: Check if a paper is already downloaded locally. Use this when the user asks 'Do I have paper X?' or 'Find paper X locally'.",
            " - `list_local_papers`: List ALL local PDF papers. Use this when the user asks 'What papers do I have?', 'Show local papers', or when a specific search fails.",
            " - `open_note`: Open the reading note of a specific local paper. Use this when the user says 'open note', 'show summary', or 'view note'.",
            
            "**Context Awareness & Memory**:",
            " - **CRITICAL**: Always keep track of the last paper ID mentioned or processed (e.g., in `read_paper` or `fetch_papers`).",
            " - If the user asks a follow-up question like 'What is this paper about?', 'How does it work?', 'Explain the method', or 'Open the note', **assume they are referring to the last processed paper**.",
            " - In such cases, DO NOT ask 'Which paper?'. Instead, use the appropriate tool (`ask_paper_question` or `open_note`) with the last paper ID you processed.",
            " - If you just ran `read_paper`, the output contains the abstract. You can use that information to answer general summary questions directly, or use `ask_paper_question` for more specific details.",
            
            " - If the user asks for a definition (e.g., 'What is an RNN?'), use `ask_general_question`. The Knowledge Agent will handle saving it if necessary.",
            " - If the user wants to 'open' or 'view' a paper, use `open_pdf`. If they want to see the **note**, use `open_note`.",
            
            "**Strict Delegation Rule**:",
            " - You are a **Router**, not a knowledge base. You MUST NOT answer user questions directly using your internal training data.",
            " - For ANY question about a paper's content, method, or results, you MUST use `ask_paper_question`.",
            " - For ANY general question about AI concepts, definitions, or history, you MUST use `ask_general_question`.",
            " - Only use your own text generation to summarize the output of tools or to clarify user intent.",

            "Always clarify the query ONLY if the context is truly ambiguous.",
            "After the tool completes, summarize the result for the user."
        ],
        "markdown": True,
    }
    
    if db_instance:
        agent_kwargs["db"] = db_instance
        
    if max_tool_calls is not None:
        agent_kwargs["tool_call_limit"] = max_tool_calls
    
    return Agent(**agent_kwargs)
