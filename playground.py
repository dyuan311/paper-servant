from agno.os import AgentOS
from agents.router_agent import get_router_agent
from agents.paper_fetcher import get_paper_fetcher_agent
from agents.organizer_agent import get_organizer_agent
from agents.reader_agent import get_reader_agent
from agents.qa_agent import get_qa_agent
from agents.knowledge_agent import get_knowledge_agent
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Agents
router = get_router_agent()
fetcher = get_paper_fetcher_agent()
organizer = get_organizer_agent()
reader = get_reader_agent()
qa = get_qa_agent()
knowledge = get_knowledge_agent()

# Create AgentOS
# In Agno v2, Playground is deprecated and replaced by AgentOS
agent_os = AgentOS(
    description="Paper Servent AgentOS",
    agents=[router, fetcher, organizer, reader, qa, knowledge]
)

# Get the FastAPI app
app = agent_os.get_app()

if __name__ == "__main__":
    # Serve the app using agent_os.serve
    # Default port is 7777
    agent_os.serve(app="playground:app", reload=True)
