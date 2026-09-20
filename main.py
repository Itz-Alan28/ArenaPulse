import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="ArenaPulse Operations API")

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
                    )

api_key = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key) if api_key else None


class IncidentReport(BaseModel):
    location: str
    description: str


@app.get("/health")
def health_check():
    return {
    "status": "online" ,
    "api_key_configured": bool(api_key),
    "system": "ArenaPulse FIFA 2026 Operations Core"
                        }


@app.post("/api/triage")
async def triage_incident(report: IncidentReport):
    if not client:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY environment variable is missing."
        )
                                                           
    prompt = f"""
You are the AI Operations Controller for ArenaPulse at FIFA World Cup 2026.
Analyze the incoming incident report and categorize it for stadium dispatch.

Location: {report.location}
Report: {report.description}

Return JSON only with:
- category: (Medical, Security, Maintenance, Crowd Control, General Inquiry)
- priority: (Low, Medium, High, Critical)
- summary: A concise 1-sentence summary of the situation
- recommended_action: Immediate recommended operational step for dispatchers
    """
    try:        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        parsed_data = json.loads(response.text)
        return {"status": "success", "data": parsed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_index():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "index.html not found. Please ensure the file is named index.html"}
                                                                                                                                                                                                                                                                                    