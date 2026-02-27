import os
import subprocess
import sys
from pathlib import Path
from agno.tools import Toolkit

class SystemTools(Toolkit):
    def __init__(self, base_dir: str = "papers"):
        super().__init__(name="system_tools")
        self.base_dir = Path(base_dir)
        
        self.register(self.open_pdf)
        self.register(self.open_note)

    def open_note(self, paper_identifier: str) -> str:
        """
        Open the reading note for a specific paper.
        
        Args:
            paper_identifier (str): The identifier of the paper (e.g., ArXiv ID "1706.03762" or Title).
            
        Returns:
            str: Success or error message.
        """
        try:
            # Notes are stored in papers/notes/
            notes_dir = self.base_dir / "notes"
            if not notes_dir.exists():
                return "Error: Notes directory does not exist."
                
            # Try to find the file
            # Common patterns: {id}_{title}.md, or just {title}.md
            # We search for any markdown file containing the identifier as a substring
            
            matches = list(notes_dir.rglob(f"*{paper_identifier}*.md"))
            
            if not matches:
                return f"Error: No reading note found for '{paper_identifier}'."
            
            # Prefer the shortest match or the one that starts with the ID if possible
            # For now, just pick the first one
            file_path = matches[0]
            
            # Determine OS and open command
            # User requested Chrome for markdown files
            if sys.platform == "darwin":  # macOS
                # Use 'open -a "Google Chrome" file_path'
                try:
                    subprocess.run(["open", "-a", "Google Chrome", str(file_path)], check=True)
                except subprocess.CalledProcessError:
                    # Fallback to default open if Chrome fails
                    subprocess.run(["open", str(file_path)], check=True)
                    return f"Chrome not found, opened '{file_path.name}' with default app."
            elif sys.platform == "win32": # Windows
                # Try to find Chrome path or use 'start chrome file_path'
                # 'start' is a shell command, so use shell=True
                try:
                    subprocess.run(["start", "chrome", str(file_path)], shell=True, check=True)
                except Exception:
                    os.startfile(str(file_path))
            else: # Linux
                # Try google-chrome or google-chrome-stable
                try:
                    subprocess.run(["google-chrome", str(file_path)], check=True)
                except FileNotFoundError:
                    subprocess.run(["xdg-open", str(file_path)], check=True)
                
            return f"Opened note '{file_path.name}' in Chrome."
            
        except Exception as e:
            return f"Error opening note: {str(e)}"

    def open_pdf(self, paper_identifier: str) -> str:
        """
        Open a PDF file using the system's default PDF viewer.
        
        Args:
            paper_identifier (str): The identifier of the paper (e.g., ArXiv ID "1706.03762" or filename).
            
        Returns:
            str: Success or error message.
        """
        try:
            # Handle .pdf extension
            if not paper_identifier.endswith(".pdf"):
                # Try adding .pdf
                paper_id_with_ext = f"{paper_identifier}.pdf"
            else:
                paper_id_with_ext = paper_identifier
                paper_identifier = paper_identifier[:-4] # Remove extension for searching if needed

            # 1. Try direct path in papers/
            file_path = self.base_dir / paper_id_with_ext
            
            # 2. If not found, search recursively
            if not file_path.exists():
                # Use recursive glob with wildcards on both sides to support partial ID matches
                # e.g., "18397" will match "2602.18397v1.pdf"
                found_files = list(self.base_dir.rglob(f"*{paper_identifier}*.pdf"))
                if found_files:
                    file_path = found_files[0]
                else:
                    return f"Error: PDF for '{paper_identifier}' not found."

            # Determine OS and open command
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(file_path)], check=True)
            elif sys.platform == "win32": # Windows
                os.startfile(str(file_path))
            else: # Linux
                subprocess.run(["xdg-open", str(file_path)], check=True)
                
            return f"Opened '{file_path.name}' in system viewer."
            
        except Exception as e:
            return f"Error opening PDF: {str(e)}"
