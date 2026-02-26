"""
Email Automation & Campaign Management
AI-powered personalized email sending
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.campaign import EmailCampaign, CampaignEmail, CampaignStatus
from app.models.company import Company
from app.models.user import User
import uuid


class EmailAutomationService:
    """Email kampanya otomasyonu"""

    @staticmethod
    def create_campaign(
        db: Session,
        user_id: int,
        name: str,
        subject: str,
        body_template: str,
        target_company_ids: List[int],
        attachments: Optional[List[dict]] = None
    ) -> EmailCampaign:
        """
        Yeni email kampanyası oluştur

        Args:
            user_id: Kampanya sahibi
            name: Kampanya adı
            subject: Email konusu
            body_template: Email içeriği (HTML/Text, AI placeholders ile)
            target_company_ids: Hedef firma ID'leri
            attachments: Eklentiler (katalog, PDF vb.)

        Returns:
            EmailCampaign instance

        Body Template Placeholders:
            {company_name}, {country}, {contact_name}, {product}
        """
        campaign = EmailCampaign(
            user_id=user_id,
            name=name,
            subject=subject,
            body_template=body_template,
            target_company_ids=target_company_ids,
            attachments=attachments or [],
            total_recipients=len(target_company_ids),
            status=CampaignStatus.DRAFT
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        # Her firma için CampaignEmail oluştur
        companies = db.query(Company).filter(
            Company.id.in_(target_company_ids)
        ).all()

        for company in companies:
            # Email bul (contact_emails veya genel email)
            recipient_email = None
            if company.contact_emails:
                # Purchasing email öncelikli
                for email in company.contact_emails:
                    if 'purchasing' in email.lower() or 'manager' in email.lower():
                        recipient_email = email
                        break
                if not recipient_email:
                    recipient_email = company.contact_emails[0]
            elif company.email:
                recipient_email = company.email

            if not recipient_email:
                continue  # Email yoksa atla

            # Tracking ID oluştur
            tracking_id = str(uuid.uuid4())

            campaign_email = CampaignEmail(
                campaign_id=campaign.id,
                company_id=company.id,
                recipient_email=recipient_email,
                tracking_id=tracking_id,
                personalized_subject=subject,  # AI ile kişiselleştirilecek
                personalized_body=body_template  # AI ile kişiselleştirilecek
            )
            db.add(campaign_email)

        db.commit()
        return campaign

    @staticmethod
    async def personalize_email_with_ai(
        subject: str,
        body_template: str,
        company: Company
    ) -> dict:
        """
        OpenAI/Claude ile email kişiselleştirme

        Args:
            subject: Orijinal konu
            body_template: Template içeriği
            company: Hedef firma bilgileri

        Returns:
            {subject, body} - Kişiselleştirilmiş içerik
        """
        from app.core.config import settings
        
        # OpenAI API varsa kullan, yoksa basit placeholder replacement
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-placeholder":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                
                prompt = f"""
Sen profesyonel bir B2B email yazarısın. Aşağıdaki bilgileri kullanarak kişiselleştirilmiş bir email oluştur.

Şirket Bilgileri:
- İsim: {company.name or 'N/A'}
- Ülke: {company.country or 'N/A'}
- Şehir: {company.city or 'N/A'}
- Website: {company.website or 'N/A'}

Email Template:
{body_template}

Kurallar:
1. Spam kelimelerinden kaçın (FREE, URGENT, CLICK HERE, vb.)
2. Profesyonel ve samimi bir ton kullan
3. Kısa ve öz ol (max 200 kelime)
4. Şirket bilgilerini doğal bir şekilde entegre et
5. Template'teki ana mesajı koru ama daha kişisel yap
6. HTML formatında döndür (basit formatlar: <p>, <br>, <strong>)

Sadece email içeriğini döndür, başka açıklama ekleme.
"""
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Sen B2B email kişiselleştirme uzmanısın."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                personalized_body = response.choices[0].message.content.strip()
                
                # Subject'i de kişiselleştir
                personalized_subject = subject.replace("{company_name}", company.name or "")
                
                return {
                    "subject": personalized_subject,
                    "body": personalized_body
                }
                
            except Exception as e:
                print(f"OpenAI API error: {e}")
                # Fallback to simple replacement
        
        # Fallback: Basit placeholder replacement
        personalized = {
            "subject": subject.replace("{company_name}", company.name or "")
                             .replace("{country}", company.country or ""),
            "body": body_template.replace("{company_name}", company.name or "")
                                 .replace("{country}", company.country or "")
                                 .replace("{city}", company.city or "")
                                 .replace("{website}", company.website or "")
        }

        return personalized

    @staticmethod
    async def send_campaign(
        db: Session,
        campaign_id: int,
        email_provider: str = "sendgrid"
    ) -> dict:
        """
        Kampanyayı gönder

        Args:
            campaign_id: Kampanya ID
            email_provider: sendgrid, aws_ses, resend

        Returns:
            {sent: int, failed: int, status: str}
        """
        campaign = db.query(EmailCampaign).filter(
            EmailCampaign.id == campaign_id
        ).first()

        if not campaign:
            return {"error": "Campaign not found"}

        # Durum güncelle
        campaign.status = CampaignStatus.SENDING
        db.commit()

        # Her email'i gönder
        emails = db.query(CampaignEmail).filter(
            CampaignEmail.campaign_id == campaign_id,
            CampaignEmail.is_sent == False
        ).all()

        sent_count = 0
        failed_count = 0

        for email in emails:
            try:
                # AI ile kişiselleştir
                personalized = await EmailAutomationService.personalize_email_with_ai(
                    campaign.subject,
                    campaign.body_template,
                    email.company
                )

                # Email gönder (SendGrid/AWS SES)
                success = await EmailAutomationService._send_email(
                    to=email.recipient_email,
                    subject=personalized["subject"],
                    body=personalized["body"],
                    tracking_id=email.tracking_id,
                    provider=email_provider
                )

                if success:
                    email.is_sent = True
                    email.sent_at = db.func.now()
                    sent_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                print(f"Email send error: {e}")
                failed_count += 1

            db.commit()

        # Kampanya durumu güncelle
        campaign.status = CampaignStatus.COMPLETED
        campaign.sent_count = sent_count
        campaign.completed_at = db.func.now()
        db.commit()

        return {
            "sent": sent_count,
            "failed": failed_count,
            "status": "completed"
        }

    @staticmethod
    async def _send_email(
        to: str,
        subject: str,
        body: str,
        tracking_id: str,
        provider: str = "sendgrid"
    ) -> bool:
        """
        Gerçek email gönderimi

        Args:
            to: Alıcı email
            subject: Konu
            body: İçerik (HTML)
            tracking_id: Tracking pixel ID
            provider: Email provider

        Returns:
            Success boolean
        """
        from app.core.config import settings
        
        # Tracking pixel ekle
        tracking_pixel = f'<img src="https://yourdomain.com/api/v1/track/pixel/{tracking_id}" width="1" height="1" />'
        body_with_tracking = body + tracking_pixel

        # SendGrid entegrasyonu
        if provider == "sendgrid" and settings.SENDGRID_API_KEY and settings.SENDGRID_API_KEY != "placeholder":
            try:
                from sendgrid import SendGridAPIClient
                from sendgrid.helpers.mail import Mail
                
                message = Mail(
                    from_email='noreply@yasin-trade.com',
                    to_emails=to,
                    subject=subject,
                    html_content=body_with_tracking
                )
                
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                
                return response.status_code == 202
                
            except Exception as e:
                print(f"SendGrid error: {e}")
                return False
        
        # Resend alternatifi
        elif provider == "resend" and hasattr(settings, 'RESEND_API_KEY'):
            try:
                import resend
                resend.api_key = settings.RESEND_API_KEY
                
                params = {
                    "from": "noreply@yasin-trade.com",
                    "to": [to],
                    "subject": subject,
                    "html": body_with_tracking,
                }
                
                email = resend.Emails.send(params)
                return True
                
            except Exception as e:
                print(f"Resend error: {e}")
                return False
        
        # Mock mode (development)
        print(f"[Mock] Sending email to {to}: {subject}")
        print(f"[Mock] API key not configured, email not actually sent")
        return True

    @staticmethod
    def track_email_open(db: Session, tracking_id: str):
        """Email açılma tracking"""
        email = db.query(CampaignEmail).filter(
            CampaignEmail.tracking_id == tracking_id
        ).first()

        if email and not email.is_opened:
            email.is_opened = True
            email.opened_at = db.func.now()
            db.commit()

            # Kampanya istatistiklerini güncelle
            campaign = email.campaign
            campaign.opened_count += 1
            db.commit()
