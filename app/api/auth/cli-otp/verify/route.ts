import { NextRequest, NextResponse } from 'next/server';
import { adminDb } from '@/lib/firebase-admin';
import jwt from 'jsonwebtoken';

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Authorization required' }, { status: 401 });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string; email: string };

    const { otp } = await request.json();

    if (!otp || typeof otp !== 'string' || otp.length !== 6) {
      return NextResponse.json({ error: 'Invalid OTP format' }, { status: 400 });
    }

    // Find pending CLI auth request
    const authSnapshot = await adminDb.collection('cliAuthRequests')
      .where('userId', '==', decoded.userId)
      .where('status', '==', 'pending')
      .limit(1)
      .get();

    if (authSnapshot.empty) {
      return NextResponse.json({ error: 'No pending authentication request' }, { status: 404 });
    }

    const authDoc = authSnapshot.docs[0];
    const authData = authDoc.data();

    // Check if OTP expired
    if (!authData.otpExpiresAt || authData.otpExpiresAt.toMillis() < Date.now()) {
      await adminDb.collection('cliAuthRequests').doc(authDoc.id).update({ status: 'expired' });
      return NextResponse.json({ error: 'OTP expired. Please request a new one.' }, { status: 400 });
    }

    // Check attempts (max 5 attempts)
    const attempts = (authData.otpAttempts || 0) + 1;
    if (attempts > 5) {
      await adminDb.collection('cliAuthRequests').doc(authDoc.id).update({ status: 'failed' });
      return NextResponse.json({ error: 'Too many failed attempts. Please start over.' }, { status: 429 });
    }

    // Verify OTP
    if (authData.otp !== otp) {
      await adminDb.collection('cliAuthRequests').doc(authDoc.id).update({
        otpAttempts: attempts,
      });
      return NextResponse.json({ 
        error: 'Invalid OTP',
        attemptsRemaining: 5 - attempts,
      }, { status: 400 });
    }

    // OTP is correct - get user data
    const userDoc = await adminDb.collection('users').doc(decoded.userId).get();
    if (!userDoc.exists) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const userData = userDoc.data();

    // Generate JWT token for CLI
    const jwtToken = jwt.sign(
      { userId: decoded.userId, email: decoded.email },
      process.env.JWT_SECRET!,
      { expiresIn: '30d' }
    );

    // Mark as completed and store user data
    await adminDb.collection('cliAuthRequests').doc(authDoc.id).update({
      status: 'completed',
      completedAt: new Date(),
      cliToken: jwtToken, // Store token so CLI can poll for it
      userName: userData?.name,
      userEmail: decoded.email,
      userCredits: userData?.credits || 0,
    });

    return NextResponse.json({
      success: true,
      message: 'Authentication successful',
      token: jwtToken,
      user: {
        id: decoded.userId,
        name: userData?.name,
        email: decoded.email,
        credits: userData?.credits || 0,
      },
    });
  } catch (error: any) {
    console.error('Verify OTP error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to verify OTP' },
      { status: 500 }
    );
  }
}

