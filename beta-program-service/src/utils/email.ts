/**
 * Email Service using SendGrid
 */

import sgMail from '@sendgrid/mail';
import { logger } from './logger';
import { EmailTemplate } from '../types';

class EmailService {
  private isConfigured = false;

  constructor() {
    const apiKey = process.env.SENDGRID_API_KEY;
    if (apiKey) {
      sgMail.setApiKey(apiKey);
      this.isConfigured = true;
      logger.info('SendGrid configured successfully');
    } else {
      logger.warn('SendGrid API key not configured - emails will be logged only');
    }
  }

  /**
   * Send email
   */
  async send(template: EmailTemplate): Promise<void> {
    try {
      if (!this.isConfigured) {
        logger.info('Email would be sent (SendGrid not configured)', {
          to: template.to,
          subject: template.subject,
        });
        return;
      }

      const msg = {
        to: template.to,
        from: process.env.FROM_EMAIL || 'noreply@xynergy.com',
        subject: template.subject,
        text: template.text,
        html: template.html || template.text,
      };

      await sgMail.send(msg);

      logger.info('Email sent successfully', {
        to: template.to,
        subject: template.subject,
      });
    } catch (error) {
      logger.error('Failed to send email', {
        error,
        to: template.to,
        subject: template.subject,
      });
      // Don't throw - email failure shouldn't block the operation
    }
  }

  /**
   * Send welcome email to approved beta user
   */
  async sendWelcomeEmail(email: string, name: string, phase: string): Promise<void> {
    const template: EmailTemplate = {
      to: email,
      subject: `Welcome to the Xynergy ${phase.toUpperCase()} Beta Program!`,
      text: `Hi ${name},

Congratulations! Your application to join the Xynergy ${phase.toUpperCase()} Beta Program has been approved.

As a beta user, you have:
✅ Lifetime access to ALL Continuum projects (current and future)
✅ Early access to new features
✅ Priority support from our team
✅ Ability to shape the future of Xynergy

You can now log in to your account at: https://xynergy.com/login

Welcome to the Xynergy community!

Best regards,
The Xynergy Team`,
      html: `<h2>Welcome to Xynergy ${phase.toUpperCase()} Beta!</h2>
<p>Hi ${name},</p>
<p>Congratulations! Your application has been approved.</p>
<h3>Your Beta Benefits:</h3>
<ul>
<li>✅ Lifetime access to ALL Continuum projects</li>
<li>✅ Early access to new features</li>
<li>✅ Priority support</li>
<li>✅ Shape the future of Xynergy</li>
</ul>
<p><a href="https://xynergy.com/login">Log in to your account</a></p>
<p>Welcome to the community!</p>`,
    };

    await this.send(template);
  }

  /**
   * Send rejection email
   */
  async sendRejectionEmail(email: string, name: string, reason?: string): Promise<void> {
    const template: EmailTemplate = {
      to: email,
      subject: 'Update on Your Xynergy Beta Application',
      text: `Hi ${name},

Thank you for your interest in the Xynergy Beta Program.

After careful review, we're unable to accept your application at this time${reason ? `: ${reason}` : ''}.

We appreciate your interest and encourage you to stay connected with us for future opportunities.

Best regards,
The Xynergy Team`,
    };

    await this.send(template);
  }

  /**
   * Send waitlist email
   */
  async sendWaitlistEmail(email: string, name: string): Promise<void> {
    const template: EmailTemplate = {
      to: email,
      subject: 'You\'re on the Xynergy Beta Waitlist',
      text: `Hi ${name},

Thank you for your application to the Xynergy Beta Program!

We've added you to our waitlist. We'll notify you as soon as spots become available.

In the meantime, follow us on Twitter @xynergy for updates and announcements.

Best regards,
The Xynergy Team`,
    };

    await this.send(template);
  }

  /**
   * Send phase transition notification
   */
  async sendPhaseTransitionEmail(email: string, name: string, newPhase: string): Promise<void> {
    const template: EmailTemplate = {
      to: email,
      subject: `Xynergy Enters ${newPhase.toUpperCase()}!`,
      text: `Hi ${name},

Exciting news! Xynergy has transitioned to ${newPhase.toUpperCase()}.

As a beta user, you retain all your existing benefits and lifetime access. Stay tuned for new features and improvements!

Best regards,
The Xynergy Team`,
    };

    await this.send(template);
  }

  /**
   * Send new project access notification
   */
  async sendNewProjectAccessEmail(email: string, name: string, projectName: string): Promise<void> {
    const template: EmailTemplate = {
      to: email,
      subject: `New Project Access: ${projectName}`,
      text: `Hi ${name},

Great news! A new Continuum project "${projectName}" has been onboarded, and as a beta user, you now have lifetime access to it.

Check it out in your dashboard: https://xynergy.com/projects

Best regards,
The Xynergy Team`,
    };

    await this.send(template);
  }
}

export const emailService = new EmailService();
