import typer
from typing import Optional
from dotenv import load_dotenv
from agents.paper_fetcher import get_paper_fetcher_agent
from agents.router_agent import get_router_agent
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown

# Load environment variables
load_dotenv()

app = typer.Typer(help="Paper Servent CLI - Your AI Research Assistant")
console = Console()

@app.callback()
def callback():
    """
    Paper Servent CLI - Manage, read, and organize AI papers from ArXiv.
    """
    pass

@app.command()
def fetch(query: str, num_papers: int = 5):
    """
    Search, download, and store metadata for papers from ArXiv.
    """
    agent = get_paper_fetcher_agent()
    console.print(f"[bold green]🔎 Fetching {num_papers} papers for:[/bold green] {query}")
    
    prompt = (
        f"Search for top {num_papers} most relevant papers about '{query}'. "
        "Download them and save their metadata locally."
    )
    
    agent.print_response(prompt, stream=True)

@app.command()
def read_local():
    """
    Interactively select a local paper to read and generate notes.
    """
    import os
    import inquirer
    
    papers_dir = "papers"
    if not os.path.exists(papers_dir):
        console.print("[bold red]Error:[/bold red] 'papers/' directory not found.")
        return

    # Get list of PDF files
    pdf_files = [f for f in os.listdir(papers_dir) if f.endswith(".pdf")]
    
    if not pdf_files:
        console.print("[bold yellow]No PDF papers found in 'papers/' directory.[/bold yellow]")
        return
        
    # Create interactive selection
    questions = [
        inquirer.List('paper',
                      message="Select a paper to read",
                      choices=pdf_files,
                      carousel=True
                     ),
    ]
    
    try:
        answers = inquirer.prompt(questions)
        if not answers:
            return
            
        selected_paper = answers['paper']
        paper_id = selected_paper.replace(".pdf", "")
        
        console.print(f"\n[bold green]Selected:[/bold green] {selected_paper}")
        console.print(f"[bold blue]🤖 苍崎青子 (Router)[/bold blue] Delegating to Reader Agent...")
        
        # Get router agent and force execution
        agent = get_router_agent()
        
        # Construct a direct instruction that skips the router's decision making 
        # and forces it to use the read_paper tool on the exact ID
        prompt = f"Use the `read_paper` tool to read the paper with identifier '{paper_id}'. After reading, if the note is generated successfully, automatically use `open_note` to open it. If `read_paper` says the note already exists, just open it."
        
        agent.print_response(prompt, stream=True)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def playground():
    """
    Launch the AgentOS Playground to serve agents via API.
    """
    import subprocess
    import sys
    
    console.print("[bold green]🚀 Starting AgentOS Playground on http://localhost:7777...[/bold green]")
    try:
        # Run playground.py using the same python interpreter
        subprocess.run([sys.executable, "playground.py"], check=True)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Playground stopped.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error starting playground: {e}[/bold red]")

@app.command()
def chat(
    prompt: Optional[str] = typer.Argument(None, help="The prompt to send to the agent. If omitted, starts interactive mode."),
    max_tool_calls: int = typer.Option(20, "--max-tool-calls", "-m", help="Maximum number of tool calls allowed per turn.")
):
    """
    Interact with the Router Agent. Providing a prompt runs a single command; omitting it starts a continuous chat session.
    """
    # Create agent with tool call limit
    agent = get_router_agent(max_tool_calls=max_tool_calls)
    
    if prompt:
        # Single command mode
        console.print(f"[bold blue]🤖 Paper Servent Router:[/bold blue] {prompt}")
        agent.print_response(prompt, stream=True)
    else:
        # Interactive mode
        console.print(Panel.fit(
            "[bold cyan]Welcome to Paper Servent Interactive Mode![/bold cyan]\n"
            "Type [bold yellow]exit[/bold yellow], [bold yellow]quit[/bold yellow], or [bold yellow]bye[/bold yellow] to end the session.",
            title="Paper Servent",
            border_style="cyan"
        ))
        
        import readline
        
        # ANSI escape codes for bold green
        # \001 and \002 tell readline to ignore these sequences for length calculation
        # This prevents the "backspace deletes prompt" bug on macOS/libedit
        PROMPT_START = "\001\033[1;32m\002"
        PROMPT_END = "\001\033[0m\002"
        
        while True:
            try:
                # Print a newline for spacing before the prompt
                print() 
                user_input = input(f"{PROMPT_START}You{PROMPT_END}: ")
                
                if user_input.lower() in ("exit", "quit", "bye"):
                    console.print("[bold cyan]Goodbye! Happy researching![/bold cyan] 👋")
                    break
                
                if not user_input.strip():
                    continue
                
                console.print(f"\n[bold blue]🤖 苍崎青子 (Router)[/bold blue]")
                # Use standard print_response without custom session_id
                agent.print_response(user_input, stream=True)
                
            except KeyboardInterrupt:
                console.print("\n[bold red]Interrupted. Exiting...[/bold red]")
                break
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
