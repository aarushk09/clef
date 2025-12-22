import { initializeApp, getApps, cert } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import { getAuth } from 'firebase-admin/auth';

// Format private key properly
function formatPrivateKey(key: string | undefined): string | undefined {
  if (!key) return undefined;
  
  // Remove surrounding quotes if present
  let formattedKey = key.trim().replace(/^["']|["']$/g, '');
  
  // Replace literal \n with actual newlines
  formattedKey = formattedKey.replace(/\\n/g, '\n');
  
  // Remove any existing PEM headers to start fresh
  formattedKey = formattedKey
    .replace(/-----BEGIN PRIVATE KEY-----/g, '')
    .replace(/-----END PRIVATE KEY-----/g, '')
    .replace(/-----BEGIN RSA PRIVATE KEY-----/g, '')
    .replace(/-----END RSA PRIVATE KEY-----/g, '')
    .trim();
  
  // Remove all whitespace and newlines from the key content
  const keyContent = formattedKey.replace(/\s+/g, '');
  
  // Split into 64-character lines for proper PEM format
  const lines: string[] = [];
  for (let i = 0; i < keyContent.length; i += 64) {
    lines.push(keyContent.substring(i, i + 64));
  }
  
  // Reconstruct with proper PEM headers and line breaks
  formattedKey = `-----BEGIN PRIVATE KEY-----\n${lines.join('\n')}\n-----END PRIVATE KEY-----`;
  
  return formattedKey;
}

const firebaseAdminConfig = {
  projectId: process.env.FIREBASE_ADMIN_PROJECT_ID,
  clientEmail: process.env.FIREBASE_ADMIN_CLIENT_EMAIL,
  privateKey: formatPrivateKey(process.env.FIREBASE_ADMIN_PRIVATE_KEY),
};

// Validate configuration
if (!firebaseAdminConfig.projectId || !firebaseAdminConfig.clientEmail || !firebaseAdminConfig.privateKey) {
  console.warn('⚠️  Firebase Admin configuration is incomplete. Some features may not work.');
  console.warn('Please check your .env.local file has all Firebase Admin credentials.');
}

// Initialize Firebase Admin
let adminApp: any;
const isConfigValid = firebaseAdminConfig.projectId && firebaseAdminConfig.clientEmail && firebaseAdminConfig.privateKey;

if (isConfigValid) {
  try {
    adminApp = getApps().length === 0 
      ? initializeApp({
          credential: cert(firebaseAdminConfig as any),
          projectId: process.env.FIREBASE_ADMIN_PROJECT_ID,
        })
      : getApps()[0];
  } catch (error: any) {
    console.error('❌ Firebase Admin initialization failed:', error.message);
    
    // If formatting failed, try using the key directly from JSON format
    if (error.message.includes('private key') || error.message.includes('DER')) {
      console.warn('⚠️  Attempting to use private key in JSON format...');
      
      const rawKey = process.env.FIREBASE_ADMIN_PRIVATE_KEY;
      if (rawKey) {
        try {
          const directConfig = {
            projectId: process.env.FIREBASE_ADMIN_PROJECT_ID,
            clientEmail: process.env.FIREBASE_ADMIN_CLIENT_EMAIL,
            privateKey: rawKey.replace(/\\n/g, '\n'),
          };
          
          adminApp = getApps().length === 0 
            ? initializeApp({
                credential: cert(directConfig as any),
                projectId: process.env.FIREBASE_ADMIN_PROJECT_ID,
              })
            : getApps()[0];
          
          console.log('✅ Firebase Admin initialized with direct key format');
        } catch (fallbackError: any) {
          console.error('❌ Fallback initialization also failed:', fallbackError.message);
        }
      }
    }
  }
} else {
  // During build time or if env vars are missing
  adminApp = getApps().length > 0 ? getApps()[0] : null;
}

export const adminDb = adminApp ? getFirestore(adminApp) : (null as any);
export const adminAuth = adminApp ? getAuth(adminApp) : (null as any);
export default adminApp;
