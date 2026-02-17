---
title: Strenger Pro Chat
emoji: 💬
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

# 🚀 StrengerChat Pro - Hugging Face Edition

This repository is configured to deploy directly to Hugging Face Spaces.

## How to Deploy on Hugging Face (Free Forever)

1.  **Create a New Space:**
    *   Go to [huggingface.co/new-space](https://huggingface.co/new-space)
    *   Name: `strenger-chat` (or similar)
    *   SDK: **Docker** (Select "Docker", do NOT select Gradio/Streamlit)
    *   Hardware: **CPU Basic (Free - 2 vCPU, 16GB RAM)**

2.  **Upload Code:**
    *   Clone this repo to the Hugging Face Space via git, OR
    *   Go to "Files" -> "Add File" -> "Upload Files" and upload everything from this folder.

3.  **Environment Variables (CRITICAL):**
    *   Go to your Space's **Settings** -> **Variables and secrets**.
    *   Add your Database URL (from Neon/ElephantSQL):
        *   Key: `DATABASE_URL` 
        *   Value: `postgres://user:pass@host/db`
    *   (Optional) Secret Key:
        *   Key: `SECRET_KEY`
        *   Value: `some_random_secure_string`

4.  **Wait for Build:**
    *   Click "App". You will see "Building...". This takes ~3-5 minutes.
    *   Once done, your app is live at `https://huggingface.co/spaces/YOUR_USERNAME/strenger-chat`.

## ⚠️ Important Limitations on Hugging Face Spaces (Free Tier)
1.  **Sleeps after 48h:** Unless you upgrade to Pro ($9/mo), the Space will "pause" if no one visits it for 48 hours. The first visit after a pause takes ~30s to start up.
2.  **No Persistent Files:** If you restart the Space, any file saved to disk (`logs`, `sqlite.db`) is DELETED. You **MUST** use an external database (which you are already doing with Postgres!).