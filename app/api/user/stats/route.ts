import { NextRequest, NextResponse } from 'next/server';
import { adminDb } from '@/lib/firebase-admin';
import jwt from 'jsonwebtoken';

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Authorization token required' }, { status: 401 });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };
    const userId = decoded.userId;

    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    // Execute queries
    const [userDoc, apiKeysSnapshot, userRequestsSnapshot] = await Promise.all([
      adminDb.collection('users').doc(userId).get(),
      adminDb.collection('apiKeys').where('userId', '==', userId).get(),
      // Fetch all requests for user and filter in memory to avoid Firestore index requirement
      adminDb.collection('apiRequests').where('userId', '==', userId).get()
    ]);
    
    if (!userDoc.exists) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }
    
    const userData = userDoc.data();
    const credits = userData?.credits !== undefined ? userData.credits : 0;
    const is2FAEnabled = userData?.is2FAEnabled || false;
    const twoFactorMethod = userData?.twoFactorMethod || null;

    // Calculate total requests
    const totalRequests = userRequestsSnapshot.size;

    // Calculate today's stats in memory
    let requestsToday = 0;
    let creditsUsedToday = 0;
    let totalTime = 0;
    let timeCount = 0;

    userRequestsSnapshot.forEach((doc: any) => {
      const data = doc.data();
      
      // Check if request was made today
      const timestamp = data.timestamp?.toDate ? data.timestamp.toDate() : new Date(data.timestamp);
      
      if (timestamp >= startOfDay) {
        requestsToday++;
        creditsUsedToday += (data.creditsUsed || 0);
        if (data.processingTime) {
          totalTime += data.processingTime;
          timeCount++;
        }
      }
    });

    const avgResponseTime = timeCount > 0 ? (totalTime / timeCount / 1000).toFixed(2) + 's' : '0s';

    const stats = {
      credits,
      totalRequests,
      requestsToday,
      creditsUsedToday,
      avgResponseTime,
      is2FAEnabled,
      twoFactorMethod
    };

    return NextResponse.json({
      success: true,
      stats
    });

  } catch (error: any) {
    console.error('Get stats error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to get stats' },
      { status: 500 }
    );
  }
}
