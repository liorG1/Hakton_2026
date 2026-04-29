from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import asyncio
import json
from ..prompts import ANXIETY_PROMPT, PTSD_PROMPT
from .llm_manager import LLMManager

class Section(BaseModel):
    subtitle: str = Field(description="The subtitle of the section")
    content: str = Field(description="The content of the section")

class AnalysisResult(BaseModel):
    title: str = Field(description="The overall title of the summary")
    sections: List[Section] = Field(description="List of sections containing summary details")

async def process_url_for_disability(content: str, disability: str):
    if disability.lower() == "anxiety":
        prompt_text = ANXIETY_PROMPT
    else:
        prompt_text = PTSD_PROMPT

    try:
        llm = LLMManager().get_llm()
        parser = JsonOutputParser(pydantic_object=AnalysisResult)
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | llm | parser

        result = await chain.ainvoke({"content": content})
        return result

    except Exception as e:
        return {
            "title": "Error Processing Content",
            "sections": [
                {
                    "subtitle": "Error",
                    "content": str(e)
                }
            ]
        }

async def stream_url_for_disability(content: str, disability: str):
    prompt_text = ANXIETY_PROMPT if disability.lower() == "anxiety" else PTSD_PROMPT
    
    try:
        llm = LLMManager().get_llm()
        parser = JsonOutputParser(pydantic_object=AnalysisResult)
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | llm | parser

        # שים לב: אנחנו פשוט עושים yield לצ'אנק כמו שהוא
        async for chunk in chain.astream({"content": content}):
            if chunk:
                yield chunk
    except Exception as e:
        yield {"title": "Error", "sections": [{"subtitle": "Error", "content": str(e)}]}