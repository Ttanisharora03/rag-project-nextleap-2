# Deployment Plan

This guide outlines the steps to deploy the **Mutual Fund FAQ Assistant** with the backend hosted on **Railway** and the frontend hosted on **Vercel**.

---

## Prerequisites

- A GitHub account with the project repository (`rag-project-nextleap-2`) pushed to the `main` branch.
- A [Railway](https://railway.app/) account.
- A [Vercel](https://vercel.com/) account.
- A Groq API key from [console.groq.com/keys](https://console.groq.com/keys).

---

## Part 1 — Backend Deployment on Railway

### Step 1: Prepare the Repository

Make sure the following files are committed and pushed to `main`:

1. **`requirements.txt`** at the project root with all Python dependencies.
2. **`Procfile`** at the project root with the following content:
   ```
   web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
   ```
3. **`data/processed/*.json`** files so the RAG pipeline can load data at startup.

### Step 2: Create a New Project on Railway

1. Go to [railway.app/dashboard](https://railway.app/dashboard).
2. Click **New Project**.
3. Select **Deploy from GitHub repo**.
4. Connect your GitHub account if prompted.
5. Select the `rag-project-nextleap-2` repository.
6. Railway will automatically detect Python and start building.

### Step 3: Add Environment Variables

1. Click on your newly created service in the Railway dashboard.
2. Go to the **Variables** tab.
3. Click **New Variable** and add:
   - `GROQ_API_KEY` = `<your Groq API key>`
4. Railway will automatically redeploy after saving.

### Step 4: Generate a Public Domain

1. Click on your service and go to the **Settings** tab.
2. Scroll down to the **Networking** section.
3. Click **Generate Domain**.
4. Copy the generated URL (e.g., `https://rag-project-nextleap-2-production.up.railway.app`).

### Step 5: Verify the Backend

Visit the following URL in your browser:

```
https://<your-railway-domain>/api/health
```

You should see:

```json
{ "status": "ok" }
```

---

## Part 2 — Frontend Deployment on Vercel

### Step 1: Update the Backend URL in the Frontend

1. Open `frontend/app.js`.
2. On line 117, change:
   ```javascript
   const response = await fetch('http://127.0.0.1:8000/api/chat', {
   ```
   to:
   ```javascript
   const response = await fetch('https://<your-railway-domain>/api/chat', {
   ```
   Replace `<your-railway-domain>` with the actual Railway URL you copied earlier.

3. Commit and push:
   ```bash
   git add frontend/app.js
   git commit -m "Update API URL to Railway backend"
   git push origin main
   ```

### Step 2: Deploy to Vercel

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard).
2. Click **Add New** → **Project**.
3. Import the `rag-project-nextleap-2` repository.
4. Configure the project:
   - **Framework Preset**: `Other`
   - **Root Directory**: Click **Edit** and select `frontend`
   - **Build Command**: Leave blank
   - **Output Directory**: Leave blank
5. Click **Deploy**.

### Step 3: Verify the Frontend

1. Open the Vercel URL provided after deployment.
2. Ask the chatbot a question like *"What is the exit load?"*.
3. If you get a response, the deployment is successful.

---

## CORS Configuration

The backend already allows cross-origin requests from any domain. This is configured in `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, you can replace `"*"` with your Vercel URL for stricter security.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Railway fails with "No start command" | Make sure `Procfile` exists at the project root |
| `ModuleNotFoundError` on Railway | Check `requirements.txt` has all dependencies |
| Frontend says "Backend not available" | Verify the Railway URL in `frontend/app.js` is correct |
| CORS errors in browser console | Check `allow_origins` in `src/api/main.py` |
