# Fixing Firebase Private Key Error

## Quick Fix

The error "Unparsed DER bytes remain after ASN.1 parsing" means the private key format is incorrect. Here's how to fix it:

### Option 1: Use the Helper Script (Easiest)

1. Download your Firebase service account JSON file from Firebase Console
2. Run the extraction script:
   ```bash
   node scripts/extract-firebase-key.js path/to/your-service-account-key.json
   ```
3. Copy the output directly into your `.env.local` file

### Option 2: Manual Fix

1. **Open your Firebase service account JSON file** (the one you downloaded from Firebase Console)

2. **Find the `private_key` field** - it should look like this:
   ```json
   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/F6kTisxP+l/M\n...more lines...\n-----END PRIVATE KEY-----\n"
   ```

3. **Copy the ENTIRE value** including the quotes and `\n` characters

4. **In your `.env.local` file**, set it like this:
   ```env
   FIREBASE_ADMIN_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/F6kTisxP+l/M\n...rest of key...\n-----END PRIVATE KEY-----\n"
   ```

   **Important:**
   - Wrap the entire value in double quotes `"`
   - Keep all `\n` characters as literal text (don't convert to actual newlines)
   - Include the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` markers
   - The key should be on a single line in the .env file

### Option 3: Regenerate the Key

If the key is corrupted or incomplete:

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: **edpearapi**
3. Click ⚙️ → **Project Settings** → **Service accounts** tab
4. Click **"Generate new private key"**
5. Download the new JSON file
6. Use Option 1 or 2 above with the new file

## Your Current Key Format

Based on what you provided, your `.env.local` should have:

```env
FIREBASE_ADMIN_PROJECT_ID=edpearapi
FIREBASE_ADMIN_CLIENT_EMAIL=firebase-adminsdk-fbsvc@edpearapi.iam.gserviceaccount.com
FIREBASE_ADMIN_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/F6kTisxP+l/M\nSnmCVYDkMueXXVdNFjR04yMnLa/lGpQOvA+5ewDcUR/cSjUmmBMshd8ZMhGh1746\n0yt3G5sjRu3Ey/onx/TD8RrE9vdgVj6lqnj6Q1QKaVcjxzza84p1QznPgzqblPHl\n6SMnOyLGNhmgROAJhE9oBAIs0vGAK909UwNW5uvuqeiKM7RltnrWqJRlRUg3CZ8E\nVa6PPBKkNO/iHMTjJMQhkksgDLQ2wd6RN6gaxkOyPbVp+ESmfDCgX1T5z50Nca9q\nY4UI8zjcyRSG530OeYGfv0zd/Zpn0/9X5IQgm1GjEPBx59mEB5RRAlhQmEo0VQyS\nHwXieBFLAgMBAAECggEAUgaSfYB5ViVXpMYdJVyVgJ73OUqIVF8hMkFjkAg09id0\nAWUpbMlHY8rw3ar+6Kujo1ttmg+bcPi+P9rwT+bKL5jdLDoQja3vu4INpxmJs1Ei\nABPObUKkWvm/vWxjC2s59j7enFwstqb3NOTfwZHJSgLj+h9Ged9RBImf82Sy5Hxx\nlPcdA7zBMxPUKKsVdqL74UBcLZCVyuJkxO7qnSqyUlP+qRoquP6icUmM88XUQYLN\nDE+kCN9AkcVlUM6UdYrQxbA+GzjvYqPMhO1AOFqcbXTDGlUKW41QlU3ClOL3BgGA\nZrOHh/87wE/PiE2z8UM64yp+EtHn9G8ADIcO19vUwQKBgQDoVt+ugmRoEXMGj/sr\nSDUYP41fcWMtUX0YyFVek66ehopp+c4ckbicX3MovQV4g0F0SzD02WZzUXyrx1W8\nkW95JOwgMiI9r68/balAg7zFiLPa2tgViehjqGUsUi8sXm0QvKxgaPHDi/ccRpnG\n99EnQjQzy1GEQpU6SLRJFeckQQKBgQDSjXjqGvOOrl8LQERNBUbd3OW/s+8tvkjm\nZHHsJPuJrtU3ZTG+U0HomFam54TVMcBpQy0V/v/8VyUHabuYbfI8sJJjvKbtvKdl\nHp+DEITTx64UVogJ0nnYyTmYYl5ZWjhSdJ4COWVQxxw7jfiK8U3jqR8hrIoC8aLO\nTPlfunbiiwKBgQDTAhMj6khGO5K74we5x1pxK0a558Cq59c1KrxdqMJuNsJ+fOE0zESQY4Jc16HWPfaV0eNV9ifQBx3/ygpbbKzqSS3Ynx2BRpb0DXhTZAsvumri9iwO0\njAsCd21rUziEkz16deAXrzfi4LsMcxI2IdtSTE4cvArMk6vzwxP5TGsgAQKBgQC1\neJOfim0jK6zlQJXdoE+tByfJq2bZESk50ZbSxik6SMKiRQizloS22R3OKrs1GPVS\nhECGtcqiDeXvVrUGMrTWlAUIC2AAhVntcJBg4UrqUS77fn0vogW8z+phKV9SOc1T\nXAmXtypYjdQKjFmMP2A3eNtJJbGpyePdVUCVvlua8wKBgA8ctNc1ECofYiZrU8cV\npgg1nFqwUa66H47YdOT3ncU2adLQdJCqjg9CEocsH7ZUIfmY4Ww9A0vTw0Dh8kZa\no4q8aEl23pLVFwtgxitn9dao1LerwAt+xdlklJWezODxRyriyR+/pLjliwina6do\nJjIDwhwKbj1YdgT1FlrDZEUg\n-----END PRIVATE KEY-----\n"
```

**Note:** The key above might be incomplete. Make sure you copy the COMPLETE key from your JSON file.

## After Fixing

1. **Save your `.env.local` file**
2. **Restart your development server completely:**
   ```bash
   # Stop the server (Ctrl+C)
   # Then start again
   npm run dev
   ```
3. **Try registering a user again**

## Verification

If the key is correct, you should see:
- ✅ No errors in the console
- ✅ Successful user registration
- ✅ No "Failed to parse private key" errors

If you still get errors, the key might be:
- Incomplete (missing characters)
- Corrupted (wrong characters)
- From the wrong project

In that case, regenerate the key from Firebase Console.
