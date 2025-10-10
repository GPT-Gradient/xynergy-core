"""
Email Service - Handles all email notifications
Supports SendGrid API and SMTP fallback
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class EmailService:
    """Service for sending email notifications"""

    def __init__(self):
        self.mailjet_api_key = os.getenv("MAILJET_API_KEY")
        self.mailjet_api_secret = os.getenv("MAILJET_API_SECRET")
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@clearforge.ai")
        self.team_email = os.getenv("TEAM_EMAIL", "hello@clearforge.ai")

        # Determine which provider to use
        if self.mailjet_api_key and self.mailjet_api_secret:
            self.provider = "mailjet"
            self._init_mailjet()
        elif self.smtp_host and self.smtp_user:
            self.provider = "smtp"
            logger.info("email_service_initialized", provider="smtp")
        else:
            self.provider = "none"
            logger.warning("email_service_not_configured", message="No email credentials provided")

    def _init_mailjet(self):
        """Initialize Mailjet client"""
        try:
            from mailjet_rest import Client
            self.mailjet_client = Client(auth=(self.mailjet_api_key, self.mailjet_api_secret), version='v3.1')
            logger.info("email_service_initialized", provider="mailjet")
        except ImportError:
            logger.error("mailjet_import_error", message="mailjet-rest library not installed")
            self.provider = "none"
        except Exception as e:
            logger.error("mailjet_init_error", error=str(e))
            self.provider = "none"

    def is_configured(self) -> bool:
        """Check if email service is configured"""
        return self.provider != "none"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email using configured provider

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML body
            text_content: Plain text body (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("email_send_skipped", reason="not_configured", to=to_email)
            return False

        try:
            if self.provider == "mailjet":
                return await self._send_via_mailjet(to_email, subject, html_content, text_content)
            elif self.provider == "smtp":
                return await self._send_via_smtp(to_email, subject, html_content, text_content)
        except Exception as e:
            logger.error("email_send_failed", error=str(e), to=to_email, subject=subject)
            return False

    async def _send_via_mailjet(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email via Mailjet API"""
        try:
            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": self.from_email,
                            "Name": "ClearForge"
                        },
                        "To": [
                            {
                                "Email": to_email
                            }
                        ],
                        "Subject": subject,
                        "HTMLPart": html_content
                    }
                ]
            }

            if text_content:
                data['Messages'][0]['TextPart'] = text_content

            result = self.mailjet_client.send.create(data=data)

            logger.info(
                "email_sent_mailjet",
                to=to_email,
                subject=subject,
                status_code=result.status_code
            )
            return result.status_code < 300

        except Exception as e:
            logger.error("mailjet_send_error", error=str(e), to=to_email)
            return False

    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Attach text and HTML parts
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("email_sent_smtp", to=to_email, subject=subject)
            return True

        except Exception as e:
            logger.error("smtp_send_error", error=str(e), to=to_email)
            return False

    # ================================
    # BETA APPLICATION EMAILS
    # ================================

    async def send_beta_application_notification(
        self,
        application_id: str,
        application_data: Dict[str, Any],
        submitted_at: datetime
    ) -> bool:
        """Send beta application notification to ClearForge team"""

        subject = f"New Beta Application: {application_data.get('businessName', 'Unknown')}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2563eb;">New Beta Application Received</h2>

            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Application Details</h3>

                <p><strong>Business:</strong> {application_data.get('businessName', 'N/A')}</p>
                <p><strong>Industry:</strong> {application_data.get('industry', 'N/A')}</p>
                <p><strong>Contact:</strong> {application_data.get('name', 'N/A')} ({application_data.get('email', 'N/A')})</p>
                <p><strong>Company:</strong> {application_data.get('company', 'N/A')}</p>
                <p><strong>Role:</strong> {application_data.get('role', 'N/A')}</p>
                <p><strong>Website:</strong> {application_data.get('website', 'N/A')}</p>
                <p><strong>Team Size:</strong> {application_data.get('teamSize', 'N/A')}</p>
            </div>

            <div style="margin: 20px 0;">
                <h4>Challenges:</h4>
                <p style="background: #fff; padding: 15px; border-left: 4px solid #2563eb;">
                    {application_data.get('challenges', 'N/A')}
                </p>

                <h4>Why Right Fit:</h4>
                <p style="background: #fff; padding: 15px; border-left: 4px solid #2563eb;">
                    {application_data.get('whyRightFit', 'N/A')}
                </p>
            </div>

            <div style="background: #e5e7eb; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Application ID:</strong> {application_id}</p>
                <p style="margin: 0;"><strong>Submitted:</strong> {submitted_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>

            <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                View in Firebase Console or respond directly to the applicant at {application_data.get('email', 'N/A')}
            </p>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=self.team_email,
            subject=subject,
            html_content=html_content
        )

    async def send_beta_application_confirmation(
        self,
        applicant_name: str,
        applicant_email: str,
        business_name: str,
        application_id: str
    ) -> bool:
        """Send confirmation email to beta applicant"""

        subject = "Beta Application Received - ClearForge"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">Thanks for Applying to ClearForge Beta!</h2>

                <p>Hi {applicant_name},</p>

                <p>We've received your beta application for <strong>{business_name}</strong> and are excited to review it!</p>

                <div style="background: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">What Happens Next?</h3>
                    <ul>
                        <li>Our team will review your application within <strong>48 hours</strong></li>
                        <li>We'll reach out via email with next steps</li>
                        <li>If selected, we'll schedule an onboarding call</li>
                    </ul>
                </div>

                <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin-top: 0;">We're Looking For:</h4>
                    <ul>
                        <li>Businesses creating content regularly</li>
                        <li>Teams wanting to improve SEO and content ROI</li>
                        <li>Partners ready to provide honest feedback</li>
                    </ul>
                </div>

                <p>Have questions? Just reply to this email - we're here to help!</p>

                <p style="margin-top: 30px;">
                    Best,<br>
                    <strong>The ClearForge Team</strong>
                </p>

                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

                <p style="color: #6b7280; font-size: 12px;">
                    Application ID: {application_id}<br>
                    This is an automated confirmation email.
                </p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=applicant_email,
            subject=subject,
            html_content=html_content
        )

    # ================================
    # CONTACT FORM EMAILS
    # ================================

    async def send_contact_notification(
        self,
        ticket_id: str,
        contact_data: Dict[str, Any],
        submitted_at: datetime
    ) -> bool:
        """Send contact form notification to ClearForge team"""

        contact_type = contact_data.get('type', 'general')
        subject = f"New Contact: {contact_type.title()} - {contact_data.get('name', 'Unknown')}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2563eb;">New Contact Form Submission</h2>

            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Contact Details</h3>

                <p><strong>Type:</strong> <span style="background: #dbeafe; padding: 4px 8px; border-radius: 4px;">{contact_type.upper()}</span></p>
                <p><strong>Name:</strong> {contact_data.get('name', 'N/A')}</p>
                <p><strong>Email:</strong> {contact_data.get('email', 'N/A')}</p>
                <p><strong>Company:</strong> {contact_data.get('company', 'N/A')}</p>
                <p><strong>Phone:</strong> {contact_data.get('phone', 'N/A')}</p>
            </div>

            <div style="margin: 20px 0;">
                <h4>Message:</h4>
                <p style="background: #fff; padding: 15px; border-left: 4px solid #2563eb; white-space: pre-wrap;">
{contact_data.get('message', 'N/A')}
                </p>
            </div>

            <div style="background: #e5e7eb; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Ticket ID:</strong> {ticket_id}</p>
                <p style="margin: 0;"><strong>Submitted:</strong> {submitted_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>

            <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                Respond directly to {contact_data.get('email', 'N/A')} or manage in your CRM.
            </p>
        </body>
        </html>
        """

        # Route to appropriate email based on type
        type_email_map = {
            "beta": self.team_email,
            "partnership": os.getenv("PARTNERSHIP_EMAIL", self.team_email),
            "consulting": os.getenv("CONSULTING_EMAIL", self.team_email),
            "media": os.getenv("MEDIA_EMAIL", self.team_email),
            "general": self.team_email
        }

        recipient = type_email_map.get(contact_type, self.team_email)

        return await self.send_email(
            to_email=recipient,
            subject=subject,
            html_content=html_content
        )

    async def send_contact_confirmation(
        self,
        submitter_name: str,
        submitter_email: str,
        contact_type: str,
        ticket_id: str
    ) -> bool:
        """Send confirmation email to contact form submitter"""

        subject = "Message Received - ClearForge"

        # Response time based on type
        response_times = {
            "beta": "48 hours",
            "partnership": "48-72 hours",
            "consulting": "48-72 hours",
            "general": "24-48 hours",
            "media": "48-72 hours"
        }
        expected_response = response_times.get(contact_type, "48 hours")

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">Message Received!</h2>

                <p>Hi {submitter_name},</p>

                <p>We've received your message regarding <strong>{contact_type}</strong>.</p>

                <div style="background: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;">
                        <strong>Expected Response Time:</strong> {expected_response}
                    </p>
                </div>

                <p>We'll get back to you as soon as possible. In the meantime, feel free to explore our website to learn more about ClearForge.</p>

                <p style="margin-top: 30px;">
                    Best,<br>
                    <strong>The ClearForge Team</strong>
                </p>

                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

                <p style="color: #6b7280; font-size: 12px;">
                    Ticket ID: {ticket_id}<br>
                    This is an automated confirmation email.
                </p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(
            to_email=submitter_email,
            subject=subject,
            html_content=html_content
        )
