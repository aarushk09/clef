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

    // Get query parameters
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '10');

    // Get recent API requests
    const logsSnapshot = await adminDb
      .collection('apiRequests')
      .where('userId', '==', userId)
      .orderBy('timestamp', 'desc')
      .limit(limit)
      .get();

    const logs = logsSnapshot.docs.map((doc: any) => {
      const data = doc.data();
      return {
        id: doc.id,
        endpoint: data.endpoint,
        method: data.method,
        statusCode: data.statusCode,
        timestamp: data.timestamp?.toDate?.() || data.timestamp,
        creditsUsed: data.creditsUsed,
        processingTime: data.processingTime,
        apiKeyId: data.apiKeyId,
      };
    });

    return NextResponse.json({
      success: true,
      logs,
    });
  } catch (error: any) {
    if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
      return NextResponse.json(
        { error: 'Invalid or expired token' },
        { status: 401 }
      );
    }
    
    console.error('Get logs error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to get logs' },
      { status: 500 }
    );
  }
}

