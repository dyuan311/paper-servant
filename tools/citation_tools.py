import requests
from typing import Optional
from agno.tools import Toolkit

class CitationTools(Toolkit):
    def __init__(self):
        super().__init__(name="citation_tools")
        self.register(self.get_citation_count)

    def get_citation_count(self, arxiv_id: str) -> str:
        """
        Get the citation count for a paper using OpenAlex (primary) or Semantic Scholar (fallback).
        
        Args:
            arxiv_id (str): The ArXiv ID of the paper (e.g., "1706.03762").
            
        Returns:
            str: The citation count as a string, or "Unknown" if not found.
        """
        # Clean ID (remove version suffix like v1, v2 if present)
        clean_id = arxiv_id.split('v')[0]
        
        # 1. Try OpenAlex first (High limits, free)
        try:
            # Using the filter parameter to find the work by ArXiv ID
            # OpenAlex ArXiv IDs are usually stored without version, e.g., "https://arxiv.org/abs/2310.12345"
            # The API accepts the short ID in the filter as well: ids.arxiv:2310.12345
            openalex_url = f"https://api.openalex.org/works?filter=ids.arxiv:{clean_id}"
            
            # Polite pool: adding an email header is recommended but not strictly required for low volume
            headers = {
                "User-Agent": "PaperServent/1.0 (mailto:example@example.com)" 
            }
            
            response = requests.get(openalex_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                if results:
                    # Taking the first result (should be unique for ID)
                    count = results[0].get('cited_by_count')
                    if count is not None:
                        return str(count)
        except Exception as e:
            # Log error internally or just pass to fallback
            print(f"OpenAlex fetch failed for {clean_id}: {e}")
            pass

        # 2. Fallback to Semantic Scholar
        url = f"https://api.semanticscholar.org/graph/v1/paper/ARXIV:{clean_id}?fields=citationCount"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 404:
                return "Unknown (Paper not found)"
            
            response.raise_for_status()
            data = response.json()
            count = data.get('citationCount')
            
            if count is not None:
                return str(count)
            else:
                return "Unknown"
                
        except Exception as e:
            return f"Error fetching citation count: {str(e)}"
