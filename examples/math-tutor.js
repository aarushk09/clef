const { createEdPearClient } = require('../edpear-sdk');

// Configuration
// In a real application, never hardcode your API keys. Use environment variables.
const API_KEY = process.env.EDPEAR_API_KEY || 'edpear_8c44a9c418367e7cbf007c010ccea682ce622a4a2661e252df0ac1efea529f6f';

// Initialize the client
const client = createEdPearClient(API_KEY);

// Mock image data (a simple 1x1 pixel JPEG)
// In a real app, you would read this from a file: fs.readFileSync('math-problem.jpg', 'base64')
const MOCK_IMAGE_BASE64 = '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=';

async function gradeMathHomework() {
  console.log('🎓 Math Tutor AI - Homework Grader');
  console.log('----------------------------------');
  console.log('Initializing EdPear Client...');

  try {
    // 1. Check account status before processing
    console.log('\nChecking account status...');
    const status = await client.getStatus();
    console.log(`✅ Connected as: ${status.user.name}`);
    console.log(`💳 Credits available: ${status.credits}`);

    if (status.credits < 1) {
      console.error('❌ Insufficient credits to grade homework.');
      return;
    }

    // 2. Define the problem
    // Note: We include "TEST" in the prompt to ensure we get a simulated response 
    // even if the backend AI service isn't fully configured with a paid API key yet.
    const studentPrompt = "TEST: Please solve this calculus problem step-by-step: integral of x^2 dx";
    console.log(`\n📝 Analyzing student submission: "${studentPrompt}"`);
    console.log('   Image: [Attached Image Data]');
    console.log('\nProcessing with Vision API...');

    // 3. Call the Vision API
    const response = await client.analyzeImage({
      image: MOCK_IMAGE_BASE64,
      prompt: studentPrompt,
      temperature: 0.2, // Lower temperature for more precise math answers
      maxTokens: 500
    });

    // 4. Display results
    console.log('\n✅ Analysis Complete!');
    console.log('-------------------');
    console.log('AI Response:');
    console.log(response.result);
    console.log('-------------------');
    console.log(`STATS:`);
    console.log(`⏱️  Processing time: ${response.processingTime}ms`);
    console.log(`💰 Credits used: ${response.creditsUsed}`);
    console.log(`💳 Remaining credits: ${response.remainingCredits}`);

  } catch (error) {
    console.error('\n❌ Error:', error.message);
    if (error.message.includes('Invalid API key')) {
        console.log('   -> Please check that your API key is correct and active in the dashboard.');
    }
  }
}

// Run the demo
gradeMathHomework();

