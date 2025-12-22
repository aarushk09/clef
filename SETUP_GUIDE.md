# EdPear Setup Guide - Finding Your Secrets

This guide will help you find all the required secrets and API keys for your EdPear platform.

## 🔥 Firebase Admin Credentials

### Step-by-Step Instructions:

1. **Go to Firebase Console**
   - Visit: https://console.firebase.google.com
   - Sign in with your Google account

2. **Select Your Project**
   - Click on your project: **edpearapi**

3. **Open Project Settings**
   - Click the gear icon ⚙️ next to "Project Overview"
   - Select "Project settings"

4. **Navigate to Service Accounts**
   - Click on the "Service accounts" tab
   - You'll see options for Node.js, Python, and Java

5. **Generate Private Key**
   - Click the "Generate new private key" button
   - A warning dialog will appear - click "Generate key"
   - A JSON file will be downloaded (e.g., `edpearapi-firebase-adminsdk-xxxxx.json`)

6. **Extract Values from JSON**
   Open the downloaded JSON file and extract:
   ```json
   {
     "project_id": "edpearapi",  // -> FIREBASE_ADMIN_PROJECT_ID
     "client_email": "firebase-adminsdk-xxxxx@edpearapi.iam.gserviceaccount.com",  // -> FIREBASE_ADMIN_CLIENT_EMAIL
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"  // -> FIREBASE_ADMIN_PRIVATE_KEY
   }
   ```

7. **Add to .env.local**
   ```env
   FIREBASE_ADMIN_PROJECT_ID=edpearapi
   FIREBASE_ADMIN_CLIENT_EMAIL=firebase-adminsdk-xxxxx@edpearapi.iam.gserviceaccount.com
   FIREBASE_ADMIN_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   ```
   
   **Important:** Keep the quotes around the private key and preserve the `\n` characters!

## 🔐 NextAuth Secret

The NextAuth secret is used to encrypt cookies and tokens. You need to generate a random string.

### Option 1: Using OpenSSL (Recommended)
```bash
openssl rand -base64 32
```

### Option 2: Online Generator
Visit: https://generate-secret.vercel.app/32

### Option 3: Using Node.js
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### Option 4: PowerShell (Windows)
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

**Add to .env.local:**
```env
NEXTAUTH_SECRET=your_generated_32_character_random_string
```

## 🔑 JWT Secret for API Keys

This secret is used to sign and verify JWT tokens for API key authentication. Generate a different random string from your NextAuth secret.

### Generate Using Same Methods as NextAuth Secret

**Option 1: OpenSSL**
```bash
openssl rand -base64 32
```

**Option 2: Online Generator**
Visit: https://generate-secret.vercel.app/32

**Add to .env.local:**
```env
JWT_SECRET=your_different_generated_32_character_random_string
```

**Important:** This should be a DIFFERENT value from `NEXTAUTH_SECRET`!

## 📝 Complete .env.local Setup

1. **Copy the example file:**
   ```bash
   cp env.example .env.local
   ```

2. **Fill in the missing values:**
   - Firebase Admin credentials (from JSON file)
   - NextAuth secret (generate random string)
   - JWT secret (generate different random string)

3. **Your final .env.local should look like:**
   ```env
   # Firebase Configuration (Already filled)
   NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyBQJfiYT1p35ePNtfa5ItnH7HNz35_HWXc
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=edpearapi.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=edpearapi
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=edpearapi.firebasestorage.app
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=436821138832
   NEXT_PUBLIC_FIREBASE_APP_ID=1:436821138832:web:018370f0cfef4d6107e715
   NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-Z6WTKLQK2R

   # Firebase Admin (Fill from JSON)
   FIREBASE_ADMIN_PROJECT_ID=edpearapi
   FIREBASE_ADMIN_CLIENT_EMAIL=firebase-adminsdk-xxxxx@edpearapi.iam.gserviceaccount.com
   FIREBASE_ADMIN_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

   # NextAuth (Generate random string)
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your_generated_secret_here

   # Groq API (Get your key from https://console.groq.com)
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct

   # JWT Secret (Generate different random string)
   JWT_SECRET=your_different_generated_secret_here
   ```

## ✅ Verification Checklist

- [ ] Firebase Admin credentials extracted from JSON file
- [ ] NextAuth secret generated and added
- [ ] JWT secret generated (different from NextAuth secret) and added
- [ ] All Firebase public keys are correct
- [ ] Groq API key is set
- [ ] .env.local file is created (not committed to git)

## 🚨 Security Notes

1. **Never commit .env.local to git** - It's already in .gitignore
2. **Keep secrets secure** - Don't share them publicly
3. **Use different secrets** - NextAuth and JWT secrets should be different
4. **Rotate secrets regularly** - Especially if compromised
5. **Use environment-specific secrets** - Different secrets for dev/staging/prod

## 🆘 Troubleshooting

### Firebase Admin Issues
- **Error: "Invalid credentials"** - Check that the private key includes the full key with `\n` characters
- **Error: "Permission denied"** - Make sure the service account has proper permissions in Firebase

### NextAuth Issues
- **Error: "Invalid secret"** - Make sure the secret is at least 32 characters
- **Error: "Cookies not working"** - Check NEXTAUTH_URL matches your domain

### JWT Issues
- **Error: "Invalid token"** - Verify JWT_SECRET is set correctly
- **Error: "Token expired"** - Check token expiration settings

## 📞 Need Help?

If you're still having issues:
1. Check the Firebase Console for any service account errors
2. Verify all environment variables are set correctly
3. Make sure there are no extra spaces or quotes in your .env.local file
4. Restart your development server after making changes

---

**Quick Reference:**
- Firebase Admin: Firebase Console → Project Settings → Service Accounts
- NextAuth Secret: Generate with `openssl rand -base64 32`
- JWT Secret: Generate with `openssl rand -base64 32` (different from NextAuth)

## 📦 Library Installation

The EdPear SDK and CLI are now combined into a single package for easier installation.

```bash
# Install the library
npm install @edpear/sdk

# Login to your account
npx edpear login

# Generate an API key
npx edpear generate-key
```
