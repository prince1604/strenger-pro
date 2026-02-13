# Recommended Model: Llama 2 Uncensored

Based on your **8GB RAM** and desire for **unrestricted** chat, here is the best choice:

### 🏆 Best Choice: `llama2-uncensored`
- **Why**: It is specifically designed to have fewer refusals/restrictions.
- **Size**: **3.8GB**. This fits perfectly in your 8GB RAM (leaving ~4GB for Windows). 
- **Performance**: It will run reasonably fast on your machine.

---

## 🚀 How to Install & Run (Required)

Since you are switching back to local AI, you **must** do this once:

1. **Install Ollama** (if you haven't already) from [ollama.com](https://ollama.com).
2. Open a Terminal (Command Prompt).
3. Run this command to download the specific model:
   ```bash
   ollama run llama2-uncensored
   ```
4. Wait for it to finish downloading (approx 3.8GB).
5. Once it gives you a prompt `>>>`, you can type `/bye` to exit or just close the window.
6. **Restart your Strenger Chat server** (`run_app.bat`).

---

## 🥈 Alternative: `llama3.2`
If Llama 2 feels too "old" or "dumb", try **Llama 3.2**.
- **Size**: **2.0GB** (Runs extremely fast).
- **Pros**: Very smart, very fast.
- **Cons**: Might refuse some spicy topics.
- **Command**: `ollama run llama3.2`

To switch, just change line 9 in `bot.py` to `model_name="llama3.2"`.
