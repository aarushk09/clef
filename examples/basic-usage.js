// Basic usage example for EdPear SDK
const { EdPearClient } = require('@edpear/sdk');
const fs = require('fs');

// Initialize the client with your API key
const client = new EdPearClient({
  apiKey: process.env.EDPEAR_API_KEY, // Get this from your dashboard
});

async function analyzeTextbook() {
  try {
    // Read an image file and convert to base64
    const imageBuffer = fs.readFileSync('./textbook-page.jpg');
    const base64Image = imageBuffer.toString('base64');

    // Analyze the image
    const result = await client.analyzeImage({
      image: base64Image,
      prompt: "Analyze this textbook page and explain the main concepts. Create a study guide with key points.",
      maxTokens: 1000,
      temperature: 0.7
    });

    console.log('Analysis Result:');
    console.log(result.result);
    console.log(`\nCredits used: ${result.creditsUsed}`);
    console.log(`Remaining credits: ${result.remainingCredits}`);
    console.log(`Processing time: ${result.processingTime}ms`);

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Check account status
async function checkStatus() {
  try {
    const status = await client.getStatus();
    console.log('Account Status:');
    console.log(`Credits remaining: ${status.credits}`);
    console.log(`User: ${status.user.name}`);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Run the examples
async function main() {
  console.log('🔍 Checking account status...');
  await checkStatus();
  
  console.log('\n📚 Analyzing textbook page...');
  await analyzeTextbook();
}

main();
