from typing import Optional, List, Dict, Any
from agno.agent import Agent
from agno.models.openai import OpenAILike
from tools.metadata_tools import MetadataTools
from tools.file_tools import FileTools
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_organizer_agent(model_id: str = "gpt-4o"):
    """
    Returns an Agent configured to organize papers into categories.
    """
    
    # Configure OpenAILike model
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL_ID", model_id)
    
    return Agent(
        name="OrganizerAgent", # Internal utility
        model=OpenAILike(
            id=model_name,
            api_key=api_key,
            base_url=base_url
        ),
        tools=[MetadataTools(), FileTools()],
        description="You are an expert librarian responsible for organizing AI research papers.",
        instructions=[
            "1. Retrieve all paper metadata using the `get_all_papers` tool.",
            "2. Analyze the metadata structure carefully. It is a list of dictionaries where each dictionary contains a single key (the paper ID) mapping to the paper details.",
            "3. For EACH paper found in the metadata:",
            "   a. Extract the Paper ID (the key), Title, and Summary.",
            "   b. Classify the paper into exactly ONE of the following categories based on its content:",
            "      - 'Large Language Models' (LLMs, NLP, Prompt Engineering, Text Generation)",
            "      - 'Computer Vision' (Image Classification, Detection, Segmentation, Generation)",
            "      - 'Multimodal AI' (Vision-Language, Audio-Video, Cross-modal)",
            "      - 'Reinforcement Learning' (RL, Bandits, Decision Making)",
            "      - 'Robotics' (Control, Manipulation, Navigation, Sim-to-Real)",
            "      - 'AI Theory' (Optimization, Learning Theory, Architecture Design, Fundamentals)",
            "      - 'AI Applications' (Science, Medicine, Finance, Social Science, HC)",
            "      - 'Other' (If none of the above fits well)",
            "   c. Use the `categorize_paper` tool to create a symbolic link.",
            "      - `paper_id`: The ID extracted from the metadata key (e.g., '1706.03762v7').",
            "      - `category`: The chosen category name.",
            "      - `title`: The paper title (sanitized automatically by the tool).",
            "4. Provide a summary of the categorization results, listing which papers went into which category.",
            "5. Do NOT modify the original files or delete anything. The `categorize_paper` tool handles symbolic links safely."
        ],
        markdown=True,
    )
