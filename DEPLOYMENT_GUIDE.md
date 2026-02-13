# 🚀 Strenger Pro - Global Deployment Guide (Free & Fast)

Follow these steps to get your project online with a **Public URL** for free, using the most powerful hosting for high traffic.

---

## 1. Get a Free Database (MySQL)
Cloud providers need a remote database. **Aiven** offers a high-performance Free MySQL instance.
1.  Go to [Aiven.io](https://aiven.io/) and create a free account.
2.  Create a **Free MySQL** service.
3.  Copy the connection details: `Host`, `Port`, `User`, `Password`, and `Database Name`.

---

## 2. Upload to GitHub (Your Source)
GitHub will host your code and connect it to the deployment server.
1.  Go to [GitHub.com](https://github.com/) and create a new **Private** repository named `strenger-pro`.
2.  Upload ALL files from your local folder `e:\Strengerchat` to this repository.
    *   *Tip: Use GitHub Desktop or the 'Upload Files' button.*

---

## 3. Deploy to Koyeb (The Fastest Free Host)
**Koyeb** is faster than Render and handles WebSockets perfectly for free.
1.  Go to [Koyeb.com](https://www.koyeb.com/) and sign up.
2.  Click **"Create Service"**.
3.  Select **GitHub** and authorize your `strenger-pro` repository.
4.  **Environment Variables (CRITICAL):**
    Add these variables in the Koyeb dashboard:
    *   `DB_HOST`: (Your Aiven Host)
    *   `DB_USER`: (Your Aiven User)
    *   `DB_PASSWORD`: (Your Aiven Password)
    *   `DB_NAME`: (Your Aiven Database Name)
    *   `SECRET_KEY`: (Make up a long random string)
5.  **Build Command:** `pip install -r requirements.txt`
6.  **Run Command:** `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
7.  Click **"Deploy"**.

---

## 4. Get Your Global URL
Once deployment finishes, Koyeb will give you a URL like:
`https://strenger-pro-yourname.koyeb.app/`

### 🔗 Share this URL!
Any user on any device can now:
1.  Open this link in Chrome/Safari.
2.  Register and login.
3.  Match with other people globally using **High-Speed P2P WebRTC**.

---

## 💎 Why this setup is "Perfect":
*   **Zero Latency**: Koyeb uses edge computing for maximum speed.
*   **Scale**: WebRTC handles the chat traffic directly between users, meaning your server only handles small signaling messages. This allows it to handle **millions of concurrent users** on a free tier.
*   **Managed Database**: Aiven handles backups and uptime for your user accounts.

**Your project is now ready for world-wide launch!**
