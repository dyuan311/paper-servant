from typing import Optional
from agno.agent import Agent
from agno.models.openai import OpenAILike
from tools.paper_tools import PaperTools
from tools.metadata_tools import MetadataTools
from tools.citation_tools import CitationTools
import os
from dotenv import load_dotenv

load_dotenv()

def get_paper_fetcher_agent(model_id: str = "gpt-4o"):
    """
    Returns an Agent configured to fetch papers from ArXiv and store metadata.
    """
    
    # Configure OpenAILike model
    # Use environment variables for API key and Base URL
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model_name = os.getenv("LLM_MODEL_ID", model_id)
    
    if not api_key:
        print("⚠️  Warning: LLM_API_KEY not found in environment variables.")

    return Agent(
        name="FetcherAgent", # Internal utility, keeping simple name or changing if desired
        model=OpenAILike(
            id=model_name,
            api_key=api_key,
            base_url=base_url
        ),
        tools=[PaperTools(), MetadataTools(), CitationTools()],
        description="You are a research assistant responsible for fetching papers from ArXiv.",
        instructions=[
            "1. Search for papers on ArXiv based on the user's query.",
            "   - If the user asks for 'latest', 'newest', or 'recent' papers, use `sort_by='submittedDate'` in the `search_arxiv` tool.",
            "   - Otherwise, use the default `sort_by='relevance'`.",
            "2. For EACH relevant paper found:",
            "   a. Download the paper using the `download_paper` tool. It will return the local file path.",
            "   b. Get the citation count using the `get_citation_count` tool with the paper's ArXiv ID.",
            "   c. Construct a metadata object containing: title, authors, published date, summary, pdf_url, categories, citation_count, and the `local_pdf_path` obtained from step 2a.",
            "   d. Save this metadata using the `save_paper_metadata` tool.",
            "3. Finally, list the titles and citation counts of the papers you successfully processed."
        ],
        markdown=True,
    )
