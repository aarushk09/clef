# Fixing Google Cloud IAM Permissions Error

## The Problem

The error indicates that your Firebase service account doesn't have permission to use the Identity Toolkit API. This is a Google Cloud IAM permissions issue.

## Solution 1: Grant Required Permissions (Recommended)

### Step 1: Enable Identity Toolkit API

1. Go to [Google Cloud Console - APIs & Services](https://console.cloud.google.com/apis/library)
2. Select your project: **edpearapi**
3. Search for **"Identity Toolkit API"**
4. Click on it and click **"Enable"**

### Step 2: Grant Service Account Permissions

1. Go to [Google Cloud Console - IAM & Admin](https://console.cloud.google.com/iam-admin/iam?project=edpearapi)
2. Find your service account: `firebase-adminsdk-fbsvc@edpearapi.iam.gserviceaccount.com`
3. Click the **pencil icon** (Edit) next to it
4. Click **"Add Another Role"**
5. Add these roles:
   - `Service Usage Consumer` (roles/serviceusage.serviceUsageConsumer)
   - `Firebase Admin SDK Administrator Service Agent` (if available)
6. Click **"Save"**

### Step 3: Wait for Propagation

Permissions can take a few minutes to propagate. Wait 2-3 minutes, then try again.

## Solution 2: Use Public API Key Instead (Alternative)

If you can't modify IAM permissions, we can modify the code to use the public API key for sign-in instead of the service account. However, this is less secure for user creation.

Let me know if you want me to implement this alternative approach.

## Solution 3: Enable APIs via Firebase Console

Sometimes enabling APIs through Firebase Console is easier:

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: **edpearapi**
3. Go to **Project Settings** (gear icon)
4. Scroll down to **"Your apps"** section
5. Make sure you have a **Web app** configured
6. The APIs should be automatically enabled when you create a web app

## Verification

After making changes:

1. Wait 2-3 minutes for permissions to propagate
2. Restart your development server:
   ```bash
   npm run dev
   ```
3. Try registering a user again

## Quick Fix Script

If you have `gcloud` CLI installed:

```bash
# Enable Identity Toolkit API
gcloud services enable identitytoolkit.googleapis.com --project=edpearapi

# Grant service account the required role
gcloud projects add-iam-policy-binding edpearapi \
  --member="serviceAccount:firebase-adminsdk-fbsvc@edpearapi.iam.gserviceaccount.com" \
  --role="roles/serviceusage.serviceUsageConsumer"
```

## Still Having Issues?

If you're still getting permission errors:

1. **Check if you're the project owner:**
   - Go to [IAM & Admin](https://console.cloud.google.com/iam-admin/iam?project=edpearapi)
   - Make sure your account has "Owner" or "Editor" role

2. **Try using a different approach:**
   - We can modify the code to use the public API key for authentication
   - This doesn't require service account permissions

3. **Contact your project administrator:**
   - If you don't have permission to modify IAM roles, ask your project admin to grant the required permissions
