import os
from pathlib import Path
from agno.tools import Toolkit

class WikiTools(Toolkit):
    def __init__(self, wiki_dir: str = "knowledge/wiki"):
        super().__init__(name="wiki_tools")
        self.wiki_dir = Path(wiki_dir)
        self.wiki_dir.mkdir(parents=True, exist_ok=True)
        
        self.register(self.write_wiki_entry)
        self.register(self.search_wiki)
        self.register(self.list_wiki_entries)
        self.register(self.read_wiki_entry)

    def write_wiki_entry(self, concept: str, definition: str, source: str = "AI Knowledge") -> str:
        """
        Create or update a wiki entry for a specific concept.
        
        Args:
            concept (str): The name of the concept (e.g., "RNN", "Transformer").
            definition (str): The detailed explanation/definition in Markdown format.
            source (str): The source of the information (e.g., paper ID "1706.03762", "General AI Knowledge", or user input).
            
        Returns:
            str: Success message.
        """
        try:
            # Sanitize filename
            safe_concept = "".join(c for c in concept if c.isalnum() or c in (' ', '_', '-')).strip()
            filename = f"{safe_concept}.md"
            file_path = self.wiki_dir / filename
            
            # Format content with metadata header
            content = f"# {concept}\n\n> Source: {source}\n\n{definition}"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            return f"Wiki entry for '{concept}' saved to {file_path} (Source: {source})"
        except Exception as e:
            return f"Error writing wiki entry: {str(e)}"

    def search_wiki(self, query: str) -> str:
        """
        Search for a concept in the wiki knowledge base.
        
        Args:
            query (str): The concept to search for.
            
        Returns:
            str: The content of the wiki entry if found, or a list of similar entries.
        """
        try:
            # Direct match check
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '_', '-')).strip()
            direct_file = self.wiki_dir / f"{safe_query}.md"
            
            if direct_file.exists():
                with open(direct_file, "r", encoding="utf-8") as f:
                    return f"Found exact match:\n\n{f.read()}"
            
            # Fuzzy search (simple substring match in filenames)
            matches = []
            for file in self.wiki_dir.glob("*.md"):
                if query.lower() in file.stem.lower():
                    matches.append(file.stem)
            
            if matches:
                return f"No exact match for '{query}'. Found similar entries: {', '.join(matches)}. Use `read_wiki_entry` to read one."
            else:
                return f"No wiki entries found matching '{query}'."
                
        except Exception as e:
            return f"Error searching wiki: {str(e)}"

    def read_wiki_entry(self, concept: str) -> str:
        """
        Read the content of a specific wiki entry.
        
        Args:
            concept (str): The concept name.
            
        Returns:
            str: Content or error.
        """
        safe_concept = "".join(c for c in concept if c.isalnum() or c in (' ', '_', '-')).strip()
        file_path = self.wiki_dir / f"{safe_concept}.md"
        
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return f"Wiki entry for '{concept}' not found."

    def list_wiki_entries(self) -> str:
        """
        List all available concepts in the wiki.
        
        Returns:
            str: List of concepts.
        """
        entries = [f.stem for f in self.wiki_dir.glob("*.md")]
        return f"Available Wiki Entries: {', '.join(entries)}" if entries else "Wiki is empty."
