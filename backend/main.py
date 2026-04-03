from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Trigger reload
app = FastAPI(title="CBSE Math Evaluator API", version="1.0")

# Setup CORS to allow requests from the frontend (especially if served locally via file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")

class EvaluationRequest(BaseModel):
    question: str
    student_answer: str
    total_marks: float

class StepBreakdown(BaseModel):
    step_description: str
    marks_awarded: float
    max_marks_for_step: float
    status: str

class ErrorAnalysis(BaseModel):
    conceptual_errors: List[str]
    procedural_errors: List[str]
    calculation_errors: List[str]
    presentation_errors: List[str]

class EvaluationResponse(BaseModel):
    total_marks_awarded: float
    maximum_marks: float
    step_by_step_breakdown: List[StepBreakdown]
    error_analysis: ErrorAnalysis
    feedback_for_student: str

GUIDELINES = """
You are an expert CBSE Class 10 Mathematics Examiner. Your task is to evaluate student answers strictly based on NCERT mathematical concepts and CBSE marking schemes.

## Core Evaluation Principles
- Follow NCERT strictly
- Evaluate step-by-step
- Method is more important than final answer
- Maintain consistency in grading
- Balanced strictness (strict but fair)

## Marking Scheme
- Understanding problem -> 1 mark
- Correct formula -> 1 mark
- Substitution/steps -> 1 mark
- Calculation -> 1-2 marks
- Final answer -> 1 mark
(Adapt these proportionately based on the maximum marks allowed).

## Error Classification
- Conceptual Error (wrong formula/theory)
- Procedural Error (wrong steps)
- Calculation Error (arithmetic mistake)
- Presentation Error (missing steps/units)

## Partial Marking Rules
- Give marks for correct steps even if final answer is wrong
- Follow carry-forward rule for calculation mistakes

## Special Cases
- If only final answer is correct: -> award up to 1-2 marks depending on correctness
- Correct method but wrong answer -> give most marks
- Minor calculation mistake -> small deduction
- Completely wrong -> 0 or minimal marks

## Anti-Hallucination Rules
- Do NOT assume steps
- Do NOT invent reasoning
- Evaluate only what is written

## Output Format
You MUST return ONLY valid JSON in exactly this schema without markdown block formatting:
{
  "total_marks_awarded": float,
  "maximum_marks": float,
  "step_by_step_breakdown": [
    {
      "step_description": "string",
      "marks_awarded": float,
      "max_marks_for_step": float,
      "status": "correct | partial | incorrect | skipped"
    }
  ],
  "error_analysis": {
    "conceptual_errors": ["string"],
    "procedural_errors": ["string"],
    "calculation_errors": ["string"],
    "presentation_errors": ["string"]
  },
  "feedback_for_student": "string"
}
"""

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_answer(req: EvaluationRequest):
    # Check if a real key exists.
    load_dotenv(override=True)
    current_key = os.getenv("OPENAI_API_KEY")
    if not current_key or current_key == "your_actual_api_key_here" or current_key.strip() == "":
        print("Using MOCK response because OpenAI API key is missing or default.")
        
        return {
            "total_marks_awarded": round(req.total_marks * 0.9, 1),
            "maximum_marks": req.total_marks,
            "step_by_step_breakdown": [
                {
                    "step_description": "(MOCKED) Understanding problem & Extracting Given",
                    "marks_awarded": round(req.total_marks * 0.2, 1),
                    "max_marks_for_step": round(req.total_marks * 0.2, 1),
                    "status": "correct"
                },
                {
                    "step_description": "(MOCKED) Applying Correct Method/Formula",
                    "marks_awarded": round(req.total_marks * 0.3, 1),
                    "max_marks_for_step": round(req.total_marks * 0.3, 1),
                    "status": "correct"
                },
                {
                    "step_description": "(MOCKED) Calculation and Execution",
                    "marks_awarded": round(req.total_marks * 0.4, 1),
                    "max_marks_for_step": round(req.total_marks * 0.5, 1),
                    "status": "partial"
                }

            ],
            "error_analysis": {
                "conceptual_errors": [],
                "procedural_errors": [],
                "calculation_errors": ["(MOCKED) Minor error in intermediate addition."],
                "presentation_errors": ["(MOCKED) Missing units in one of the steps."]
            },
            "feedback_for_student": "[MOCKED FEEDBACK] Your method is correct, but be careful with calculations and always include units."
        }

    # If the key is present, attempt live execution
    client = OpenAI(api_key=api_key)

    prompt = f"""
Strictly follow the GUIDELINES below to evaluate the STUDENT ANSWER.
-----------------------------------
GUIDELINES:
{GUIDELINES}

-----------------------------------
QUESTION:
{req.question}

-----------------------------------
STUDENT ANSWER:
{req.student_answer}

-----------------------------------
MAXIMUM MARKS:
{req.total_marks}
-----------------------------------
Ensure you return strictly JSON.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a highly strict and consistent CBSE Class 10 Mathematics examiner. You output strictly conforming JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        output_txt = response.choices[0].message.content
        parsed = json.loads(output_txt)
        return parsed
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg.lower() or "429" in error_msg:
            error_msg = "OpenAI API Quota Exceeded. Please check your billing dashboard."
            
        print(f"Error calling OpenAI API: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
