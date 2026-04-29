import asyncio
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import json
from langchain_community.document_loaders import WebBaseLoader

class Section(BaseModel):
    subtitle: str = Field(description="The subtitle of the section")
    content: str = Field(description="The content of the section")

class AnalysisResult(BaseModel):
    title: str = Field(description="The overall title of the summary")
    sections: List[Section] = Field(description="List of sections containing summary details")

ANXIETY_PROMPT = """
You are an assistant helping someone with anxiety. 
Please summarize the following webpage content in a calm, simple, and reassuring way. 
Avoid overwhelming details and focus on the most important information.
Format the output as a JSON object with 'title' and 'sections' (each section having 'subtitle' and 'content').

Content:
{content}
"""

PTSD_PROMPT = """
You are an assistant helping someone with PTSD. 
Please summarize the following webpage content. 
Be direct, use clear structure, and provide trigger warnings if any potentially distressing content is found. 
Ensure the summary is safe and supportive.
Format the output as a JSON object with 'title' and 'sections' (each section having 'subtitle' and 'content').

Content:
{content}
"""

async def process_url_for_disability(url: str, disability: str):
    loader = WebBaseLoader(url)
    # Use asyncio.to_thread to run the synchronous load() in a separate thread
    # This avoids the error "asyncio.run() cannot be called from a running event loop"
    # which happens with loader.aload() in some environments.
    docs = await asyncio.to_thread(loader.load)
    content = "\n".join([doc.page_content for doc in docs])

    if disability.lower() == "anxiety":
        prompt_text = ANXIETY_PROMPT
    else:
        prompt_text = PTSD_PROMPT

    llm = ChatOllama(model="phi3:mini", temperature=0)
    parser = JsonOutputParser(pydantic_object=AnalysisResult)

    prompt = ChatPromptTemplate.from_template(prompt_text)

    chain = prompt | llm | parser

    try:
        result = await chain.ainvoke({"content": content[:10000]})
        return result
    except Exception as e:
        # Fallback in case of parsing error
        return {
            "title": "Error Processing Content",
            "sections": [
                {"subtitle": "Error", "content": f"There was an error analyzing the content: {str(e)}"}
            ]
        }

