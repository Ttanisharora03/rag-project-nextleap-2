# Deployment Plan

This guide outlines the steps to deploy the RAG Chatbot project with the **Backend hosted on Railway** and the **Frontend hosted on Vercel**.

## 1. Prerequisites
- A GitHub account with the project repository pushed to the `main` branch.
- A [Railway](https://railway.app/) account.
- A [Vercel](https://vercel.com/) account.
- A Groq API Key.

## 2. Backend Deployment (Railway)

Railway makes it easy to deploy Python/FastAPI applications directly from a GitHub repository.

### Step 2.1: Prepare the Repository
1. Ensure your `requirements.txt` is up-to-date and at the root of the project. It should include `fastapi`, `uvicorn`, `langchain`, `langchain-huggingface`, `langchain-groq`, `chromadb`, and `sentence-transformers`.
2. Ensure your processed data JSON files (`data/processed/*.json`) are committed to the repository so the backend can load them during deployment.

### Step 2.2: Deploy to Railway
1. Go to the [Railway Dashboard](https://railway.app/dashboard) and click **New Project**.
2. Select **Deploy from GitHub repo** and choose the `rag-project-nextleap-2` repository.
3. Railway will automatically detect the Python environment from `requirements.txt`.
4. Go to the **Settings** tab of your new service, scroll down to the **Deploy** section, and set the **Start Command** to:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
   ```

### Step 2.3: Set Environment Variables
1. Go to the **Variables** tab for your Railway service.
2. Add the following variable:
   - `GROQ_API_KEY`: Paste your Groq API key here.

### Step 2.4: Generate a Public Domain
1. Go to the **Settings** tab.
2. Under the **Networking** section, click **Generate Domain**.
3. **Copy this newly generated URL** (e.g., `https://rag-backend-production.up.railway.app`). You will need this for the frontend!

---

## 3. Frontend Deployment (Vercel)

The frontend is a static site (HTML/JS/CSS) located in the `frontend/` directory.

### Step 3.1: Update the API URL
Before deploying to Vercel, you need to tell the frontend to talk to your new Railway backend instead of `localhost`.
1. Open `frontend/app.js` in your code editor.
2. Locate the `fetch` call in the `handleSendMessage` function (around line 108).
3. Change `'http://127.0.0.1:8000/api/chat'` to point to your Railway domain:
   ```javascript
   // Change this:
   const response = await fetch('http://127.0.0.1:8000/api/chat', ...
   
   // To this (replace with your actual Railway URL):
   const response = await fetch('https://YOUR-RAILWAY-DOMAIN.up.railway.app/api/chat', ...
   ```
4. Commit this change and push it to GitHub:
   ```bash
   git add frontend/app.js
   git commit -m "Update backend API URL for production"
   git push origin main
   ```

### Step 3.2: Deploy to Vercel
1. Go to the [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New** > **Project**.
2. Import the `rag-project-nextleap-2` repository.
3. In the **Configure Project** section:
   - **Framework Preset**: Leave as `Other`.
   - **Root Directory**: Click **Edit** and select the `frontend` folder.
   - **Build Command**: Leave blank (not needed for plain HTML/JS).
   - **Output Directory**: Leave blank.
4. Click **Deploy**.

## 4. Final Verification
- Once Vercel finishes deploying, click on your newly generated Vercel URL.
- Try asking the AI a question (e.g., "What is the exit load?").
- If you receive a correct response, your full stack is successfully deployed in the cloud!

## Additional Notes (CORS)
FastAPI automatically blocks requests from unknown domains for security. Ensure that `src/api/main.py` has CORS configured to allow your Vercel domain. 

In `src/api/main.py`, make sure you have:
```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For strict security in production, replace "*" with your exact Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Since this is already implemented in your codebase, you should not face any CORS issues!
