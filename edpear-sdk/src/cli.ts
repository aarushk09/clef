#!/usr/bin/env node

import { Command } from 'commander';
import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import open from 'open';
import axios from 'axios';
import fs from 'fs-extra';
import path from 'path';
import { homedir } from 'os';
import dotenv from 'dotenv';

// Load environment variables from .env or .env.local if they exist
dotenv.config();
dotenv.config({ path: path.join(process.cwd(), '.env.local') });

const program = new Command();

// Configuration
const CONFIG_DIR = path.join(homedir(), '.edpear');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');
const ENV_FILE = path.join(process.cwd(), '.env.local');

// Default production URL
const DEFAULT_API_URL = 'https://edpearofficial.vercel.app';

interface Config {
  token?: string;
  user?: {
    id: string;
    name: string;
    email: string;
    credits: number;
  };
  apiKeys?: Array<{
    id: string;
    key: string;
    name: string;
    createdAt: string;
  }>;
}

class EdPearCLI {
  private config: Config = {};

  constructor() {
    this.loadConfig();
  }

  private loadConfig() {
    try {
      if (fs.existsSync(CONFIG_FILE)) {
        this.config = fs.readJsonSync(CONFIG_FILE);
      }
    } catch (error) {
      // Ignore config loading errors on first run
    }
  }

  private saveConfig() {
    try {
      fs.ensureDirSync(CONFIG_DIR);
      fs.writeJsonSync(CONFIG_FILE, this.config, { spaces: 2 });
    } catch (error) {
      console.error(chalk.red('Error saving config:'), error);
    }
  }

  private async makeRequest(endpoint: string, data?: any, method: string = 'GET') {
    const baseURL = process.env.EDPEAR_API_URL || DEFAULT_API_URL;
    
    try {
      const response = await axios({
        method,
        url: `${baseURL}${endpoint}`,
        data,
        headers: {
          'Content-Type': 'application/json',
          ...(this.config.token && { 'Authorization': `Bearer ${this.config.token}` }),
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        console.error(chalk.red('Authentication required. Please run "edpear login" first.'));
        process.exit(1);
      }
      throw error;
    }
  }

  async login() {
    console.log(chalk.blue('🔐 EdPear Authentication'));
    
    const baseURL = process.env.EDPEAR_API_URL || DEFAULT_API_URL;

    console.log(chalk.gray(`Connecting to: ${baseURL}`));
    console.log(chalk.gray('Press ENTER to open the browser for authentication...'));

    await inquirer.prompt([
      {
        type: 'input',
        name: 'confirm',
        message: '',
      },
    ]);

    try {
      // 1. Initialize CLI auth session
      const initResponse = await axios.post(`${baseURL}/api/auth/cli/init`);
      const { tempToken, url } = initResponse.data;

      // 2. Open browser
      await open(url);
      console.log(chalk.green('✅ Browser opened!'));
      console.log(chalk.yellow('Please login and complete 2FA verification in your browser.'));
      console.log(chalk.gray('The CLI will automatically detect when you are authenticated.\n'));

      // 3. Poll for completion
      const spinner = ora('Waiting for authentication...').start();
      const maxAttempts = 200; // 10 minutes (3 seconds * 200)
      let attempts = 0;

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        try {
          // Poll the status endpoint using the tempToken
          const statusResponse = await axios.get(`${baseURL}/api/auth/cli-status?token=${tempToken}`);
          
          if (statusResponse.data.status === 'completed' && statusResponse.data.cliToken) {
            spinner.stop();
            
            // Save token and user data
            this.config.token = statusResponse.data.cliToken;
            this.config.user = statusResponse.data.user;
            this.saveConfig();

            console.log(chalk.green('\n✅ Successfully authenticated!'));
            console.log(chalk.blue(`\nWelcome, ${statusResponse.data.user.name}!`));
            console.log(chalk.gray(`Email: ${statusResponse.data.user.email}`));
            console.log(chalk.gray(`Credits: ${statusResponse.data.user.credits}`));
            return;
          } else if (statusResponse.data.status === 'expired' || statusResponse.data.status === 'failed') {
            spinner.stop();
            console.log(chalk.red(`\n❌ Authentication ${statusResponse.data.status}. Please try again.`));
            process.exit(1);
          } else if (statusResponse.data.otpRequired) {
             spinner.text = 'Waiting for OTP verification... (Check your email)';
          }
          
          attempts++;
        } catch (error: any) {
          // Continue polling on error
          attempts++;
        }
      }

      spinner.stop();
      console.log(chalk.yellow('\n⏱️  Authentication timeout. Please try again.'));
      process.exit(1);

    } catch (error: any) {
      console.error(chalk.red('Error during login:'), error.message);
      process.exit(1);
    }
  }

  async generateKey() {
    if (!this.config.token) {
      console.error(chalk.red('Please login first: edpear login'));
      process.exit(1);
    }

    console.log(chalk.blue('🔑 Generate New API Key\n'));

    const { name } = await inquirer.prompt([
      {
        type: 'input',
        name: 'name',
        message: 'Enter a name for your API key:',
        default: 'My API Key',
        validate: (input: string) => {
          if (!input.trim()) {
            return 'Name is required';
          }
          return true;
        },
      },
    ]);

    const spinner = ora('Generating API key...').start();

    try {
      const result = await this.makeRequest('/api/keys/generate', {
        name,
      }, 'POST');

      spinner.succeed(chalk.green('✅ API key generated successfully!'));

      // Add to config
      if (!this.config.apiKeys) {
        this.config.apiKeys = [];
      }
      this.config.apiKeys.push(result.apiKey);
      this.saveConfig();

      console.log(chalk.blue('\n📋 Your new API key:'));
      console.log(chalk.yellow(result.apiKey.key));
      console.log(chalk.gray('\n💡 Save this key securely. It will not be shown again.'));

      // Ask if user wants to save to .env.local
      const { saveToEnv } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'saveToEnv',
          message: 'Save API key to .env.local file?',
          default: true,
        },
      ]);

      if (saveToEnv) {
        await this.saveToEnvFile(result.apiKey.key);
      }
    } catch (error: any) {
      spinner.fail(chalk.red('❌ Failed to generate API key'));
      console.error(chalk.red('Error:'), error.response?.data?.error || error.message);
      process.exit(1);
    }
  }

  private async saveToEnvFile(apiKey: string) {
    try {
      let envContent = '';
      
      if (fs.existsSync(ENV_FILE)) {
        envContent = fs.readFileSync(ENV_FILE, 'utf8');
      }

      // Remove existing EDPEAR_API_KEY if present
      envContent = envContent.replace(/^EDPEAR_API_KEY=.*$/m, '');
      
      // Add new API key
      if (envContent && !envContent.endsWith('\n')) {
        envContent += '\n';
      }
      envContent += `EDPEAR_API_KEY=${apiKey}\n`;

      fs.writeFileSync(ENV_FILE, envContent);
      console.log(chalk.green('✅ API key saved to .env.local'));
    } catch (error) {
      console.error(chalk.red('Error saving to .env.local:'), error);
    }
  }

  async status() {
    if (!this.config.token) {
      console.log(chalk.red('❌ Not authenticated'));
      console.log(chalk.gray('Run "edpear login" to get started'));
      return;
    }

    console.log(chalk.blue('📊 EdPear Status\n'));
    
    if (this.config.user) {
      console.log(chalk.green(`👤 User: ${this.config.user.name}`));
      console.log(chalk.green(`📧 Email: ${this.config.user.email}`));
      console.log(chalk.green(`💳 Credits: ${this.config.user.credits}`));
    }

    if (this.config.apiKeys && this.config.apiKeys.length > 0) {
      console.log(chalk.blue(`\n🔑 API Keys (${this.config.apiKeys.length}):`));
      this.config.apiKeys.forEach((key, index) => {
        console.log(chalk.gray(`  ${index + 1}. ${key.name}`));
        console.log(chalk.yellow(`     ${key.key}`));
        console.log(chalk.gray(`     Created: ${new Date(key.createdAt).toLocaleDateString()}`));
      });
    } else {
      console.log(chalk.yellow('\n🔑 No API keys found'));
      console.log(chalk.gray('Run "edpear generate-key" to create your first API key'));
    }
  }

  async logout() {
    this.config = {};
    this.saveConfig();
    console.log(chalk.green('✅ Logged out successfully'));
  }
}

// CLI Commands
const cli = new EdPearCLI();

program
  .name('edpear')
  .description('EdPear CLI - AI-powered educational components')
  .version('1.0.0');

program
  .command('login')
  .description('Authenticate with EdPear')
  .action(() => cli.login());

program
  .command('generate-key')
  .description('Generate a new API key')
  .action(() => cli.generateKey());

program
  .command('status')
  .description('Show current status and API keys')
  .action(() => cli.status());

program
  .command('command-line')
  .description('Alias for login')
  .action(() => cli.login());

program
  .command('logout')
  .description('Logout from EdPear')
  .action(() => cli.logout());

program.parse();
