"""
Email service for sending various types of emails.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import jinja2
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from warehouse_quote_app.app.core.config import settings
from warehouse_quote_app.app.core.monitoring import log_event
from warehouse_quote_app.app.models.quote import Quote
from warehouse_quote_app.app.models.user import User

class EmailService:
    """Service for sending emails."""

    def __init__(self):
        """Initialize email service with configuration."""
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_TLS=settings.MAIL_TLS,
            MAIL_SSL=settings.MAIL_SSL,
            TEMPLATE_FOLDER=Path(__file__).parent / "templates"
        )
        self.fastmail = FastMail(self.config)
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.config.TEMPLATE_FOLDER))
        )

    async def send_email(
        self,
        email_to: List[EmailStr],
        subject: str,
        template_name: str,
        template_data: Dict[str, Any],
        cc: Optional[List[EmailStr]] = None,
        bcc: Optional[List[EmailStr]] = None
    ) -> None:
        """Send an email using a template."""
        template = self.template_env.get_template(template_name)
        html = template.render(**template_data)
        
        message = MessageSchema(
            subject=subject,
            recipients=email_to,
            cc=cc or [],
            bcc=bcc or [],
            body=html,
            subtype="html"
        )
        
        await self.fastmail.send_message(message)

    async def send_quote_email(
        self,
        email_to: List[EmailStr],
        quote_data: Dict[str, Any],
        user_id: int
    ) -> None:
        """Send a quote email to a customer."""
        await self.send_email(
            email_to=email_to,
            subject="Your Quote is Ready",
            template_name="quote.html",
            template_data=quote_data
        )
        
        log_event(
            event_type="quote_email_sent",
            user_id=user_id,
            resource_type="email",
            resource_id=quote_data["quote_id"],
            details={"recipients": email_to}
        )

    async def send_rate_update_notification(
        self,
        email_to: List[EmailStr],
        rate_changes: Dict[str, Any],
        user_id: int
    ) -> None:
        """Send notification about rate changes."""
        await self.send_email(
            email_to=email_to,
            subject="Rate Card Updates",
            template_name="rate_update.html",
            template_data=rate_changes
        )
        
        log_event(
            event_type="rate_update_email_sent",
            user_id=user_id,
            resource_type="email",
            resource_id=None,
            details={"changes": rate_changes}
        )

    async def send_welcome_email(
        self,
        user: User
    ) -> None:
        """Send welcome email to new users."""
        template_data = {
            "username": user.username,
            "first_name": user.first_name,
            "login_url": f"{settings.FRONTEND_URL}/login"
        }
        
        await self.send_email(
            email_to=[user.email],
            subject="Welcome to AUL Quote App",
            template_name="welcome.html",
            template_data=template_data
        )
        
        log_event(
            event_type="welcome_email_sent",
            user_id=user.id,
            resource_type="email",
            resource_id=None,
            details={"email": user.email}
        )

    async def send_quote_confirmation(
        self,
        quote: Quote,
        user: User
    ) -> None:
        """Send quote confirmation email."""
        template_data = {
            "quote_id": quote.id,
            "customer_name": quote.customer.name,
            "total_amount": quote.total_amount,
            "services": quote.services,
            "quote_url": f"{settings.FRONTEND_URL}/quotes/{quote.id}"
        }
        
        await self.send_email(
            email_to=[user.email],
            subject=f"Quote Confirmation #{quote.id}",
            template_name="quote_confirmation.html",
            template_data=template_data
        )
        
        log_event(
            event_type="quote_confirmation_sent",
            user_id=user.id,
            resource_type="email",
            resource_id=str(quote.id),
            details={"email": user.email}
        )

    async def send_admin_notification(
        self,
        admin_email: EmailStr,
        subject: str,
        notification_data: Dict[str, Any]
    ) -> None:
        """Send notification to admin."""
        await self.send_email(
            email_to=[admin_email],
            subject=subject,
            template_name="admin_notification.html",
            template_data=notification_data
        )
        
        log_event(
            event_type="admin_notification_sent",
            user_id=None,
            resource_type="email",
            resource_id=None,
            details={"email": admin_email, "subject": subject}
        )

    async def send_password_reset(
        self,
        user: User,
        reset_token: str
    ) -> None:
        """Send password reset email."""
        template_data = {
            "username": user.username,
            "reset_url": f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        }
        
        await self.send_email(
            email_to=[user.email],
            subject="Password Reset Request",
            template_name="password_reset.html",
            template_data=template_data
        )
        
        log_event(
            event_type="password_reset_sent",
            user_id=user.id,
            resource_type="email",
            resource_id=None,
            details={"email": user.email}
        )
