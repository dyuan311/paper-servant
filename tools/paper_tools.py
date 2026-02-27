import os
import arxiv
from pathlib import Path
from typing import List, Optional, Literal
from agno.tools import Toolkit

class PaperTools(Toolkit):
    def __init__(self, download_dir: str = "papers"):
        super().__init__(name="paper_tools")
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.client = arxiv.Client()
        
        self.register(self.search_arxiv)
        self.register(self.download_paper)

    def search_arxiv(self, query: str, max_results: int = 5, sort_by: str = "relevance") -> str:
        """
        Search ArXiv for papers.
        
        Args:
            query (str): Search query.
            max_results (int): Maximum number of results.
            sort_by (str): Sort criterion. Options: "relevance", "submittedDate", "lastUpdatedDate". Defaults to "relevance".
            
        Returns:
            str: JSON string of found papers with metadata.
        """
        sort_criterion = arxiv.SortCriterion.Relevance
        if sort_by == "submittedDate":
            sort_criterion = arxiv.SortCriterion.SubmittedDate
        elif sort_by == "lastUpdatedDate":
            sort_criterion = arxiv.SortCriterion.LastUpdatedDate
            
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion,
            sort_order=arxiv.SortOrder.Descending,
        )
        
        results = []
        for result in self.client.results(search):
            paper = {
                "id": result.get_short_id(),
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "published": result.published.isoformat(),
                "summary": result.summary,
                "pdf_url": result.pdf_url,
                "categories": result.categories,
            }
            results.append(paper)
        
        import json
        return json.dumps(results, indent=2)

    def download_paper(self, paper_id: str) -> str:
        """
        Download a paper from ArXiv by ID.
        
        Args:
            paper_id (str): ArXiv ID of the paper (e.g., "2310.xxxxx").
            
        Returns:
            str: Path to the downloaded PDF or error message.
        """
        try:
            paper = next(self.client.results(arxiv.Search(id_list=[paper_id])))
            filename = f"{paper_id}.pdf"
            file_path = self.download_dir / filename
            
            # Use custom filename to ensure predictability
            paper.download_pdf(dirpath=str(self.download_dir), filename=filename)
            
            return str(file_path)
        except Exception as e:
            return f"Error downloading paper {paper_id}: {str(e)}"
