# CBSE Class 10 Math AI Evaluator

A complete, full-stack AI system designed specifically to evaluate Class 10 Mathematics answers strictly according to **NCERT mathematical patterns** and **official CBSE marking schemes**. 

This system moves beyond basic generative responses by structurally decomposing the student's solution, calculating partial marks, isolating specific algorithmic/conceptual errors, and generating actionable feedback without assuming unwritten logic.

---

## ⚡ Features

- **CBSE Guidelines Enforcer**: Hard-coded structural prompts that simulate a strict CBSE examiner prioritizing the *method and logic* directly over the *final answer*.
- **Structured JSON Engine**: Ensures the AI securely outputs rigid JSON data tracking specific error arrays and nested timeline evaluations.
- **Step-by-step Timeline Rendering**: Parses evaluations into a beautiful UI timeline displaying individual marks earned per conceptual step.
- **Error Classification**: Granular categorization separating *Procedural Errors* (skipping algebraic steps), *Calculation Errors* (simple numerical slips), and *Presentation Errors* (omitting final units).
- **Graceful Fallbacks**: Catches native OpenAI Quota/Billing rate limits and forwards structured errors cleanly to the frontend instead of crashing natively.

---

## 🏗️ System Architecture

### 1. The Backend (`/backend`)
- **Framework**: Built completely in Python using **FastAPI** for ultra-fast, robust asynchronous REST endpoints.
- **Integration**: Leverages the **OpenAI Python SDK** (`gpt-4o-mini`) leveraging native `response_format={"type": "json_object"}`.
- **Data Integrity**: Powered by **Pydantic** data classes for explicit structural type-safety and request validation.

### 2. The Frontend (`/frontend`)
- **Tech Stack**: 100% Vanilla HTML, CSS, and JS. Zero `npm` build dependencies required for absolute maximum cross-platform compatibility.
- **UI/UX**: Premium Dark-Theme aesthetic. Built using highly customizable CSS variables, fluid glassmorphism (translucency and backdrop blurs), responsive grids, and Google Fonts (`Outfit`).

---

## 🚀 Setup & Installation

### Step 1: Backend Configuration
1. Navigate to the `backend/` directory footprint.
2. Install the necessary Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your API key:
   - Create a `.env` file (or duplicate `.env.example`).
   - Add your live OpenAI API key.
   ```ini
   OPENAI_API_KEY=sk-xxxx...
   ```

### Step 2: Initialize Server
Run the FastAPI application via Uvicorn. The backend runs securely on `http://localhost:8000` by default.
```bash
uvicorn main:app --reload
```

### Step 3: Launch Interface
1. Because the frontend relies entirely on native browser scripting, there are no webpack steps.
2. Navigate directly to the `frontend/` folder.
3. Open `index.html` natively inside Chrome, Firefox, or Edge.
4. Input your equations and evaluate!

---

## 📝 Core Evaluation Rules Configured

Our model evaluates every request under these specific constraints enforced in `main.py`:

- **Anti-Hallucination Framework:** The system evaluates strictly and solely off the provided text. It is expressly prohibited from inventing missing intermediary logical leaps to "help" the student secure marks. 
- **The "Final Answer Only" Protocol:** Answers yielding correct endpoints without explicitly detailing underlying mathematical methods suffer heavily. Unless evaluating an explicit 1-mark objective question, answers without step tracking forfeit up to 80% to 100% of awarded marks.
- **Carry Forward Safety:** Subsequent steps are actively checked against mathematical consistency based on *flawed intermediate calculations*. An arithmetic error isolated at Step 1 does not unilaterally nuke points earned at Step 3, granted Step 3 logically stems from Step 1's numerical flaw.
