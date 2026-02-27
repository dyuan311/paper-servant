import os
import re
from pathlib import Path
from agno.tools import Toolkit
import datetime

class FileTools(Toolkit):
    def __init__(self, base_dir: str = "papers"):
        super().__init__(name="file_tools")
        self.base_dir = Path(base_dir)
        self.categorized_dir = self.base_dir / "categorized"
        self.notes_dir = self.base_dir / "notes"
        
        # New directories for Q&A history
        self.qa_history_dir = Path("knowledge/qa_history")
        
        self.categorized_dir.mkdir(parents=True, exist_ok=True)
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.qa_history_dir.mkdir(parents=True, exist_ok=True)
        
        self.register(self.categorize_paper)
        self.register(self.save_note)
        self.register(self.read_file)
        self.register(self.log_qa_session)

    def categorize_paper(self, paper_id: str, category: str, title: str = "") -> str:
        """
        Creates a symbolic link for a paper in a categorized subdirectory.
        Does NOT move the original file, preserving the flat structure in 'papers/'.
        
        Args:
            paper_id (str): The ID of the paper (filename without extension, e.g., '1706.03762v7').
            category (str): The target category (e.g., 'LLM', 'CV').
            title (str): The paper title (used for the link name). If empty, uses ID.
            
        Returns:
            str: Result message.
        """
        try:
            # Source file (in papers/)
            # Handle potential pdf extension in input
            if paper_id.endswith(".pdf"):
                paper_id = paper_id[:-4]
                
            src_file = self.base_dir / f"{paper_id}.pdf"
            
            if not src_file.exists():
                return f"Error: Source file {src_file} does not exist."
            
            # Target directory
            # Sanitize category name
            safe_category = "".join(c for c in category if c.isalnum() or c in (' ', '_', '-')).strip()
            category_dir = self.categorized_dir / safe_category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Link name
            if title:
                # Sanitize title for filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()
                # Limit length
                safe_title = safe_title[:100]
                link_name = f"{safe_title}.pdf"
            else:
                link_name = f"{paper_id}.pdf"
                
            link_path = category_dir / link_name
            
            # Remove existing link if needed
            if link_path.exists() or link_path.is_symlink():
                link_path.unlink()
                
            # Create relative symlink
            # link_path -> src_file
            # From link_path (papers/categorized/Cat/file.pdf) to src_file (papers/file.pdf)
            # Path is ../../file.pdf
            
            # Using os.path.relpath to be safe
            relative_src = os.path.relpath(src_file, category_dir)
            os.symlink(relative_src, link_path)
            
            return f"Categorized '{paper_id}' into '{safe_category}' as '{link_name}'"
            
        except Exception as e:
            return f"Error categorizing paper {paper_id}: {str(e)}"

    def save_note(self, filename: str, content: str) -> str:
        """
        Save a markdown note to the papers/notes directory.
        
        Args:
            filename (str): The filename for the note (e.g., "Attention_Is_All_You_Need.md").
            content (str): The markdown content of the note.
            
        Returns:
            str: The full path where the note was saved.
        """
        try:
            if not filename.endswith(".md"):
                filename += ".md"
                
            # Sanitize filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '_', '-', '.')).strip()
            file_path = self.notes_dir / safe_filename
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            return str(file_path)
        except Exception as e:
            return f"Error saving note: {str(e)}"

    def read_file(self, file_path: str) -> str:
        """
        Read content from a text/markdown file.
        
        Args:
            file_path (str): The absolute or relative path to the file.
            
        Returns:
            str: File content or error message.
        """
        path = Path(file_path)
        if not path.exists():
            return f"Error: File {file_path} not found."
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def log_qa_session(self, paper_id: str, question: str, answer: str) -> str:
        """
        Append a Q&A interaction to the history log.
        
        Args:
            paper_id (str): The ID of the paper being discussed (or "General" for general QA).
            question (str): The user's question.
            answer (str): The agent's answer.
            
        Returns:
            str: Success message.
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
            # Create a daily log file or a per-paper log file?
            # User requirement: "Complete Q&A must be recorded".
            # Let's organize by paper_id to keep context together.
            
            safe_id = "".join(c for c in paper_id if c.isalnum() or c in ('_', '-'))
            filename = f"QA_{safe_id}.md"
            file_path = self.qa_history_dir / filename
            
            mode = "a" if file_path.exists() else "w"
            
            with open(file_path, mode, encoding="utf-8") as f:
                entry = f"\n\n## [{datetime.datetime.now().strftime('%H:%M:%S')}] Question\n{question}\n\n### Answer\n{answer}\n\n---\n"
                f.write(entry)
                
            return f"Logged Q&A to {file_path}"
        except Exception as e:
            return f"Error logging Q&A: {str(e)}"
