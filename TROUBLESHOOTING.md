# Troubleshooting Guide

## Error: CONFIGURATION_NOT_FOUND

This error means Firebase can't find your project configuration. Here's how to fix it:

### Step 1: Verify Your .env.local File

Make sure your `.env.local` file exists and has all required variables:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyBQJfiYT1p35ePNtfa5ItnH7HNz35_HWXc
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=edpearapi.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=edpearapi
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=edpearapi.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=436821138832
NEXT_PUBLIC_FIREBASE_APP_ID=1:436821138832:web:018370f0cfef4d6107e715
```

### Step 2: Verify Firebase Authentication is Enabled

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: **edpearapi**
3. Go to **Authentication** in the left menu
4. Click **Get Started** if you haven't enabled it yet
5. Go to the **Sign-in method** tab
6. Make sure **Email/Password** is enabled
   - Click on **Email/Password**
   - Toggle it to **Enabled**
   - Click **Save**

### Step 3: Verify API Key is Correct

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: **edpearapi**
3. Click ⚙️ → **Project Settings**
4. Scroll down to **Your apps** section
5. Find your web app (or create one if it doesn't exist)
6. Copy the **API Key** from the config
7. Make sure it matches what's in your `.env.local` file

### Step 4: Restart Your Development Server

After making changes to `.env.local`:

```bash
# Stop the server (Ctrl+C)
npm run dev
```

### Step 5: Verify Environment Variables are Loaded

Add a temporary debug route to check if variables are loaded:

Create `app/api/debug/env/route.ts`:
```typescript
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    hasApiKey: !!process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    apiKeyPrefix: process.env.NEXT_PUBLIC_FIREBASE_API_KEY?.substring(0, 10) + '...',
    hasProjectId: !!process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  });
}
```

Then visit: `http://localhost:3000/api/debug/env`

You should see your API key prefix and project ID. If not, your `.env.local` file isn't being loaded.

## Common Issues

### Issue: "Firebase API key is not configured"

**Solution:** Make sure your `.env.local` file:
- Exists in the root directory
- Has `NEXT_PUBLIC_FIREBASE_API_KEY` set
- Doesn't have any extra spaces or quotes around the value
- Server was restarted after adding the variable

### Issue: "An account with this email already exists"

**Solution:** The email is already registered. Try logging in instead, or use a different email.

### Issue: "Invalid email or password"

**Solution:** 
- Check that the email and password are correct
- Make sure the user exists in Firebase Authentication
- Try resetting the password from Firebase Console

### Issue: Firebase Admin initialization fails

**Solution:**
1. Make sure you've downloaded the service account JSON file
2. Extract the private key correctly (see `FIREBASE_KEY_FIX.md`)
3. Make sure the private key is wrapped in quotes in `.env.local`
4. Restart the server after updating `.env.local`

## Still Having Issues?

1. **Check Firebase Console:**
   - Is Authentication enabled?
   - Is Email/Password sign-in method enabled?
   - Does your project have the correct API key?

2. **Check Your Code:**
   - Is `.env.local` in the root directory?
   - Are all environment variables set?
   - Did you restart the server after changes?

3. **Check Network:**
   - Are you able to access Firebase services?
   - Is there a firewall blocking requests?

4. **Verify Project Settings:**
   - Go to Firebase Console → Project Settings
   - Verify all the configuration values match your `.env.local` file
