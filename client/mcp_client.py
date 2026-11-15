
import asyncio
import sys
from pathlib import Path

import ollama

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Find the project directory
BASE_DIR = Path(__file__).resolve().parent.parent


# Configure the MCP server
server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(BASE_DIR / "server" / "mcp_server.py")]
)


async def main():

    # Connect to the MCP server
    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Initialize MCP connection
            await session.initialize()

            print("Connected to Campus Knowledge MCP Server!")

            # Get question from user
            question = input("\nAsk your campus question: ")

            # Call the MCP tool
            result = await session.call_tool(
                "search_campus_knowledge",
                arguments={"question": question}
            )

            # Extract retrieved information
            evidence = "\n".join(
                item.text
                for item in result.content
                if hasattr(item, "text")
            )

            print("\nRetrieved Information:")
            print(evidence)

            # Stop if no information is available
            if not evidence or "No matching information found." in evidence:
                print("\nAnswer: Sorry, I couldn't find this information in the campus documents.")
                return

            # Send retrieved information to Ollama
            response = ollama.chat(
                model="qwen3.5:4b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Campus Knowledge Assistant. "
                            "Answer using ONLY the provided campus information. "
                            "Do not make up or assume facts. "
                            "Mention the source filename in your answer. "
                            "If the information is insufficient, say so."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Question: {question}\n\n"
                            f"Campus Information:\n{evidence}"
                        )
                    }
                ]
            )

            # Display final answer
            print("\nFinal Answer:")
            print(response["message"]["content"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCampus Assistant stopped.")
