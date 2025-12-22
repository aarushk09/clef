import { NextRequest, NextResponse } from 'next/server';
import { createUserWithEmailAndPassword } from '@/lib/firebase-auth-api';
import { adminDb } from '@/lib/firebase-admin';
import { User } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const { email, password, name } = await request.json();

    if (!email || !password || !name) {
      return NextResponse.json(
        { error: 'Email, password, and name are required' },
        { status: 400 }
      );
    }

    // Create user with Firebase Auth REST API
    const userCredential = await createUserWithEmailAndPassword(email, password);

    // Create user document in Firestore using Admin SDK syntax
    const userData: Omit<User, 'id'> = {
      email,
      name,
      credits: 100, // Starting credits
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    await adminDb.collection('users').doc(userCredential.uid).set(userData);

    return NextResponse.json({
      success: true,
      user: {
        id: userCredential.uid,
        ...userData,
      },
    });
  } catch (error: any) {
    console.error('Registration error:', error);
    return NextResponse.json(
      { error: error.message || 'Registration failed' },
      { status: 500 }
    );
  }
}
