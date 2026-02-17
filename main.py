from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

import os
import asyncio
import requests

if __name__ == "__main__":

    def read_repository(repository_url: str, branch: str = "main") -> dict:

        parts = repository_url.rstrip("/").split("/")
        if len(parts) < 2:
            raise ValueError("Incorrect repo format")
        owner, repo = parts[-2], parts[-1]

        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        response = requests.get(api_url)
        if response.status_code != 200:
            raise Exception(f"Can not get file tree: {response.text}")

        tree = response.json().get("tree", [])
        repo_content = {}

        allowed_ext = {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".c",
            ".cpp",
            ".go",
            ".rb",
            ".php",
            ".cs",
            ".swift",
            ".rs",
            ".html",
            ".css",
            ".json",
            ".yml",
            ".yaml",
            ".md",
        }

        for item in tree:
            if item["type"] == "blob":
                if not any(item["path"].lower().endswith(ext) for ext in allowed_ext):
                    continue

                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{item['path']}"
                file_resp = requests.get(raw_url)
                if file_resp.status_code == 200:
                    repo_content[item["path"]] = file_resp.text
                else:
                    repo_content[item["path"]] = (
                        f"Can not read file: {file_resp.status_code}"
                    )

        return repo_content

    def write_text_to_file(text: str, file_name: str = "doc_assets"):
        with open(f"{file_name}", "w", encoding="utf-8") as f:
            f.write(text)

    def read_file(file_path: str = "doc_assets.txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return f"File {file_path} not found."
        except Exception as e:
            return f"Error while reading {file_path}: {e}"

    async def main():
        model_client = OpenAIChatCompletionClient(
            model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"], temperature=0.2
        )

        reader = AssistantAgent(
            name="reader",
            description=(
                "Repository Reader Agent. "
                "Task: read each file in the repository and produce a dictionary, "
                "which will be passed to the Writer Agent for documentation creation."
            ),
            model_client=model_client,
            system_message=(
                "You read the repository and provide file contents to another agent."
            ),
            tools=[read_repository],
        )

        writer = AssistantAgent(
            name="writer",
            description=(
                "Writer Assistant. "
                "Task: receive the dictionary from the Reader Agent and generate "
                "documentation assets based on the provided data."
            ),
            model_client=model_client,
            system_message=(
                "Write documentation for the provided file, using your tool to record conclusions."
            ),
            tools=[write_text_to_file],
        )

        conclusion_formatter = AssistantAgent(
            name="conclusion_formatter",
            description="Architecture Documentation Agent. Generates full system documentation in Markdown format.",
            model_client=model_client,
            tools=[write_text_to_file, read_file],
            system_message="""You are the Document Agent. Your role is to generate clear, structured, and professional system documentation in **Markdown format**. 
            Your documentation must always follow the format below:
            
            # Introduction
            Provide a concise overview of the system, its context, and what it is designed to achieve. (1–2 pages)
            
            # Purpose & Scope
            Explain the goals of the system and define the boundaries of what is covered in this documentation. (1–2 pages)
            
            # System Overview
            Summarize the system architecture and how the components interact. (1–2 pages)
            
            ## Key Functionalities
            List the main features of the system. Each feature should be presented as:
            **Feature Name**: followed by 2–3 sentences describing what the feature does and why it is important.
            
            ## Technology Stack
            Detail the technologies used in the system:
            - **Programming Languages**
            - **Databases** (include schema if available)
            - **Message Queues** (list topics and their purpose)
            - **Frameworks/Libraries**
            - **CI/CD (including build and packaging process)**
            
            # Codebase Structure
            Explain how the repository is organized:
            - **Repository Organization**: describe folder layout and purpose.
            - **Key Packages**: list important packages and their responsibilities.
            - **Key Modules & Entry Points (API)**: describe endpoints, business logic, and how the system starts.
            
            ---
            
            ### Requirements:
            - Each section must be **1–2 pages of text** with concrete details from the repository.
            - Avoid generic information; instead, extract specifics such as:
              - Endpoints with business logic
              - Database schema
              - Message queue topics
              - Build and packaging process (analyze code for build scripts, Dockerfiles, etc.)
            - The final document must be in **Markdown format**.
            """,
        )

        task = "Please write me documentation for this repository https://github.com/github-samples/game-of-life-walkthrough"

        team = RoundRobinGroupChat([reader, writer, conclusion_formatter], max_turns=10)

        stream = team.run_stream(task=task)

        await Console(stream)

    asyncio.run(main())
