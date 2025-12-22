import { NextRequest, NextResponse } from 'next/server';
import { adminDb } from '@/lib/firebase-admin';
import jwt from 'jsonwebtoken';

export async function DELETE(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Authorization token required' }, { status: 401 });
    }

    const token = authHeader.substring(7);
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };
    const userId = decoded.userId;

    const { searchParams } = new URL(request.url);
    const keyId = searchParams.get('id');

    if (!keyId) {
      return NextResponse.json({ error: 'Key ID is required' }, { status: 400 });
    }

    // Verify key belongs to user
    const keyDoc = await adminDb.collection('apiKeys').doc(keyId).get();
    
    if (!keyDoc.exists) {
      return NextResponse.json({ error: 'Key not found' }, { status: 404 });
    }

    const keyData = keyDoc.data();
    if (keyData?.userId !== userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
    }

    // Delete the key
    await adminDb.collection('apiKeys').doc(keyId).delete();

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('Delete key error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to delete key' },
      { status: 500 }
    );
  }
}

