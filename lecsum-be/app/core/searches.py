import os
from dotenv import load_dotenv
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper

load_dotenv()

google_search_APIWrapper = GoogleSearchAPIWrapper(
    google_cse_id=os.getenv("GOOGLE_CSE_ID"), google_api_key=os.getenv("GOOGLE_API_KEY")
)

google_search_tool = Tool(
    name="Google Search",
    description="Search the web for relevant documents",
    func=google_search_APIWrapper.run,
    
)

def search_run(query: str):
    print("+++ web Searching ...........")
    return google_search_tool.run(query)