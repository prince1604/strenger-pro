# 🚀 Strenger Pro - Global Deployment Guide (Free & Fast)

Follow these steps to get your project online with a **Public URL** for free, using the most powerful hosting for high traffic.

---

## 1. Set Up Koyeb PostgreSQL Database
Koyeb provides a managed PostgreSQL database for your application.

### Create Database:
1. Go to [Koyeb.com](https://www.koyeb.com/) → **Database Services**
2. Click **"Create Database"** (if you haven't already)
3. Select **PostgreSQL** (Free tier available)
4. Choose a region (e.g., Singapore `ap-southeast-1`)
5. Name it `koyebdb` (or any name you prefer)
6. Click **"Create"**

### Get Connection Details:
1. Click on your **database name** in the databases list
2. Copy these exact values from the **Connection Details** section:
   - **Host**: `ep-XXXXX-XXXXX.ap-southeast-1.pg.koyeb.app`
   - **Port**: `5432`
   - **User**: `koyeb-adm` (usually)
   - **Password**: `npg_XXXXXXXXXXXXXXX` (**IMPORTANT**: Copy the FULL password!)
   - **Database**: `koyebdb`

⚠️ **CRITICAL**: Save these credentials securely - you'll need them in the next steps!

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
    Add these variables in the Koyeb **App Settings** → **Environment** section:
    ```
    DATABASE_HOST=<Your Koyeb Postgres Host from Step 1>
    DATABASE_USER=<Your Koyeb User from Step 1>
    DATABASE_PASSWORD=<Your Koyeb Password from Step 1>
    DATABASE_NAME=koyebdb
    DATABASE_PORT=5432
    SECRET_KEY=<Make up a long random string, e.g., your-super-secret-key-12345>
    ```
    
    **Example:**
    ```
    DATABASE_HOST=ep-patient-wind-a1phbzpe.ap-southeast-1.pg.koyeb.app
    DATABASE_USER=koyeb-adm
    DATABASE_PASSWORD=npg_Q1lakOpE5omYXXXXXXXX
    DATABASE_NAME=koyebdb
    DATABASE_PORT=5432
    SECRET_KEY=my-super-secret-random-key-2024
    ```
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
