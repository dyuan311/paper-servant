import json
from pathlib import Path
from typing import List, Dict, Any
from agno.tools import Toolkit

class MetadataTools(Toolkit):
    def __init__(self, metadata_file: str = "papers/metadata.json"):
        super().__init__(name="metadata_tools")
        self.metadata_file = Path(metadata_file)
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.metadata_file.exists():
            with open(self.metadata_file, "w") as f:
                json.dump([], f)
        
        # Register tools
        self.register(self.save_paper_metadata)
        self.register(self.get_all_papers)
        self.register(self.find_paper)

    def find_paper(self, query: str) -> str:
        """
        Search for papers in the local metadata by title or ID.
        
        Args:
            query (str): The search term (e.g., "Transformer", "1706.03762").
            
        Returns:
            str: JSON string of matching papers.
        """
        try:
            if not self.metadata_file.exists():
                return "[]"
                
            with open(self.metadata_file, "r") as f:
                papers = json.load(f)
                
            query_lower = query.lower()
            matches = []
            
            for item in papers:
                # The structure is list of dicts: [{"id": {data}}, {"id": {data}}]
                for p_id, p_info in item.items():
                    title = p_info.get("title", "").lower()
                    paper_id_str = str(p_id).lower()
                    
                    # Fuzzy match: 
                    # 1. query is part of title (e.g. "Transformer" in "Attention Is All You Need")
                    # 2. query is part of ID (e.g. "18397" in "2602.18397v1")
                    # 3. ID is part of query (e.g. "2602.18397" in "2602.18397v1")
                    # 4. Handle versioning: ignore 'v1', 'v2' suffix for matching if needed
                    
                    # Strip version from both sides for cleaner comparison
                    pid_clean = paper_id_str.split('v')[0] if 'v' in paper_id_str else paper_id_str
                    q_clean = query_lower.split('v')[0] if 'v' in query_lower else query_lower
                    
                    if (query_lower in title) or \
                       (query_lower in paper_id_str) or \
                       (paper_id_str in query_lower) or \
                       (q_clean in pid_clean) or \
                       (pid_clean in q_clean):
                        
                        # Add ID to the info for clarity
                        match_data = p_info.copy()
                        match_data["id"] = p_id
                        matches.append(match_data)
                    
            return json.dumps(matches, indent=2)
        except Exception as e:
            return f"Error searching papers: {str(e)}"
    def save_paper_metadata(self, paper_data: Dict[str, Any]) -> str:
        """
        Save or update paper metadata in the local JSON storage.
        
        Args:
            paper_data (dict): Dictionary containing paper metadata (title, authors, summary, pdf_url, etc.)
        
        Returns:
            str: Success message.
        """
        try:
            with open(self.metadata_file, "r") as f:
                current_data = json.load(f)
            
            # Check if paper already exists (by id or title)
            # Assuming 'id' is available, otherwise use 'title'
            paper_id = paper_data.get("id") or paper_data.get("entry_id")
            
            existing_index = -1
            if paper_id:
                for i, paper in enumerate(current_data):
                    if paper.get("id") == paper_id or paper.get("entry_id") == paper_id:
                        existing_index = i
                        break
            
            if existing_index >= 0:
                current_data[existing_index].update(paper_data)
                action = "Updated"
            else:
                current_data.append(paper_data)
                action = "Added"
            
            with open(self.metadata_file, "w") as f:
                json.dump(current_data, f, indent=4)
                
            return f"{action} metadata for paper: {paper_data.get('title', 'Unknown')}"
        except Exception as e:
            return f"Error saving metadata: {str(e)}"

    def get_all_papers(self) -> str:
        """
        Retrieve all stored paper metadata.
        
        Returns:
            str: JSON string of all papers.
        """
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return f.read()
        return "[]"
