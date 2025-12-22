import axios from 'axios';
import { adminAuth, adminDb } from './firebase-admin';

const FIREBASE_API_KEY = process.env.NEXT_PUBLIC_FIREBASE_API_KEY;
const FIREBASE_AUTH_DOMAIN = process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN;

// Validate API key is available
if (!FIREBASE_API_KEY) {
  console.warn('⚠️  NEXT_PUBLIC_FIREBASE_API_KEY is not set in environment variables');
}

/**
 * Create a new user using Firebase Auth REST API
 * Using REST API instead of Admin SDK to avoid IAM permission issues
 */
export async function createUserWithEmailAndPassword(email: string, password: string) {
  if (!FIREBASE_API_KEY) {
    throw new Error('Firebase API key is not configured. Please check your environment variables.');
  }

  try {
    const response = await axios.post(
      `https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${FIREBASE_API_KEY}`,
      {
        email,
        password,
        returnSecureToken: true,
      }
    );

    return {
      uid: response.data.localId,
      email: response.data.email,
      idToken: response.data.idToken,
    };
  } catch (error: any) {
    if (error.response?.data?.error) {
      const errorCode = error.response.data.error.message;
      
      // Map Firebase error codes to user-friendly messages
      if (errorCode.includes('EMAIL_EXISTS')) {
        throw new Error('An account with this email already exists');
      } else if (errorCode.includes('INVALID_EMAIL')) {
        throw new Error('Invalid email address');
      } else if (errorCode.includes('WEAK_PASSWORD')) {
        throw new Error('Password is too weak. Please use at least 6 characters');
      } else if (errorCode.includes('CONFIGURATION_NOT_FOUND')) {
        throw new Error('Firebase configuration error. Please enable Authentication in Firebase Console.');
      } else if (errorCode.includes('PERMISSION_DENIED') || errorCode.includes('serviceusage')) {
        throw new Error('Firebase API permissions error. Please enable Identity Toolkit API in Google Cloud Console.');
      }
      
      throw new Error(errorCode || 'Registration failed');
    }
    throw new Error('Network error. Please try again.');
  }
}

/**
 * Sign in a user using Firebase Auth REST API
 */
export async function signInWithEmailAndPassword(email: string, password: string) {
  if (!FIREBASE_API_KEY) {
    throw new Error('Firebase API key is not configured. Please check your environment variables.');
  }

  try {
    const response = await axios.post(
      `https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${FIREBASE_API_KEY}`,
      {
        email,
        password,
        returnSecureToken: true,
      }
    );

    return {
      uid: response.data.localId,
      email: response.data.email,
      idToken: response.data.idToken,
    };
  } catch (error: any) {
    if (error.response?.data?.error) {
      const errorCode = error.response.data.error.message;
      
      // Map Firebase error codes to user-friendly messages
      if (errorCode.includes('EMAIL_NOT_FOUND') || errorCode.includes('INVALID_PASSWORD')) {
        throw new Error('Invalid email or password');
      } else if (errorCode.includes('USER_DISABLED')) {
        throw new Error('This account has been disabled');
      } else if (errorCode.includes('TOO_MANY_ATTEMPTS_TRY_LATER')) {
        throw new Error('Too many failed login attempts. Please try again later');
      } else if (errorCode.includes('CONFIGURATION_NOT_FOUND')) {
        throw new Error('Firebase configuration error. Please enable Authentication in Firebase Console.');
      } else if (errorCode.includes('PERMISSION_DENIED') || errorCode.includes('serviceusage')) {
        throw new Error('Firebase API permissions error. Please enable Identity Toolkit API in Google Cloud Console.');
      }
      
      throw new Error(errorCode || 'Login failed');
    }
    throw new Error('Network error. Please try again.');
  }
}

/**
 * Verify an ID token using Firebase Admin
 */
export async function verifyIdToken(idToken: string) {
  try {
    const decodedToken = await adminAuth.verifyIdToken(idToken);
    return decodedToken;
  } catch (error) {
    throw new Error('Invalid token');
  }
}
