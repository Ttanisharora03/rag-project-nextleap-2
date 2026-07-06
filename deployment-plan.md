# Deployment Plan

This guide outlines the steps to deploy the RAG Chatbot project with the **Backend hosted on Render** and the **Frontend hosted on Vercel**.

## 1. Prerequisites
- A GitHub account with the project repository pushed to the `main` branch.
- A [Render](https://render.com/) account.
- A [Vercel](https://vercel.com/) account.
- A Groq API Key.

## 2. Backend Deployment (Render)

Render is a great free alternative for hosting Python/FastAPI applications directly from a GitHub repository.

### Step 2.1: Prepare the Repository
1. Ensure your `requirements.txt` is up-to-date and at the root of the project. It should include `fastapi`, `uvicorn`, `langchain`, `langchain-huggingface`, `langchain-groq`, `chromadb`, and `sentence-transformers`.
2. Ensure your processed data JSON files (`data/processed/*.json`) are committed to the repository so the backend can load them during deployment.

### Step 2.2: Deploy to Render
1. Go to the [Render Dashboard](https://dashboard.render.com/) and click **New** > **Web Service**.
2. Select **Build and deploy from a Git repository** and connect your GitHub account.
3. Choose the `rag-project-nextleap-2` repository.
4. Fill in the deployment details:
   - **Name**: `rag-backend` (or whatever you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.main:app --host 0.0.0.0 --port 10000` (Render defaults to port 10000, though `$PORT` also works).
5. Scroll down to **Advanced** to set environment variables.

### Step 2.3: Set Environment Variables
1. Under **Environment Variables**, click **Add Environment Variable**.
2. Add the following:
   - Key: `GROQ_API_KEY`
   - Value: Paste your Groq API key here.
3. Select the **Free** instance type and click **Create Web Service**.

### Step 2.4: Generate a Public Domain
1. Render will start building your project. This might take 3-5 minutes.
2. Once deployed, you will see a URL at the top left of your dashboard under the service name (e.g., `https://rag-backend-xyz.onrender.com`).
3. **Copy this URL**. You will need this for the frontend!

---

## 3. Frontend Deployment (Vercel)

The frontend is a static site (HTML/JS/CSS) located in the `frontend/` directory.

### Step 3.1: Update the API URL
Before deploying to Vercel, you need to tell the frontend to talk to your new Render backend instead of `localhost`.
1. Open `frontend/app.js` in your code editor.
2. Locate the `fetch` call in the `handleSendMessage` function (around line 108).
3. Change `'http://127.0.0.1:8000/api/chat'` to point to your Render domain:
   ```javascript
   // Change this:
   const response = await fetch('http://127.0.0.1:8000/api/chat', ...
   
   // To this (replace with your actual Render URL):
   const response = await fetch('https://YOUR-RENDER-DOMAIN.onrender.com/api/chat', ...
   ```
4. Commit this change and push it to GitHub:
   ```bash
   git add frontend/app.js
   git commit -m "Update backend API URL for production on Render"
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
- If you receive a correct response, your full stack is successfully deployed in the cloud! Note that Render's free tier spins down after 15 minutes of inactivity, so the very first request you make after a pause might take ~30-50 seconds to wake the server up.

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
