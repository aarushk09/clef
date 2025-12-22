import { NextRequest, NextResponse } from 'next/server';
import { adminDb } from '@/lib/firebase-admin';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const token = searchParams.get('token');
    const userId = searchParams.get('userId');

    if (!token || !userId) {
      return NextResponse.json({ error: 'Missing parameters' }, { status: 400 });
    }

    // Get the CLI auth request from Firestore
    const cliAuthSnapshot = await adminDb.collection('cliAuthRequests')
      .where('userId', '==', userId)
      .where('tempToken', '==', token)
      .where('status', '==', 'pending')
      .limit(1)
      .get();

    if (cliAuthSnapshot.empty) {
      return NextResponse.json({ error: 'Token expired or invalid' }, { status: 400 });
    }

    const authDoc = cliAuthSnapshot.docs[0];
    const authData = authDoc.data();

    // Check if expired (5 minutes)
    if (authData.createdAt.toMillis() + 5 * 60 * 1000 < Date.now()) {
      await adminDb.collection('cliAuthRequests').doc(authDoc.id).update({ status: 'expired' });
      return NextResponse.json({ error: 'Token expired' }, { status: 400 });
    }

    // Get user data
    const userDoc = await adminDb.collection('users').doc(userId).get();
    if (!userDoc.exists) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const userData = userDoc.data();

    // Generate JWT token
    const jwtToken = jwt.sign(
      { userId, email: userData?.email },
      process.env.JWT_SECRET!,
      { expiresIn: '30d' }
    );

    // Mark as completed
    await adminDb.collection('cliAuthRequests').doc(authDoc.id).update({ 
      status: 'completed',
      completedAt: new Date(),
    });

    return NextResponse.json({
      success: true,
      token: jwtToken,
      user: {
        id: userId,
        name: userData?.name,
        email: userData?.email,
        credits: userData?.credits,
      },
    });
  } catch (error: any) {
    console.error('OAuth callback error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to process callback' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Authorization required' }, { status: 401 });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };

    // Generate temporary token (valid for 5 minutes)
    const tempToken = crypto.randomBytes(32).toString('hex');

    // Store in Firestore
    await adminDb.collection('cliAuthRequests').add({
      userId: decoded.userId,
      tempToken,
      status: 'pending',
      createdAt: new Date(),
    });

    return NextResponse.json({
      success: true,
      token: tempToken,
      url: `${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/auth/cli-callback?token=${tempToken}&userId=${decoded.userId}`,
    });
  } catch (error: any) {
    console.error('Generate temp token error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to generate token' },
      { status: 500 }
    );
  }
}

