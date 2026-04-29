# Hakton_2026

This project consists of a FastAPI backend and a React (Vite) frontend.

## Prerequisites

- Python 3.8+
- Node.js and npm

## Setup and Running

### Backend

1. Navigate to the `BackEnd` directory:
   ```bash
   cd BackEnd
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up Ollama:
   - Install [Ollama](https://ollama.ai/) on your machine.
   - Pull the `phi3:mini` model:
     ```bash
     ollama pull phi3:mini
     ```

6. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will be running at `http://127.0.0.1:8000`.

### Frontend

1. Navigate to the `FrontEnd` directory:
   ```bash
   cd FrontEnd
   ```

2. Install the dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:5173`.
