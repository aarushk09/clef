'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Terminal, Copy, Check, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

function DocumentationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const copyCode = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    toast.success('Code copied to clipboard');
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const CodeBlock = ({ code, language = 'bash', id }: { code: string; language?: string; id: string }) => (
    <div className="relative group">
      <pre className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-4 overflow-x-auto">
        <code className={`text-sm text-[#e0e0e0] font-mono`}>{code}</code>
      </pre>
      <button
        onClick={() => copyCode(code, id)}
        className="absolute top-3 right-3 p-2 bg-[#2a2a2a] hover:bg-[#3a3a3a] rounded transition-colors opacity-0 group-hover:opacity-100"
      >
        {copiedCode === id ? (
          <Check className="w-4 h-4 text-[#4a9eff]" />
        ) : (
          <Copy className="w-4 h-4 text-[#888]" />
        )}
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0f0f0f] text-[#e0e0e0]">
      {/* Header */}
      <header className="border-b border-[#2a2a2a] bg-[#0f0f0f] sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Terminal className="w-6 h-6 text-[#4a9eff]" />
              <h1 className="text-xl font-semibold text-white">EdPear Documentation</h1>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#2a2a2a] rounded-lg transition-colors text-sm"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Getting Started */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-white mb-4">Getting Started</h2>
          <p className="text-[#888] mb-6 text-lg">
            EdPear provides AI-powered educational components through a simple API. Get started in minutes.
          </p>

          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-medium text-white mb-3">1. Install the SDK</h3>
              <CodeBlock 
                code="npm install @edpear/sdk" 
                id="install-sdk"
              />
            </div>

            <div>
              <h3 className="text-xl font-medium text-white mb-3">2. Get Your API Key</h3>
              <p className="text-[#888] mb-3">
                Sign up for an account and generate an API key from your dashboard, or use the CLI (which is included with the SDK):
              </p>
              <CodeBlock 
                code={`# Install the SDK (includes the CLI)
npm install @edpear/sdk

# Login to your account
npx edpear login

# Generate an API key
npx edpear generate-key`} 
                id="get-api-key"
              />
            </div>

            <div>
              <h3 className="text-xl font-medium text-white mb-3">3. Initialize the Client</h3>
              <CodeBlock 
                code={`const { createEdPearClient } = require('@edpear/sdk');

const client = createEdPearClient('your-api-key-here');`} 
                language="javascript"
                id="init-client"
              />
            </div>
          </div>
        </section>

        {/* CLI Commands */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-white mb-6">CLI Commands</h2>
          <p className="text-[#888] mb-6">
            The EdPear CLI is included with the SDK. You can run it using <code className="text-[#4a9eff]">npx edpear</code> or by installing the SDK globally with <code className="text-[#4a9eff]">npm install -g @edpear/sdk</code>.
          </p>
          
          <div className="space-y-8">
            <div>
              <h3 className="text-xl font-medium text-white mb-3">edpear login</h3>
              <p className="text-[#888] mb-3">
                Authenticate your CLI with your EdPear account. Opens your browser for secure authentication.
              </p>
              <CodeBlock 
                code="npx edpear login" 
                id="cli-login"
              />
            </div>

            <div>
              <h3 className="text-xl font-medium text-white mb-3">edpear generate-key</h3>
              <p className="text-[#888] mb-3">
                Generate a new API key for your account. Optionally saves it to your .env.local file.
              </p>
              <CodeBlock 
                code="npx edpear generate-key" 
                id="cli-generate"
              />
            </div>

            <div>
              <h3 className="text-xl font-medium text-white mb-3">edpear status</h3>
              <p className="text-[#888] mb-3">
                View your account status, credits, and API keys.
              </p>
              <CodeBlock 
                code="npx edpear status" 
                id="cli-status"
              />
            </div>

            <div>
              <h3 className="text-xl font-medium text-white mb-3">edpear logout</h3>
              <p className="text-[#888] mb-3">
                Logout from your EdPear CLI session.
              </p>
              <CodeBlock 
                code="npx edpear logout" 
                id="cli-logout"
              />
            </div>
          </div>
        </section>

        {/* SDK Usage */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-white mb-6">SDK Usage</h2>

          <div className="space-y-8">
            <div>
              <h3 className="text-xl font-medium text-white mb-3">Text Chat</h3>
              <p className="text-[#888] mb-3">
                Send text-only prompts to the AI. Perfect for chat, Q&A, and text generation.
              </p>
              <CodeBlock 
                code={`const response = await client.chat('Explain quantum physics in simple terms', {
  temperature: 0.7,
  maxTokens: 500
});

console.log(response.result);
console.log(\`Credits used: \${response.creditsUsed}\`);`} 
                language="javascript"
                id="sdk-chat"
              />
            </div>

            <div>
              <h3 className="text-xl font-medium text-white mb-3">Vision Analysis</h3>
              <p className="text-[#888] mb-3">
                Analyze images with AI. Upload a base64-encoded image and ask questions about it.
              </p>
              <CodeBlock 
                code={`const fs = require('fs');
const image = fs.readFileSync('math-problem.jpg', 'base64');

const response = await client.analyzeImage({
  image: image,
  prompt: 'Solve this math problem step by step',
  temperature: 0.2,
  maxTokens: 1000
});

console.log(response.result);`} 
                language="javascript"
                id="sdk-vision"
              />
            </div>

            <div>
              <h3 className="text-xl font-medium text-white mb-3">Check Account Status</h3>
              <p className="text-[#888] mb-3">
                Get your current credit balance and account information.
              </p>
              <CodeBlock 
                code={`const status = await client.getStatus();
console.log(\`Credits: \${status.credits}\`);
console.log(\`User: \${status.user.name}\`);`} 
                language="javascript"
                id="sdk-status"
              />
            </div>
          </div>
        </section>

        {/* Examples */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-white mb-6">Examples</h2>

          <div className="space-y-8">
            <div>
              <h3 className="text-xl font-medium text-white mb-3">Math Tutor</h3>
              <p className="text-[#888] mb-3">
                Create an AI-powered math tutor that explains solutions step-by-step.
              </p>
              <CodeBlock 
                code={`const { createEdPearClient } = require('@edpear/sdk');
const client = createEdPearClient(process.env.EDPEAR_API_KEY);

async function solveMath(problem) {
  const response = await client.chat(
    \`Solve this problem step by step: \${problem}\`,
    { temperature: 0.2 }
  );
  return response.result;
}

solveMath('What is the integral of x^2?')
  .then(solution => console.log(solution));`} 
                language="javascript"
                id="example-math"
              />
            </div>

            <div>
              <h3 className="text-xl font-medium text-white mb-3">Homework Grader</h3>
              <p className="text-[#888] mb-3">
                Grade student submissions using vision AI to analyze handwritten work.
              </p>
              <CodeBlock 
                code={`const fs = require('fs');
const client = createEdPearClient(process.env.EDPEAR_API_KEY);

async function gradeHomework(imagePath, assignment) {
  const image = fs.readFileSync(imagePath, 'base64');
  
  const response = await client.analyzeImage({
    image: image,
    prompt: \`Grade this \${assignment} submission. Provide feedback.\`,
    temperature: 0.3
  });
  
  return {
    feedback: response.result,
    creditsUsed: response.creditsUsed
  };
}`} 
                language="javascript"
                id="example-grader"
              />
            </div>
          </div>
        </section>

        {/* API Reference */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-white mb-6">API Reference</h2>

          <div className="space-y-6">
            <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">client.chat(prompt, options?)</h3>
              <p className="text-[#888] mb-4">Send a text prompt to the AI.</p>
              <div className="space-y-2 text-sm">
                <div><span className="text-[#4a9eff]">prompt</span>: <span className="text-[#888]">string - The text prompt</span></div>
                <div><span className="text-[#4a9eff]">options.temperature</span>: <span className="text-[#888]">number (0-1) - Controls randomness (default: 0.7)</span></div>
                <div><span className="text-[#4a9eff]">options.maxTokens</span>: <span className="text-[#888]">number - Maximum response length (default: 1000)</span></div>
              </div>
            </div>

            <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">client.analyzeImage(request)</h3>
              <p className="text-[#888] mb-4">Analyze an image with AI vision capabilities.</p>
              <div className="space-y-2 text-sm">
                <div><span className="text-[#4a9eff]">request.image</span>: <span className="text-[#888]">string (optional) - Base64 encoded image</span></div>
                <div><span className="text-[#4a9eff]">request.prompt</span>: <span className="text-[#888]">string - Question or instruction about the image</span></div>
                <div><span className="text-[#4a9eff]">request.temperature</span>: <span className="text-[#888]">number (optional) - Controls randomness</span></div>
                <div><span className="text-[#4a9eff]">request.maxTokens</span>: <span className="text-[#888]">number (optional) - Maximum response length</span></div>
              </div>
            </div>

            <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-2">client.getStatus()</h3>
              <p className="text-[#888] mb-4">Get your account status and remaining credits.</p>
              <p className="text-sm text-[#888]">Returns: <span className="text-[#4a9eff]">{`{ credits: number, user: { id, name, email } }`}</span></p>
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section className="mb-16">
          <h2 className="text-3xl font-semibold text-white mb-6">Pricing</h2>
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
            <p className="text-[#888] mb-4">
              EdPear uses a credit-based system. Each successful API call costs <span className="text-white font-medium">1 credit</span>.
            </p>
            <ul className="list-disc list-inside space-y-2 text-[#888]">
              <li>New accounts start with <span className="text-white font-medium">100 free credits</span></li>
              <li>Credits are deducted only on successful requests (200 status codes)</li>
              <li>Failed requests do not consume credits</li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}

export default function DocumentationPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#4a9eff] animate-spin" />
      </div>
    }>
      <DocumentationContent />
    </Suspense>
  );
}
