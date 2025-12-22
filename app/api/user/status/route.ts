import { NextRequest, NextResponse } from 'next/server';
import { ApiService } from '@/lib/api-service';
import { adminDb } from '@/lib/firebase-admin';

export async function GET(request: NextRequest) {
  try {
    const apiKey = request.headers.get('x-api-key');
    
    if (!apiKey) {
      return NextResponse.json(
        { error: 'API key is required' },
        { status: 401 }
      );
    }

    // Validate API key
    const keyValidation = await ApiService.validateApiKey(apiKey);
    if (!keyValidation.isValid || !keyValidation.userId) {
      return NextResponse.json(
        { error: 'Invalid API key' },
        { status: 401 }
      );
    }

    // Get user data from Firestore
    const userDoc = await adminDb.collection('users').doc(keyValidation.userId).get();
    
    if (!userDoc.exists) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    const userData = userDoc.data();

    return NextResponse.json({
      success: true,
      credits: userData?.credits || 0,
      user: {
        id: keyValidation.userId,
        name: userData?.name,
        email: userData?.email,
      },
    });
  } catch (error: any) {
    console.error('Get status error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to get status' },
      { status: 500 }
    );
  }
}
