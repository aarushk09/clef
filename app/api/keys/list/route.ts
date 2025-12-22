import { NextRequest, NextResponse } from 'next/server';
import { adminDb } from '@/lib/firebase-admin';
import jwt from 'jsonwebtoken';

export async function GET(request: NextRequest) {
  try {
    // Get user from JWT token
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Authorization token required' },
        { status: 401 }
      );
    }

    const token = authHeader.substring(7);
    
    // Verify JWT token
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string; email: string };
    const userId = decoded.userId;

    // Get all API keys for this user
    const apiKeysSnapshot = await adminDb
      .collection('apiKeys')
      .where('userId', '==', userId)
      .orderBy('createdAt', 'desc')
      .get();

    const apiKeys = apiKeysSnapshot.docs.map((doc: any) => {
      const data = doc.data();
      return {
        id: doc.id,
        name: data.name,
        key: data.key.substring(0, 20) + '...', // Only show first 20 chars for security
        isActive: data.isActive,
        createdAt: data.createdAt?.toDate?.() || data.createdAt,
        lastUsed: data.lastUsed?.toDate?.() || data.lastUsed,
        usageCount: data.usageCount || 0,
      };
    });

    return NextResponse.json({
      success: true,
      apiKeys,
    });
  } catch (error: any) {
    if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
      return NextResponse.json(
        { error: 'Invalid or expired token' },
        { status: 401 }
      );
    }
    
    console.error('List API keys error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to list API keys' },
      { status: 500 }
    );
  }
}
