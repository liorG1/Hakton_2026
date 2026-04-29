import aiohttp
import asyncio
import trafilatura
from bs4 import BeautifulSoup
import json
import time

# ---------- FETCH ----------
async def get_html(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


# ---------- TRAFILATURA ----------
def extract_text_sync(html: str):
    return trafilatura.extract(html, include_formatting=True)


async def extract_text_async(html: str):
    return await asyncio.to_thread(extract_text_sync, html)


# ---------- TITLE ----------
def extract_title(html: str):
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    if soup.title:
        return soup.title.get_text(strip=True)

    return ""


# ---------- SMART PARSER ----------
def parse_text_smart(text: str):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    sections = []
    current = None

    has_subtitles = any(line.startswith("## ") for line in lines)

    # ?? ?? ??? ??????
    if has_subtitles:
        for line in lines:
            if line.startswith("## "):
                if current:
                    sections.append(current)

                current = {
                    "subtitle": line.replace("## ", ""),
                    "text": ""
                }
            else:
                if current:
                    current["text"] += " " + line

        if current:
            sections.append(current)

    # ?? ??? ??? ??????
    else:
        for i, line in enumerate(lines):
            sections.append({
                "subtitle": f"???? {i+1}",
                "text": line
            })

    return sections


# ---------- PIPELINE ----------
async def process_url(url: str):
    try:
        # ---------- FETCH ----------
        html = await get_html(url)

        # ---------- TITLE ----------
        title = await asyncio.to_thread(extract_title, html)

        # ---------- TEXT ----------
        text = await extract_text_async(html)

        if not text:
            return {"title": title, "sections": []}

        # ---------- PARSE ----------
        sections = parse_text_smart(text)

        return {
            "title": title,
            "sections": sections
        }

    except Exception as e:
        return {"title": "Error", "sections": []}
