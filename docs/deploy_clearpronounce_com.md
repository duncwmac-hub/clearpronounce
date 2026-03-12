# Deploy ClearPronounce to clearpronounce.com

You have: **Namecheap** (domain), **Google Mail** (duncan@clearpronounce.com), and this repo. Fastest path: one host for app + API, then point the domain there.

---

## 1. Host the app (Render – free tier)

1. Push this repo to **GitHub** (if not already).
2. Go to [render.com](https://render.com), sign up or log in, and connect your GitHub account.
3. **New → Web Service**. Select the `clearpronounce` repo.
4. Render will read `render.yaml` and prefill:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn src.backend.app:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Wait for the first deploy (a few minutes).
6. Note the URL Render gives you, e.g. `https://clearpronounce-xxxx.onrender.com`.

---

## 2. Point clearpronounce.com to Render (Namecheap)

1. In **Render**: open your service → **Settings → Custom Domains**. Add `clearpronounce.com` (and optionally `www.clearpronounce.com`). Render will show the target to use (e.g. a CNAME like `clearpronounce-xxxx.onrender.com` or an A record).
2. In **Namecheap**: go to **Domain List → clearpronounce.com → Manage → Advanced DNS**.
3. Add the record Render tells you:
   - Usually **CNAME Record**: Host `@` or `www`, Value = the Render host (e.g. `clearpronounce-xxxx.onrender.com`).  
   - Some setups use an **A Record** (Host `@`, Value = Render’s IP). Follow Render’s exact instructions.
4. Save. SSL (HTTPS) is issued automatically by Render; it can take a few minutes after DNS propagates (up to 48 hours, often much less).

---

## 3. Check

- Visit **https://clearpronounce.com**. You should see the app; paste text and click Analyze to confirm the API works.
- Email **duncan@clearpronounce.com** is already set up (Google); the footer links to it for contact.

---

## 4. Optional next steps

- **Support link:** Replace the placeholder Ko-fi URL in `src/frontend/index.html` with your real payment link.
- **Environment variables:** If you ever need to override paths (e.g. `CP_LEXICON_PATH`), add them in Render **Environment** and redeploy.
- **Monitoring:** Render dashboard shows logs and deploy history; use them for the first evidence-based audit after people start using the site.
