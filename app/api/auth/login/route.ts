import { NextRequest, NextResponse } from 'next/server';
import { signInWithEmailAndPassword } from '@/lib/firebase-auth-api';
import { adminDb } from '@/lib/firebase-admin';
import jwt from 'jsonwebtoken';

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required' },
        { status: 400 }
      );
    }

    // Sign in with Firebase Auth REST API
    const userCredential = await signInWithEmailAndPassword(email, password);

    // Get user data from Firestore using Admin SDK syntax
    const userDoc = await adminDb.collection('users').doc(userCredential.uid).get();
    
    if (!userDoc.exists) {
      return NextResponse.json(
        { error: 'User data not found' },
        { status: 404 }
      );
    }

    const userData = userDoc.data();

    // Create JWT token
    const token = jwt.sign(
      { userId: userCredential.uid, email: userCredential.email },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    );

    return NextResponse.json({
      success: true,
      user: {
        id: userCredential.uid,
        ...userData,
      },
      token,
    });
  } catch (error: any) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: error.message || 'Login failed' },
      { status: 500 }
    );
  }
}
