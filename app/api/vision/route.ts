import { NextRequest, NextResponse } from 'next/server';
import { ApiService } from '@/lib/api-service';
import { adminDb } from '@/lib/firebase-admin';
import { VisionRequest } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const apiKey = request.headers.get('x-api-key');
    
    if (!apiKey) {
      return NextResponse.json(
        { error: 'API key is required' },
        { status: 401 }
      );
    }

    // Validate API key
    const keyValidation = await ApiService.validateApiKey(apiKey);
    if (!keyValidation.isValid || !keyValidation.userId) {
      return NextResponse.json(
        { error: 'Invalid API key' },
        { status: 401 }
      );
    }

    const { image, prompt, maxTokens, temperature } = await request.json() as VisionRequest;

    if (!prompt) {
      return NextResponse.json(
        { error: 'Prompt is required' },
        { status: 400 }
      );
    }

    // Check user credits using Admin SDK syntax
    const userDoc = await adminDb.collection('users').doc(keyValidation.userId).get();
    if (!userDoc.exists) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    const userData = userDoc.data();
    if (!userData || userData.credits < 1) {
      return NextResponse.json(
        { error: 'Insufficient credits' },
        { status: 402 }
      );
    }

    // Process vision request
    const startTime = Date.now();
    const result = await ApiService.processVisionRequest({
      image,
      prompt,
      maxTokens,
      temperature,
    });

    // Update user credits using Admin SDK syntax
    await adminDb.collection('users').doc(keyValidation.userId).update({
      credits: userData.credits - result.creditsUsed,
      updatedAt: new Date(),
    });

    // Log API request using Admin SDK syntax
    await adminDb.collection('apiRequests').add({
      userId: keyValidation.userId,
      apiKeyId: apiKey,
      endpoint: '/api/vision',
      method: 'POST',
      requestBody: { 
        prompt, 
        maxTokens: maxTokens || null, 
        temperature: temperature || null,
        hasImage: !!image 
      },
      responseBody: { result: result.result },
      statusCode: 200,
      creditsUsed: result.creditsUsed,
      timestamp: new Date(),
      processingTime: result.processingTime,
    });

    return NextResponse.json({
      success: true,
      result: result.result,
      creditsUsed: result.creditsUsed,
      remainingCredits: userData.credits - result.creditsUsed,
      processingTime: result.processingTime,
    });
  } catch (error: any) {
    console.error('Vision API error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to process vision request' },
      { status: 500 }
    );
  }
}

