from langchain_google_community import GoogleSearchAPIWrapper
from langchain.tools import Tool
from googleapiclient.discovery import build
import os
import requests

def youtube_search(query: str, max_results: int = 3) -> str:
    api_key = os.getenv("YOUTUBE_API_KEY")  
    if not api_key:
        return "Missing YOUTUBE_API_KEY in environment."

    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=max_results,
        type="video"
    )
    response = request.execute()
    
    videos = []
    for item in response.get("items", []):
        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append(f"{title} - {url}")

    return "\n".join(videos) if videos else "No YouTube results found."

def github_issue_search(query: str) -> str:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}
    url = f"https://api.github.com/search/issues?q={query}+in:title+repo:langchain-ai/langchain"
    resp = requests.get(url, headers=headers).json()
    if "items" in resp and resp["items"]:
        return "\n".join(f"{i['title']}: {i['html_url']}" for i in resp["items"][:3])
    return "No relevant issues found on GitHub."

def get_search_tools():
    google = GoogleSearchAPIWrapper()
    return [
        Tool(name="Google Search", func=google.run, description="Web queries"),
        Tool(name="YouTube Video Search", func=youtube_search, description="YouTube video search powered by YouTube Data API"),
        Tool(name="GitHub Issues Search", func=github_issue_search, description="Search LangChain repo issues"),
    ]
