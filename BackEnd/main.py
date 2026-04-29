from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from BackEnd.services.scrapper import process_url
from BackEnd.services.langchain import stream_url_for_disability
import json

class AnalyzeRequest(BaseModel):
    url: str
    disability: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    async def event_generator():
        try:
            # 🔹 STATUS 1
            yield json.dumps({"type": "status", "message": "מנתח את הקישור..."}) + "\n"

            scraped = await process_url(request.url)
            sections = scraped.get("sections", [])
            content = "\n".join([s.get("text", "") for s in sections])

            if not content:
                yield json.dumps({"type": "error", "message": "לא נמצא תוכן."}) + "\n"
                return

            # 🔹 STATUS 2
            yield json.dumps({"type": "status", "message": "מנתח את התוכן..."}) + "\n"

            # 🔹 STREAM LLM (fixed format)
            async for chunk in stream_url_for_disability(content, request.disability):
                yield json.dumps({
                    "type": "data",
                    "chunk": chunk
                }) + "\n"

            # 🔹 END SIGNAL
            yield json.dumps({"type": "end"}) + "\n"

        except Exception as e:
            yield json.dumps({
                "type": "error",
                "message": f"שגיאה: {str(e)}"
            }) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")