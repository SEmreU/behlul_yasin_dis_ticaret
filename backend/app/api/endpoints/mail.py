"""
Direkt Mail Gönderme Endpoint
POST /api/v1/mail/send

API key olmadan mock modda çalışır (console'a yazar).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


class MailSendRequest(BaseModel):
    sender_name: str
    sender_email: str
    recipients: List[str]          # email listesi
    subject: str
    body: str                       # HTML veya düz metin
    is_html: bool = True


class MailSendResponse(BaseModel):
    sent: int
    failed: int
    failed_addresses: List[str]
    provider: str
    message: str


async def _send_via_sendgrid(
    sender_name: str,
    sender_email: str,
    recipients: List[str],
    subject: str,
    body: str,
    is_html: bool,
) -> dict:
    from app.core.config import settings
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, From, To, Content

    sent, failed, failed_addrs = 0, 0, []

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

    for recipient in recipients:
        try:
            message = Mail(
                from_email=From(sender_email, sender_name),
                to_emails=To(recipient),
                subject=subject,
                html_content=body if is_html else None,
                plain_text_content=None if is_html else body,
            )
            response = sg.send(message)
            if response.status_code in (200, 202):
                sent += 1
            else:
                failed += 1
                failed_addrs.append(recipient)
        except Exception as e:
            print(f"[SendGrid] {recipient} → {e}")
            failed += 1
            failed_addrs.append(recipient)

    return {"sent": sent, "failed": failed, "failed_addresses": failed_addrs, "provider": "sendgrid"}


async def _send_via_smtp(
    sender_name: str,
    sender_email: str,
    recipients: List[str],
    subject: str,
    body: str,
    is_html: bool,
) -> dict:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from app.core.config import settings

    sent, failed, failed_addrs = 0, 0, []

    try:
        smtp_host = settings.SMTP_HOST
        smtp_port = int(settings.SMTP_PORT or 587)
        smtp_user = settings.SMTP_USER
        smtp_pass = settings.SMTP_PASSWORD

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)

        for recipient in recipients:
            try:
                msg = MIMEMultipart("alternative")
                msg["From"] = f"{sender_name} <{sender_email}>"
                msg["To"] = recipient
                msg["Subject"] = subject
                part = MIMEText(body, "html" if is_html else "plain", "utf-8")
                msg.attach(part)
                server.sendmail(sender_email, recipient, msg.as_string())
                sent += 1
            except Exception as e:
                print(f"[SMTP] {recipient} → {e}")
                failed += 1
                failed_addrs.append(recipient)

        server.quit()
    except Exception as e:
        # SMTP bağlantı hatası — tüm alıcılar başarısız
        print(f"[SMTP] Connection error: {e}")
        return {
            "sent": 0,
            "failed": len(recipients),
            "failed_addresses": recipients,
            "provider": "smtp",
            "error": str(e),
        }

    return {"sent": sent, "failed": failed, "failed_addresses": failed_addrs, "provider": "smtp"}


async def _send_via_resend(
    sender_name: str,
    sender_email: str,
    recipients: List[str],
    subject: str,
    body: str,
    is_html: bool,
) -> dict:
    import httpx
    from app.core.config import settings

    sent, failed, failed_addrs = 0, 0, []

    async with httpx.AsyncClient() as client:
        for recipient in recipients:
            try:
                payload = {
                    "from": f"{sender_name} <{sender_email}>",
                    "to": [recipient],
                    "subject": subject,
                }
                if is_html:
                    payload["html"] = body
                else:
                    payload["text"] = body

                resp = await client.post(
                    "https://api.resend.com/emails",
                    json=payload,
                    headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                    timeout=15,
                )
                if resp.status_code in (200, 201):
                    sent += 1
                else:
                    failed += 1
                    failed_addrs.append(recipient)
            except Exception as e:
                print(f"[Resend] {recipient} → {e}")
                failed += 1
                failed_addrs.append(recipient)

    return {"sent": sent, "failed": failed, "failed_addresses": failed_addrs, "provider": "resend"}


def _send_mock(
    sender_name: str,
    sender_email: str,
    recipients: List[str],
    subject: str,
    body: str,
) -> dict:
    """API key yapılandırılmamışsa mock modda çalışır — console'a log yazar."""
    print("\n" + "=" * 60)
    print("[MOCK MAIL] — Gerçek gönderim için API key ekleyin")
    print(f"  Kimden : {sender_name} <{sender_email}>")
    print(f"  Konu   : {subject}")
    print(f"  Alıcılar ({len(recipients)}):")
    for r in recipients:
        print(f"    • {r}")
    print("=" * 60 + "\n")

    return {
        "sent": len(recipients),
        "failed": 0,
        "failed_addresses": [],
        "provider": "mock",
    }


@router.post("/send", response_model=MailSendResponse)
async def send_mail(
    request: MailSendRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Direkt mail gönderimi.

    **API Key Önceliği:**
    1. SendGrid (`SENDGRID_API_KEY`)
    2. SMTP (`SMTP_HOST` + `SMTP_USER` + `SMTP_PASSWORD`)
    3. Resend (`RESEND_API_KEY`)
    4. Mock (console log — key yoksa otomatik)

    Alıcılar boş veya geçersizse 422 döner.
    """
    if not request.recipients:
        raise HTTPException(status_code=422, detail="En az bir alıcı gerekli")
    if not request.subject.strip():
        raise HTTPException(status_code=422, detail="Konu boş olamaz")
    if not request.body.strip():
        raise HTTPException(status_code=422, detail="Mail içeriği boş olamaz")

    # Alıcı listesini temizle
    recipients = [r.strip() for r in request.recipients if r.strip() and "@" in r]
    if not recipients:
        raise HTTPException(status_code=422, detail="Geçerli e-posta adresi bulunamadı")

    from app.core.config import settings

    result = None

    # 1. SendGrid
    if getattr(settings, "SENDGRID_API_KEY", None) and settings.SENDGRID_API_KEY not in (None, "", "placeholder"):
        try:
            result = await _send_via_sendgrid(
                request.sender_name, request.sender_email,
                recipients, request.subject, request.body, request.is_html
            )
        except Exception as e:
            print(f"[SendGrid] Fallback triggered: {e}")

    # 2. SMTP
    if result is None and getattr(settings, "SMTP_HOST", None) and settings.SMTP_HOST not in (None, ""):
        try:
            result = await _send_via_smtp(
                request.sender_name, request.sender_email,
                recipients, request.subject, request.body, request.is_html
            )
        except Exception as e:
            print(f"[SMTP] Fallback triggered: {e}")

    # 3. Resend
    if result is None and getattr(settings, "RESEND_API_KEY", None) and settings.RESEND_API_KEY not in (None, ""):
        try:
            result = await _send_via_resend(
                request.sender_name, request.sender_email,
                recipients, request.subject, request.body, request.is_html
            )
        except Exception as e:
            print(f"[Resend] Fallback triggered: {e}")

    # 4. Mock
    if result is None:
        result = _send_mock(
            request.sender_name, request.sender_email,
            recipients, request.subject, request.body
        )

    provider = result.get("provider", "mock")
    sent = result.get("sent", 0)
    failed = result.get("failed", 0)

    if provider == "mock":
        msg = f"{sent} mail mock modda gönderildi. Gerçek gönderim için SENDGRID_API_KEY veya SMTP ayarları ekleyin."
    elif failed == 0:
        msg = f"{sent} mail başarıyla gönderildi ({provider})"
    else:
        msg = f"{sent} gönderildi, {failed} başarısız ({provider})"

    return MailSendResponse(
        sent=sent,
        failed=failed,
        failed_addresses=result.get("failed_addresses", []),
        provider=provider,
        message=msg,
    )
