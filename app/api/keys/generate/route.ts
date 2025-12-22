import { NextRequest, NextResponse } from 'next/server';
import { adminDb } from '@/lib/firebase-admin';
import { ApiKey } from '@/lib/types';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

export async function POST(request: NextRequest) {
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

    const { name } = await request.json();

    if (!name) {
      return NextResponse.json(
        { error: 'API key name is required' },
        { status: 400 }
      );
    }

    // Generate secure API key
    const apiKey = `edpear_${crypto.randomBytes(32).toString('hex')}`;
    const keyId = crypto.randomUUID();

    const apiKeyData: ApiKey = {
      id: keyId,
      userId,
      key: apiKey,
      name,
      isActive: true,
      createdAt: new Date(),
      usageCount: 0,
    };

    // Save to Firestore using Admin SDK syntax
    await adminDb.collection('apiKeys').doc(keyId).set(apiKeyData);

    return NextResponse.json({
      success: true,
      apiKey: {
        id: keyId,
        key: apiKey,
        name,
        createdAt: apiKeyData.createdAt,
      },
    });
  } catch (error: any) {
    if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
      return NextResponse.json(
        { error: 'Invalid or expired token' },
        { status: 401 }
      );
    }
    
    console.error('API key generation error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to generate API key' },
      { status: 500 }
    );
  }
}
