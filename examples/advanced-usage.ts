// Advanced usage example for EdPear SDK with TypeScript
import { EdPearClient, VisionRequest, VisionResponse } from '@edpear/sdk';
import * as fs from 'fs';
import * as path from 'path';

class EducationalContentAnalyzer {
  private client: EdPearClient;

  constructor(apiKey: string) {
    this.client = new EdPearClient({ apiKey });
  }

  /**
   * Analyze multiple images in a batch
   */
  async analyzeBatch(images: string[], prompt: string): Promise<VisionResponse[]> {
    const results: VisionResponse[] = [];
    
    for (const image of images) {
      try {
        const result = await this.client.analyzeImage({
          image,
          prompt,
          maxTokens: 800,
          temperature: 0.7
        });
        results.push(result);
        
        // Add delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(`Error analyzing image: ${error}`);
      }
    }
    
    return results;
  }

  /**
   * Create a comprehensive study guide from multiple textbook pages
   */
  async createStudyGuide(imagePaths: string[], subject: string): Promise<string> {
    const images = imagePaths.map(path => fs.readFileSync(path).toString('base64'));
    
    const prompt = `Create a comprehensive study guide for ${subject}. 
    Analyze each page and extract:
    1. Key concepts and definitions
    2. Important formulas or equations
    3. Examples and practice problems
    4. Summary of main topics
    5. Study recommendations
    
    Format the output as a structured study guide.`;

    const results = await this.analyzeBatch(images, prompt);
    
    // Combine all results into a comprehensive study guide
    let studyGuide = `# ${subject} Study Guide\n\n`;
    
    results.forEach((result, index) => {
      studyGuide += `## Page ${index + 1} Analysis\n\n`;
      studyGuide += result.result;
      studyGuide += `\n\n---\n\n`;
    });
    
    return studyGuide;
  }

  /**
   * Analyze handwritten notes and convert to structured content
   */
  async analyzeHandwrittenNotes(imagePath: string): Promise<string> {
    const image = fs.readFileSync(imagePath).toString('base64');
    
    const prompt = `Analyze these handwritten notes and:
    1. Transcribe the text accurately
    2. Identify the main topics and concepts
    3. Organize the information in a structured format
    4. Suggest improvements or additional points
    5. Create a summary of key takeaways`;

    const result = await this.client.analyzeImage({
      image,
      prompt,
      maxTokens: 1200,
      temperature: 0.6
    });

    return result.result;
  }

  /**
   * Get account status and usage statistics
   */
  async getAccountInfo(): Promise<void> {
    try {
      const status = await this.client.getStatus();
      console.log('📊 Account Information:');
      console.log(`👤 User: ${status.user.name}`);
      console.log(`📧 Email: ${status.user.email}`);
      console.log(`💳 Credits: ${status.credits}`);
    } catch (error) {
      console.error('Error getting account info:', error);
    }
  }
}

// Usage example
async function main() {
  const apiKey = process.env.EDPEAR_API_KEY;
  
  if (!apiKey) {
    console.error('Please set your EDPEAR_API_KEY environment variable');
    process.exit(1);
  }

  const analyzer = new EducationalContentAnalyzer(apiKey);

  try {
    // Check account status
    await analyzer.getAccountInfo();

    // Example 1: Analyze handwritten notes
    console.log('\n📝 Analyzing handwritten notes...');
    const notesResult = await analyzer.analyzeHandwrittenNotes('./my-notes.jpg');
    console.log('Notes Analysis:');
    console.log(notesResult);

    // Example 2: Create study guide from multiple pages
    console.log('\n📚 Creating study guide...');
    const studyGuide = await analyzer.createStudyGuide([
      './textbook-page-1.jpg',
      './textbook-page-2.jpg',
      './textbook-page-3.jpg'
    ], 'Mathematics');
    
    // Save study guide to file
    fs.writeFileSync('./study-guide.md', studyGuide);
    console.log('✅ Study guide saved to study-guide.md');

  } catch (error) {
    console.error('Error:', error);
  }
}

// Run if this file is executed directly
if (require.main === module) {
  main();
}

export { EducationalContentAnalyzer };
