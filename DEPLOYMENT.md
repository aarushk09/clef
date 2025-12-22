# EdPear Deployment Guide

This guide covers deploying the EdPear platform to production.

## Prerequisites

- Node.js 18+ and npm
- Firebase project with Firestore enabled
- Groq API account
- Domain name (optional)

## Environment Setup

### 1. Firebase Configuration

1. Create a Firebase project at [https://console.firebase.google.com](https://console.firebase.google.com)
2. Enable Authentication (Email/Password)
3. Enable Firestore Database
4. Generate service account key
5. Update environment variables:

```bash
# Copy the example file
cp env.example .env.local

# Edit with your Firebase credentials
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

# Firebase Admin (Server-side)
FIREBASE_ADMIN_PROJECT_ID=your_project_id
FIREBASE_ADMIN_CLIENT_EMAIL=your_service_account_email
FIREBASE_ADMIN_PRIVATE_KEY=your_private_key
```

### 2. API Configuration

```bash
# NextAuth Configuration
NEXTAUTH_URL=https://your-domain.com
NEXTAUTH_SECRET=your_nextauth_secret

# Groq API (Hidden from client)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct

# JWT Secret for API keys
JWT_SECRET=your_jwt_secret
```

## Local Development

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Production Deployment

### Option 1: Vercel (Recommended)

1. **Connect Repository**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Deploy
   vercel
   ```

2. **Configure Environment Variables**
   - Go to Vercel dashboard
   - Add all environment variables from `.env.local`
   - Redeploy

3. **Custom Domain** (Optional)
   - Add domain in Vercel dashboard
   - Update DNS records

### Option 2: Docker

1. **Create Dockerfile**
   ```dockerfile
   FROM node:18-alpine
   
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production
   
   COPY . .
   RUN npm run build
   
   EXPOSE 3000
   CMD ["npm", "start"]
   ```

2. **Build and Run**
   ```bash
   docker build -t edpear .
   docker run -p 3000:3000 --env-file .env.local edpear
   ```

### Option 3: Traditional Hosting

1. **Build Application**
   ```bash
   npm run build
   ```

2. **Deploy Files**
   - Upload `out/` directory to your hosting provider
   - Configure server to serve static files
   - Set up API routes if needed

## Database Setup

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // API keys are private to the user
    match /apiKeys/{keyId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
    
    // API requests are private to the user
    match /apiRequests/{requestId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
  }
}
```

### Firestore Indexes

Create the following indexes in Firestore:

```javascript
// Collection: apiRequests
// Fields: userId (Ascending), timestamp (Descending)

// Collection: apiKeys  
// Fields: userId (Ascending), createdAt (Descending)
```

## CLI and SDK Publishing

### 1. Publish CLI

```bash
cd edpear-cli
npm publish
```

### 2. Publish SDK

```bash
cd edpear-sdk
npm publish
```

## Monitoring and Analytics

### 1. Error Tracking

Add error tracking service:

```bash
npm install @sentry/nextjs
```

### 2. Analytics

Add analytics service:

```bash
npm install @vercel/analytics
```

### 3. Logging

Set up structured logging:

```bash
npm install winston
```

## Security Considerations

### 1. API Key Security

- Store API keys securely
- Use environment variables
- Implement rate limiting
- Monitor usage patterns

### 2. Data Protection

- Encrypt sensitive data
- Implement proper access controls
- Regular security audits
- GDPR compliance

### 3. Infrastructure Security

- Use HTTPS everywhere
- Implement CORS properly
- Regular dependency updates
- Security headers

## Performance Optimization

### 1. Caching

- Implement Redis for session storage
- Cache API responses
- Use CDN for static assets

### 2. Database Optimization

- Proper indexing
- Query optimization
- Connection pooling

### 3. API Optimization

- Request batching
- Response compression
- Rate limiting

## Backup and Recovery

### 1. Database Backups

- Automated Firestore backups
- Regular export schedules
- Cross-region replication

### 2. Code Backups

- Git repository backups
- Automated deployments
- Rollback procedures

## Scaling Considerations

### 1. Horizontal Scaling

- Load balancers
- Multiple instances
- Auto-scaling groups

### 2. Database Scaling

- Read replicas
- Sharding strategies
- Caching layers

### 3. API Scaling

- Rate limiting
- Request queuing
- Circuit breakers

## Maintenance

### 1. Regular Updates

- Dependency updates
- Security patches
- Feature updates

### 2. Monitoring

- Health checks
- Performance monitoring
- Error tracking

### 3. Documentation

- API documentation
- User guides
- Developer resources

## Troubleshooting

### Common Issues

1. **Firebase Connection Issues**
   - Check credentials
   - Verify project settings
   - Check network connectivity

2. **API Key Issues**
   - Verify Groq API key
   - Check rate limits
   - Monitor usage

3. **Authentication Issues**
   - Check Firebase Auth setup
   - Verify JWT secrets
   - Check token expiration

### Support

- Documentation: [https://docs.edpear.com](https://docs.edpear.com)
- Support: [support@edpear.com](mailto:support@edpear.com)
- GitHub Issues: [https://github.com/edpear/issues](https://github.com/edpear/issues)
