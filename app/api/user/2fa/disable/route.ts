import { NextRequest, NextResponse } from 'next/server';
import { adminDb } from '@/lib/firebase-admin';
import jwt from 'jsonwebtoken';

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Authorization token required' }, { status: 401 });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };
    const userId = decoded.userId;

    // Update user document
    await adminDb.collection('users').doc(userId).update({
      is2FAEnabled: false,
      twoFactorMethod: null,
      updatedAt: new Date()
    });

    return NextResponse.json({
      success: true,
      message: '2FA disabled'
    });

  } catch (error: any) {
    console.error('Disable 2FA error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to disable 2FA' },
      { status: 500 }
    );
  }
}

