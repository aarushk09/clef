import { NextRequest, NextResponse } from 'next/server';
import { adminDb } from '@/lib/firebase-admin';
import crypto from 'crypto';

export async function POST(request: NextRequest) {
  try {
    // Generate temporary token (valid for 10 minutes)
    const tempToken = crypto.randomBytes(32).toString('hex');
    
    // Store in Firestore with status 'initialized'
    // This allows the CLI to poll for it later
    await adminDb.collection('cliAuthRequests').add({
      tempToken,
      status: 'initialized', // Waiting for user to attach account
      createdAt: new Date(),
    });

    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    
    return NextResponse.json({
      success: true,
      tempToken,
      url: `${baseUrl}/auth/login?cli=true&token=${tempToken}`,
    });
  } catch (error: any) {
    console.error('CLI init error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to initialize CLI auth' },
      { status: 500 }
    );
  }
}

