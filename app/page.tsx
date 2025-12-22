import Link from "next/link";
import { Eye, Zap, Shield, Code, ArrowRight, Terminal } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0f0f0f] text-[#e0e0e0]">
      {/* Navigation */}
      <nav className="border-b border-[#2a2a2a] bg-[#0f0f0f] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Terminal className="w-6 h-6 text-[#4a9eff]" />
              <h1 className="text-xl font-semibold text-white">EdPear</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/auth/login"
                className="px-4 py-2 text-[#888] hover:text-white transition-colors"
              >
                Login
              </Link>
              <Link 
                href="/auth/register"
                className="px-4 py-2 bg-[#4a9eff] hover:bg-[#3a8eef] text-white rounded-lg transition-colors font-medium"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-semibold mb-6 text-white">
            AI-Powered Educational Components
          </h1>
          <p className="text-xl text-[#888] mb-8 max-w-3xl mx-auto">
            Professional AI components for educational technology applications. 
            Build smarter learning experiences with our vision AI and component library.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/auth/register"
              className="px-8 py-3 bg-[#4a9eff] hover:bg-[#3a8eef] text-white rounded-lg font-medium transition-colors"
            >
              Start Building
            </Link>
            <Link 
              href="/docs"
              className="px-8 py-3 border border-[#2a2a2a] text-white rounded-lg font-medium hover:bg-[#1a1a1a] transition-colors"
            >
              Documentation
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-[#1a1a1a]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-semibold text-center mb-12 text-white">Why Choose EdPear?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-[#0f0f0f] border border-[#2a2a2a] w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Eye className="w-8 h-8 text-[#4a9eff]" />
              </div>
              <h3 className="text-xl font-medium text-white mb-2">Vision AI</h3>
              <p className="text-[#888]">
                Advanced image analysis for educational content, textbooks, and learning materials.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-[#0f0f0f] border border-[#2a2a2a] w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-[#4a9eff]" />
              </div>
              <h3 className="text-xl font-medium text-white mb-2">Easy Integration</h3>
              <p className="text-[#888]">
                Simple API calls and CLI tools to integrate AI into your educational applications.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-[#0f0f0f] border border-[#2a2a2a] w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-[#4a9eff]" />
              </div>
              <h3 className="text-xl font-medium text-white mb-2">Secure & Reliable</h3>
              <p className="text-[#888]">
                Enterprise-grade security with usage tracking and credit management.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CLI Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-semibold mb-6 text-white">Developer-First Experience</h2>
              <p className="text-[#888] mb-6 text-lg">
                Get started in minutes with our CLI tool. Connect your account, generate API keys, 
                and start building with AI-powered educational components.
              </p>
              <div className="space-y-4">
                <div className="flex items-center text-[#e0e0e0]">
                  <Code className="w-5 h-5 text-[#4a9eff] mr-3" />
                  <span>Install with npm</span>
                </div>
                <div className="flex items-center text-[#e0e0e0]">
                  <ArrowRight className="w-5 h-5 text-[#4a9eff] mr-3" />
                  <span>Connect your account</span>
                </div>
                <div className="flex items-center text-[#e0e0e0]">
                  <ArrowRight className="w-5 h-5 text-[#4a9eff] mr-3" />
                  <span>Generate API keys</span>
                </div>
                <div className="flex items-center text-[#e0e0e0]">
                  <ArrowRight className="w-5 h-5 text-[#4a9eff] mr-3" />
                  <span>Start building</span>
                </div>
              </div>
            </div>
            <div className="bg-[#1a1a1a] border border-[#2a2a2a] p-6 rounded-lg">
              <pre className="text-[#4a9eff] text-sm font-mono">
{`npm install -g @edpear/cli

edpear login
edpear generate-key
edpear status`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#2a2a2a] py-8 px-6">
        <div className="max-w-7xl mx-auto text-center text-[#888]">
          <p>&copy; 2024 EdPear. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
