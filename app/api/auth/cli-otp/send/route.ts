import { NextRequest, NextResponse } from 'next/server';
import { adminDb, adminAuth } from '@/lib/firebase-admin';
import { sendOTPEmail } from '@/lib/email-service';
import crypto from 'crypto';
import jwt from 'jsonwebtoken';

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Authorization required' }, { status: 401 });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string; email: string };

    // Get user data
    const userDoc = await adminDb.collection('users').doc(decoded.userId).get();
    if (!userDoc.exists) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const userData = userDoc.data();
    const userEmail = decoded.email || userData?.email;

    if (!userEmail) {
      return NextResponse.json({ error: 'User email not found' }, { status: 400 });
    }

    // Check for existing pending CLI auth request
    const existingAuthSnapshot = await adminDb.collection('cliAuthRequests')
      .where('userId', '==', decoded.userId)
      .where('status', '==', 'pending')
      .limit(1)
      .get();

    let authRequestId: string;
    let tempToken: string;

    if (!existingAuthSnapshot.empty) {
      // Use existing request
      const existingDoc = existingAuthSnapshot.docs[0];
      authRequestId = existingDoc.id;
      const existingData = existingDoc.data();
      tempToken = existingData.tempToken;

      // Check if OTP was already sent recently (within last minute)
      if (existingData.otpSentAt) {
        const lastSent = existingData.otpSentAt.toMillis();
        const now = Date.now();
        if (now - lastSent < 60000) {
          return NextResponse.json({
            error: 'Please wait before requesting another OTP',
            retryAfter: Math.ceil((60000 - (now - lastSent)) / 1000),
          }, { status: 429 });
        }
      }
    } else {
      // Create new request
      tempToken = crypto.randomBytes(32).toString('hex');
      const newRequest = await adminDb.collection('cliAuthRequests').add({
        userId: decoded.userId,
        tempToken,
        status: 'pending',
        createdAt: new Date(),
      });
      authRequestId = newRequest.id;
    }

    // Generate 6-digit OTP
    const otp = crypto.randomInt(100000, 999999).toString();

    // Store OTP in Firestore (expires in 10 minutes)
    await adminDb.collection('cliAuthRequests').doc(authRequestId).update({
      otp,
      otpExpiresAt: new Date(Date.now() + 10 * 60 * 1000), // 10 minutes
      otpSentAt: new Date(),
      otpAttempts: 0,
    });

    // Send OTP email
    try {
      await sendOTPEmail(userEmail, otp, userData?.name);
    } catch (emailError: any) {
      console.error('Failed to send OTP email:', emailError);
      // Still return success if email fails (for development)
      // In production, you might want to return an error
    }

    return NextResponse.json({
      success: true,
      message: 'OTP sent to your email',
      expiresIn: 600, // 10 minutes in seconds
    });
  } catch (error: any) {
    console.error('Send OTP error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to send OTP' },
      { status: 500 }
    );
  }
}

