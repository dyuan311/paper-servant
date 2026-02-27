from typing import Optional
from agno.agent import Agent
from agno.models.openai import OpenAILike
from tools.metadata_tools import MetadataTools
from tools.file_tools import FileTools
from tools.pdf_tools import PDFTools
import os
from dotenv import load_dotenv

load_dotenv()

def get_qa_agent(model_id: str = "gpt-4o"):
    """
    Returns an Agent configured to answer questions about specific papers.
    """
    
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL_ID", model_id)
    
    return Agent(
        name="远坂凛 (QA)",
        model=OpenAILike(
            id=model_name,
            api_key=api_key,
            base_url=base_url
        ),
        tools=[MetadataTools(), PDFTools(), FileTools()],
        description="You are an expert AI tutor capable of answering detailed questions about research papers.",
        instructions=[
            "You are responsible for answering user questions about a specific paper.",
            "You have access to the paper's PDF content and its generated notes (if available).",
            
            "**Workflow:**",
            "1. **Identify Context**: The user (or router) will provide the Paper ID or Title.",
            "2. **Gather Information**:",
            "   - Check if a note exists in `papers/notes/` using `read_file` (try `Title.md`).",
            "   - Read the PDF content using `read_pdf` if the note is insufficient or if specific details are needed.",
            "3. **Answer Question**: Provide a clear, accurate, and educational answer based on the paper's content.",
            "   - If the answer is not in the paper, explicitly state that.",
            "   - Use professional Chinese unless requested otherwise.",
            "4. **Record Interaction**: IMMEDIATELY after generating the answer, use `log_qa_session` to save the Q&A pair.",
            "   - `paper_id`: The ID of the paper being discussed.",
            "   - `question`: The user's original question.",
            "   - `answer`: Your generated answer.",
            
            "**Important:** Your job is not finished until you have logged the Q&A session."
        ],
        markdown=True,
    )
