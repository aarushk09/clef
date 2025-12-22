const axios = require('axios');

const API_KEY = 'edpear_b93c1417bbb296f21c58b4a8daeb2c7e7cb0075cd2350c6e88355df306a9f87f';

async function testApi() {
  try {
    console.log('Sending text-only request to API...');
    const response = await axios.post('https://edpearofficial-ibo0qv7gj-aarushk09s-projects.vercel.app/api/vision', {
      prompt: 'test: Hello, please reply with "Test successful".'
    }, {
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
      }
    });

    console.log('Response Status:', response.status);
    console.log('Response Data:', JSON.stringify(response.data, null, 2));
  } catch (error) {
    if (error.response) {
      console.error('Error Status:', error.response.status);
      console.error('Error Data:', JSON.stringify(error.response.data, null, 2));
    } else {
      console.error('Error:', error.message);
    }
  }
}

testApi();
