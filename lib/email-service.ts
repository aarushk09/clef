import nodemailer from 'nodemailer';

// Create reusable transporter
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.SMTP_USER || process.env.EMAIL_USER,
    pass: process.env.SMTP_PASS || process.env.EMAIL_PASSWORD,
  },
});

// For development, use a test account or configure SMTP
// For production, use a proper email service like SendGrid, Resend, etc.
export async function sendOTPEmail(email: string, otp: string, userName?: string) {
  try {
    // If no SMTP configured, log the OTP (for development)
    if (!process.env.SMTP_USER && !process.env.EMAIL_USER) {
      console.log('📧 OTP Email (SMTP not configured - development mode):');
      console.log(`   To: ${email}`);
      console.log(`   OTP: ${otp}`);
      console.log('   ⚠️  Configure SMTP_USER and SMTP_PASS in .env.local for production');
      return { success: true, message: 'OTP logged (SMTP not configured)' };
    }

    const mailOptions = {
      from: process.env.EMAIL_FROM || process.env.SMTP_USER || 'noreply@edpear.com',
      to: email,
      subject: 'EdPear CLI Authentication Code',
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>EdPear CLI Authentication</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
          <div style="background-color: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h1 style="color: #1a1a1a; margin-top: 0;">EdPear CLI Authentication</h1>
            <p style="color: #666;">Hello${userName ? ` ${userName}` : ''},</p>
            <p style="color: #666;">You requested to authenticate your CLI. Use the code below to complete authentication:</p>
            <div style="background-color: #0f0f0f; border: 1px solid #2a2a2a; border-radius: 6px; padding: 20px; text-align: center; margin: 30px 0;">
              <div style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #4a9eff; font-family: 'Courier New', monospace;">
                ${otp}
              </div>
            </div>
            <p style="color: #666; font-size: 14px;">This code will expire in <strong>10 minutes</strong>.</p>
            <p style="color: #666; font-size: 14px;">If you didn't request this code, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
            <p style="color: #888; font-size: 12px; margin: 0;">© ${new Date().getFullYear()} EdPear. All rights reserved.</p>
          </div>
        </body>
        </html>
      `,
      text: `
EdPear CLI Authentication

Hello${userName ? ` ${userName}` : ''},

You requested to authenticate your CLI. Use the code below to complete authentication:

${otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

© ${new Date().getFullYear()} EdPear. All rights reserved.
      `,
    };

    const info = await transporter.sendMail(mailOptions);
    return { success: true, messageId: info.messageId };
  } catch (error: any) {
    console.error('Email sending error:', error);
    // In development, still log the OTP even if email fails
    if (!process.env.SMTP_USER && !process.env.EMAIL_USER) {
      console.log('📧 OTP (fallback):', otp);
      return { success: true, message: 'OTP logged (email failed)' };
    }
    throw new Error(`Failed to send email: ${error.message}`);
  }
}

