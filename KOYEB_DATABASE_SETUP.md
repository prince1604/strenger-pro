# 🎯 Koyeb Database Setup Checklist

## Step 1: Verify Database is Created ✅
You already have a database! I can see "koyebdb" in your screenshot.

## Step 2: Get the COMPLETE Connection Details

1. **On Koyeb Dashboard** → **Database Services**
2. Click on **"koyebdb"** (your database)
3. You should see a section called **"Connection Details"** or **"Connection Info"**
4. Copy the following (EXACTLY as shown):

   ```
   Host: ep-patient-wind-a1phbzpe.ap-southeast-1.pg.koyeb.app
   Port: 5432
   User: koyeb-adm
   Password: npg_Q1lakOpE5omY_____________ ⚠️ COPY THE FULL PASSWORD!
   Database: koyebdb
   ```

   ⚠️ **IMPORTANT**: The password shown in your current `.env` file might be incomplete!
   Make sure to copy the FULL password from Koyeb.

## Step 3: Update Your Koyeb App Environment Variables

1. Go to **Koyeb Dashboard** → **Services** (or **Apps**)
2. Click on your **deployed application** (strenger-pro or similar)
3. Go to **Settings** → **Environment Variables**
4. Add or Update these variables:

   ```
   DATABASE_HOST=ep-patient-wind-a1phbzpe.ap-southeast-1.pg.koyeb.app
   DATABASE_USER=koyeb-adm
   DATABASE_PASSWORD=<PASTE THE FULL PASSWORD FROM STEP 2>
   DATABASE_NAME=koyebdb
   DATABASE_PORT=5432
   ```

5. **Save** the changes
6. Your app will automatically **redeploy** with the new variables

## Step 4: Verify Database Tables are Created

Your app is configured to automatically create database tables on startup using `schema_pg.sql`.

When your app redeploys:
1. Check the **deployment logs** in Koyeb
2. Look for messages like:
   - `"POSTGRES SCHEMA SYNC"`
   - `"POSTGRES DB READY"`

## Step 5: Test Your Application

1. Once deployed, open your app URL: `https://your-app-name.koyeb.app`
2. Try to **register a new user**
3. If registration works → Database is connected! 🎉
4. If you get errors → Check the logs in Koyeb dashboard

---

## 🔧 Troubleshooting

### Error: "password authentication failed"
- **Fix**: Double-check the password is COMPLETE and EXACT from Koyeb

### Error: "could not connect to server"
- **Fix**: Verify the HOST is correct (should end with `.pg.koyeb.app`)

### Error: "SSL required"
- **Fix**: Already handled in your `database.py` (line 64: `sslmode='require'`)

### Tables not created
- **Fix**: Check that `schema_pg.sql` exists in your project root

---

## ✅ Quick Verification Steps

Run through this checklist:

- [ ] Database "koyebdb" exists in Koyeb (YES - I see it in your screenshot!)
- [ ] Full password copied from Koyeb
- [ ] Environment variables added to Koyeb App
- [ ] App redeployed successfully
- [ ] App logs show "POSTGRES DB READY"
- [ ] Can register and login on website

---

## 📋 Next Steps After Database is Connected

Once your database is working:

1. **Test all features**: Registration, login, chat matching
2. **Monitor logs**: Check for any database errors
3. **Scaling**: Koyeb can handle high traffic automatically
4. **Backups**: Koyeb manages automatic backups for you

Your app is configured perfectly for production! 🚀
