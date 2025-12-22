# Firebase Private Key Format Guide

## The Issue
Firebase private keys need to be properly formatted in your `.env.local` file. The key from the JSON file needs special handling.

## Solution

### Option 1: Use the Key with Quotes (Recommended)

In your `.env.local` file, wrap the private key in quotes and keep the `\n` characters:

```env
FIREBASE_ADMIN_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/F6kTisxP+l/M\nSnmCVYDkMueXXVdNFjR04yMnLa/lGpQOvA+5ewDcUR/cSjUmmBMshd8ZMhGh1746\n...rest of key...\n-----END PRIVATE KEY-----"
```

### Option 2: Use the Raw Key (Code Will Format It)

If your key doesn't have the PEM headers, you can use just the raw key. The code will automatically add the headers:

```env
FIREBASE_ADMIN_PRIVATE_KEY=MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/F6kTisxP+l/M\nSnmCVYDkMueXXVdNFjR04yMnLa/lGpQOvA+5ewDcUR/cSjUmmBMshd8ZMhGh1746\n...rest of key...
```

**Important:** Keep the `\n` characters as literal text - they will be converted to actual newlines by the code.

### Option 3: Use the Full JSON Value

Copy the `private_key` value exactly as it appears in the JSON file (it should already have the headers):

```env
FIREBASE_ADMIN_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/F6kTisxP+l/M\nSnmCVYDkMueXXVdNFjR04yMnLa/lGpQOvA+5ewDcUR/cSjUmmBMshd8ZMhGh1746\n0yt3G5sjRu3Ey/onx/TD8RrE9vdgVj6lqnj6Q1QKaVcjxzza84p1QznPgzqblPHl\n6SMnOyLGNhmgROAJhE9oBAIs0vGAK909UwNW5uvuqeiKM7RltnrWqJRlRUg3CZ8E\nVa6PPBKkNO/iHMTjJMQhkksgDLQ2wd6RN6gaxkOyPbVp+ESmfDCgX1T5z50Nca9q\nY4UI8zjcyRSG530OeYGfv0zd/Zpn0/9X5IQgm1GjEPBx59mEB5RRAlhQmEo0VQyS\nHwXieBFLAgMBAAECggEAUgaSfYB5ViVXpMYdJVyVgJ73OUqIVF8hMkFjkAg09id0\nAWUpbMlHY8rw3ar+6Kujo1ttmg+bcPi+P9rwT+bKL5jdLDoQja3vu4INpxmJs1Ei\nABPObUKkWvm/vWxjC2s59j7enFwstqb3NOTfwZHJSgLj+h9Ged9RBImf82Sy5Hxx\nlPcdA7zBMxPUKKsVdqL74UBcLZCVyuJkxO7qnSqyUlP+qRoquP6icUmM88XUQYLN\nDE+kCN9AkcVlUM6UdYrQxbA+GzjvYqPMhO1AOFqcbXTDGlUKW41QlU3ClOL3BgGA\nZrOHh/87wE/PiE2z8UM64yp+EtHn9G8ADIcO19vUwQKBgQDoVt+ugmRoEXMGj/sr\nSDUYP41fcWMtUX0YyFVek66ehopp+c4ckbicX3MovQV4g0F0SzD02WZzUXyrx1W8\nkW95JOwgMiI9r68/balAg7zFiLPa2tgViehjqGUsUi8sXm0QvKxgaPHDi/ccRpnG\n99EnQjQzy1GEQpU6SLRJFeckQQKBgQDSjXjqGvOOrl8LQERNBUbd3OW/s+8tvkjm\nZHHsJPuJrtU3ZTG+U0HomFam54TVMcBpQy0V/v/8VyUHabuYbfI8sJJjvKbtvKdl\nHp+DEITTx64UVogJ0nnYyTmYYl5ZWjhSdJ4COWVQxxw7jfiK8U3jqR8hrIoC8aLO\nTPlfunbiiwKBgQDTAhMj6khGO5K74we5x1pxK0a558Cq59c1KrxdqMJuNsJ+fOE0zESQY4Jc16HWPfaV0eNV9ifQBx3/ygpbbKzqSS3Ynx2BRpb0DXhTZAsvumri9iwO0\njAsCd21rUziEkz16deAXrzfi4LsMcxI2IdtSTE4cvArMk6vzwxP5TGsgAQKBgQC1\neJOfim0jK6zlQJXdoE+tByfJq2bZESk50ZbSxik6SMKiRQizloS22R3OKrs1GPVS\nhECGtcqiDeXvVrUGMrTWlAUIC2AAhVntcJBg4UrqUS77fn0vogW8z+phKV9SOc1T\nXAmXtypYjdQKjFmMP2A3eNtJJbGpyePdVUCVvlua8wKBgA8ctNc1ECofYiZrU8cV\npgg1nFqwUa66H47YdOT3ncU2adLQdJCqjg9CEocsH7ZUIfmY4Ww9A0vTw0Dh8kZa\no4q8aEl23pLVFwtgxitn9dao1LerwAt+xdlklJWezODxRyriyR+/pLjliwina6do\nJjIDwhwKbj1YdgT1FlrDZEUg\n-----END PRIVATE KEY-----"
```

## Your Current Key

Based on what you provided, your `.env.local` should have:

```env
FIREBASE_ADMIN_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/F6kTisxP+l/M\nSnmCVYDkMueXXVdNFjR04yMnLa/lGpQOvA+5ewDcUR/cSjUmmBMshd8ZMhGh1746\n0yt3G5sjRu3Ey/onx/TD8RrE9vdgVj6lqnj6Q1QKaVcjxzza84p1QznPgzqblPHl\n6SMnOyLGNhmgROAJhE9oBAIs0vGAK909UwNW5uvuqeiKM7RltnrWqJRlRUg3CZ8E\nVa6PPBKkNO/iHMTjJMQhkksgDLQ2wd6RN6gaxkOyPbVp+ESmfDCgX1T5z50Nca9q\nY4UI8zjcyRSG530OeYGfv0zd/Zpn0/9X5IQgm1GjEPBx59mEB5RRAlhQmEo0VQyS\nHwXieBFLAgMBAAECggEAUgaSfYB5ViVXpMYdJVyVgJ73OUqIVF8hMkFjkAg09id0\nAWUpbMlHY8rw3ar+6Kujo1ttmg+bcPi+P9rwT+bKL5jdLDoQja3vu4INpxmJs1Ei\nABPObUKkWvm/vWxjC2s59j7enFwstqb3NOTfwZHJSgLj+h9Ged9RBImf82Sy5Hxx\nlPcdA7zBMxPUKKsVdqL74UBcLZCVyuJkxO7qnSqyUlP+qRoquP6icUmM88XUQYLN\nDE+kCN9AkcVlUM6UdYrQxbA+GzjvYqPMhO1AOFqcbXTDGlUKW41QlU3ClOL3BgGA\nZrOHh/87wE/PiE2z8UM64yp+EtHn9G8ADIcO19vUwQKBgQDoVt+ugmRoEXMGj/sr\nSDUYP41fcWMtUX0YyFVek66ehopp+c4ckbicX3MovQV4g0F0SzD02WZzUXyrx1W8\nkW95JOwgMiI9r68/balAg7zFiLPa2tgViehjqGUsUi8sXm0QvKxgaPHDi/ccRpnG\n99EnQjQzy1GEQpU6SLRJFeckQQKBgQDSjXjqGvOOrl8LQERNBUbd3OW/s+8tvkjm\nZHHsJPuJrtU3ZTG+U0HomFam54TVMcBpQy0V/v/8VyUHabuYbfI8sJJjvKbtvKdl\nHp+DEITTx64UVogJ0nnYyTmYYl5ZWjhSdJ4COWVQxxw7jfiK8U3jqR8hrIoC8aLO\nTPlfunbiiwKBgQDTAhMj6khGO5K74we5x1pxK0a558Cq59c1KrxdqMJuNsJ+fOE0zESQY4Jc16HWPfaV0eNV9ifQBx3/ygpbbKzqSS3Ynx2BRpb0DXhTZAsvumri9iwO0\njAsCd21rUziEkz16deAXrzfi4LsMcxI2IdtSTE4cvArMk6vzwxP5TGsgAQKBgQC1\neJOfim0jK6zlQJXdoE+tByfJq2bZESk50ZbSxik6SMKiRQizloS22R3OKrs1GPVS\nhECGtcqiDeXvVrUGMrTWlAUIC2AAhVntcJBg4UrqUS77fn0vogW8z+phKV9SOc1T\nXAmXtypYjdQKjFmMP2A3eNtJJbGpyePdVUCVvlua8wKBgA8ctNc1ECofYiZrU8cV\npgg1nFqwUa66H47YdOT3ncU2adLQdJCqjg9CEocsH7ZUIfmY4Ww9A0vTw0Dh8kZa\no4q8aEl23pLVFwtgxitn9dao1LerwAt+xdlklJWezODxRyriyR+/pLjliwina6do\nJjIDwhwKbj1YdgT1FlrDZEUg\n-----END PRIVATE KEY-----"
```

**Note:** Make sure to:
1. Wrap the entire value in double quotes `"`
2. Keep all the `\n` characters as literal text
3. Include the BEGIN and END markers if they're in your JSON file

## Testing

After updating your `.env.local` file:
1. Restart your development server
2. Try registering a user again
3. Check the console for any error messages

If you still get errors, the key might be incomplete. In that case, regenerate the private key from Firebase Console.
