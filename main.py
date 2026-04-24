from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import random
import json

app = FastAPI()

# 1. The CORS VIP Pass
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Configure the Gemini Brain
genai.configure(api_key="AIzaSyC-W7KABfrWi92j5T8nLPw_oOu9iH3-Z0s")
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. Handle the request
@app.post("/api/generate-question")
async def generate_question(request: Request):
    try:
        body = await request.json()
        asked_questions = body.get("asked", [])
        
        categories = ["Quantitative_Ability", "Computer_Awareness", "Logical_Reasoning", "English"]
        weights = [0.40, 0.40, 0.10, 0.10]
        selected_category = random.choices(categories, weights=weights, k=1)[0]
        
        prompt = f"""
        You are an expert professor designing a test for the TANCET exam.
        Generate 1 unique, highly challenging multiple-choice question for the category: {selected_category}.
        
        CRITICAL RULE: Do NOT generate a question that is similar to any of these previous questions: {asked_questions}
        
        You must respond ONLY with a raw JSON object. Do not use Markdown formatting, do not use backticks, and do not add any extra text. 
        Format:
        {{
            "text": "The question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "The exact text of the correct option",
            "explanation": "A friendly, 1-2 sentence step-by-step explanation of why the answer is correct."
        }}
        """
        
        # Try to call the AI
        response = model.generate_content(prompt)
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        ai_question_data = json.loads(raw_text)
        
        return {
            "category": selected_category,
            "question_data": ai_question_data
        }
        
    except Exception as e:
        # NEW: The Fallback! If Google rejects the request, we send this friendly dummy question instead of crashing.
        print(f"Server caught an error: {e}")
        return {
            "category": "Speed Limit Reached",
            "question_data": {
                "text": "Whoa! The AI Tutor needs a quick 15-second coffee break! Google only allows 5 free questions per minute.",
                "options": ["I will wait 15 seconds!", "Take your time!", "I am studying too fast!"],
                "answer": "I will wait 15 seconds!",
                "explanation": "This is our built-in safety net. Wait a few seconds, then click Next Question to continue your TANCET prep!"
            }
        }