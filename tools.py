from langchain.agents import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_community.tools import YouTubeSearchTool
import requests, os

def github_issue_search(query: str) -> str:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/search/issues?q={query}+in:title+repo:langchain-ai/langchain"
    resp = requests.get(url, headers=headers).json()
    if "items" in resp and resp["items"]:
        return "\n".join(f"{i['title']}: {i['html_url']}" for i in resp["items"][:3])
    return "No relevant issues found on GitHub."

def get_search_tools():
    google = GoogleSearchAPIWrapper()
    return [
        Tool(name="Google Search", func=google.run, description="Web queries"),
        Tool(name="YouTube Transcript Search", func=YouTubeSearchTool().run, description="YouTube content"),
        Tool(name="GitHub Issues Search", func=github_issue_search, description="GitHub issues search"),
    ]

