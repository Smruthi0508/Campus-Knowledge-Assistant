
from pathlib import Path
import sys

from mcp.server.fastmcp import FastMCP

# Add the project root to Python's search path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import our existing RAG retriever
from rag.retriever import retrieve_information

# Create the MCP server
mcp = FastMCP("Campus Knowledge Assistant")


# Create one MCP tool
@mcp.tool()
def search_campus_knowledge(question: str) -> str:
    """
    Search campus documents and return relevant information
    along with the source filename.
    """

    results = retrieve_information(question)

    if not results:
        return "No matching information found."

    response = "Matching Campus Information:\n\n"

    for result in results:
        response += f"Information: {result['text']}\n"
        response += f"Source: {result['source']}\n\n"

    return response


# Start the MCP server using standard input/output
if __name__ == "__main__":
    mcp.run(transport="stdio")
