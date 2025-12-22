const { createEdPearClient } = require('../edpear-sdk');

// Configuration
const API_KEY = process.env.EDPEAR_API_KEY || 'edpear_8c44a9c418367e7cbf007c010ccea682ce622a4a2661e252df0ac1efea529f6f';

// Initialize the client
const client = createEdPearClient(API_KEY);

async function chatBot() {
  console.log('💬 AI Chat Bot Demo');
  console.log('-------------------');
  
  try {
    // 1. Text-only request using the new chat method
    const prompt = "TEST: Write a haiku about educational technology.";
    console.log(`Sending prompt: "${prompt}"...`);

    const response = await client.chat(prompt, { temperature: 0.7 });

    console.log('\nAI Response:');
    console.log(response.result);
    console.log('\n-------------------');
    console.log(`STATS:`);
    console.log(`⏱️  Processing time: ${response.processingTime}ms`);
    console.log(`💰 Credits used: ${response.creditsUsed}`);

  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

chatBot();

