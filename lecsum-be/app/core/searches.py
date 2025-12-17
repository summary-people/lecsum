import os
import asyncio
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



#### 해설 보강용 검색 함수
async def search_and_format_run(query: str, num_results: int = 3) -> str:
    """
    구글 검색을 실행하고, LLM이 읽기 좋은 URL 포함 텍스트 포맷으로 반환합니다.
    """
    print(f"+++ Web Searching (Async) ... query: {query}")
    
    # 동기 함수인 .results()를 별도 스레드에서 실행하여 비동기화 및 Non-blocking 처리
    raw_results = await asyncio.to_thread(
        google_search_APIWrapper.results, 
        query, 
        num_results
    )
    
    return _format_results(raw_results)

def _format_results(results: list) -> str:
    if not results:
        return "검색 결과가 없습니다."
    
    formatted_text = ""
    for i, res in enumerate(results, 1):
        formatted_text += f"""
        [자료 {i}]
        - 제목: {res.get('title')}
        - 내용: {res.get('snippet')}
        - 출처(URL): {res.get('link')}
        """
    return formatted_text

