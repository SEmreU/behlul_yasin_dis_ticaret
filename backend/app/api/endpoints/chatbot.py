from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import re
import uuid
from datetime import datetime

from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.chatbot import ChatbotConfig, ChatbotConversation, ChatbotLead, ChatbotGoal

router = APIRouter()


class ChatbotConfigCreate(BaseModel):
    """Chatbot configuration model"""
    bot_name: str
    welcome_message: str
    supported_languages: List[str]
    goal: str  # 'email', 'phone', 'both'
    company_info: Optional[dict] = None


class ChatbotMessage(BaseModel):
    """Chatbot message model"""
    session_id: str
    message: str
    language: Optional[str] = None


class ChatbotResponse(BaseModel):
    """Chatbot response model"""
    reply: str
    collected_data: Optional[dict] = None
    conversation_completed: bool = False


@router.post("/config")
async def configure_chatbot(
    config: ChatbotConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Chatbot ayarlarını yapılandır
    
    **Özellikler:**
    - Çoklu dil desteği (otomatik tespit)
    - Lead generation (email/phone collection)
    - Özelleştirilebilir karşılama mesajları
    - Şirket bilgilerini otomatik paylaş
    
    **Desteklenen Diller:**
    Türkçe, İngilizce, Almanca, Rusça, Arapça, Fransızca
    """
    # Mevcut config varsa güncelle
    existing_config = db.query(ChatbotConfig).filter(
        ChatbotConfig.user_id == current_user.id
    ).first()
    
    if existing_config:
        existing_config.bot_name = config.bot_name
        existing_config.welcome_message = config.welcome_message
        existing_config.supported_languages = config.supported_languages
        existing_config.goal = ChatbotGoal(config.goal)
        existing_config.company_info = config.company_info
    else:
        # Yeni config oluştur
        embed_code = f'<script src="https://api.example.com/chatbot/{current_user.id}.js"></script>'
        
        new_config = ChatbotConfig(
            user_id=current_user.id,
            bot_name=config.bot_name,
            welcome_message=config.welcome_message,
            supported_languages=config.supported_languages,
            goal=ChatbotGoal(config.goal),
            company_info=config.company_info,
            embed_code=embed_code
        )
        db.add(new_config)
        existing_config = new_config
    
    db.commit()
    db.refresh(existing_config)
    
    return {
        "status": "configured",
        "bot_name": existing_config.bot_name,
        "embed_code": existing_config.embed_code
    }


def extract_email(text: str) -> Optional[str]:
    """Email adresi çıkar"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Telefon numarası çıkar"""
    # Türkiye ve uluslararası formatlar
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\b0\d{10}\b',  # 05551234567
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


async def generate_ai_response(
    message: str,
    conversation_history: list,
    config: ChatbotConfig,
    collected_data: dict
) -> str:
    """
    AI ile chatbot yanıtı — Groq (birincil, ücretsiz) → HuggingFace → Pattern fallback
    """
    from app.core.config import settings

    system_prompt = f"""Sen {config.bot_name} adlı bir B2B satış asistanısın.
Şirket bilgileri: {config.company_info or 'Bilgi yok'}
Görevin: Müşteriye yardımcı olmak, {"email " if config.goal in ["email", "both"] else ""}{"telefon " if config.goal in ["phone", "both"] else ""}toplamak.
Toplanan: {collected_data} | Kısa, doğal, max 2-3 cümle."""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-5:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": message})

    # ── 1. Groq (birincil, ücretsiz) ─────────────────────────────────────────
    groq_key = ""
    try:
        from app.core.database import SessionLocal
        from app.models.api_setting import ApiSetting
        import base64 as _b64
        _db = SessionLocal()
        _s = _db.query(ApiSetting).filter(ApiSetting.key_name == "GROQ_API_KEY").first()
        _db.close()
        if _s and _s.key_value:
            groq_key = _b64.b64decode(_s.key_value.encode()).decode()
    except Exception:
        pass
    if not groq_key:
        groq_key = getattr(settings, "GROQ_API_KEY", "") or ""

    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.7,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Chatbot] Groq error: {e}")
        
    
    # Hugging Face ile dene
    if hasattr(settings, 'HUGGINGFACE_API_KEY') and settings.HUGGINGFACE_API_KEY:
        try:
            import requests
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
            
            payload = {
                "inputs": f"{system_prompt}\n\nUser: {message}\nAssistant:",
                "parameters": {"max_new_tokens": 150, "temperature": 0.7}
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()[0]['generated_text'].split("Assistant:")[-1].strip()
        except Exception as e:
            print(f"Hugging Face error: {e}")
    
    # Fallback: Basit pattern-based yanıtlar
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['merhaba', 'hello', 'hi', 'selam']):
        return f"{config.welcome_message}\n\nSize nasıl yardımcı olabilirim?"
    
    if any(word in message_lower for word in ['fiyat', 'price', 'cost', 'ücret']):
        return "Fiyat bilgisi için lütfen iletişim bilgilerinizi paylaşır mısınız? Size detaylı teklif gönderelim."
    
    if any(word in message_lower for word in ['ürün', 'product', 'hizmet', 'service']):
        company_name = config.company_info.get('name', 'Firmamız') if config.company_info else 'Firmamız'
        return f"{company_name} olarak geniş ürün yelpazemiz var. Hangi ürün hakkında bilgi almak istersiniz?"
    
    if not collected_data.get('email') and config.goal in ['email', 'both']:
        return "Size daha iyi yardımcı olabilmem için email adresinizi paylaşır mısınız?"
    
    return "Anlıyorum. Size nasıl yardımcı olabilirim? Daha fazla bilgi için iletişim bilgilerinizi paylaşabilirsiniz."


@router.post("/chat", response_model=ChatbotResponse)
async def chat_with_bot(
    message: ChatbotMessage,
    db: Session = Depends(get_db)
):
    """
    Chatbot konuşma endpoint'i (public - auth gerekmez)
    
    **Conversation Flow:**
    1. Karşılama
    2. Hangi ürünü arıyor? (product inquiry)
    3. E-posta/telefon toplama
    4. Teşekkür mesajı
    
    **AI Integration:**
    - OpenAI GPT-3.5/4 (ücretli)
    - Groq Llama 3 (BEDAVA!)
    - Hugging Face (bedava)
    - Fallback: Pattern-based
    """
    # Session'a göre conversation bul veya oluştur
    conversation = db.query(ChatbotConversation).filter(
        ChatbotConversation.session_id == message.session_id
    ).first()
    
    if not conversation:
        # İlk mesaj - yeni conversation oluştur
        # Config bul (şimdilik ilk aktif config'i kullan)
        config = db.query(ChatbotConfig).filter(
            ChatbotConfig.is_active == True
        ).first()
        
        if not config:
            # Varsayılan config oluştur (ilk çalıştırmada)
            import uuid as _uuid
            config = ChatbotConfig(
                user_id=1,  # ilk admin kullanıcı
                bot_name="TradeBot",
                welcome_message="Merhaba! Yasin Dış Ticaret'e hoşgeldiniz. Size nasıl yardımcı olabilirim?",
                supported_languages=["tr", "en", "de"],
                goal=ChatbotGoal.EMAIL,
                company_info={"name": "Yasin Dış Ticaret"},
                embed_code=f'<script src="https://yasin-trade-backend.onrender.com/chatbot/embed.js"></script>',
                is_active=True,
            )
            db.add(config)
            try:
                db.commit()
                db.refresh(config)
            except Exception:
                db.rollback()
                # Başka bir session zaten oluşturduysa tekrar sorgula
                config = db.query(ChatbotConfig).filter(
                    ChatbotConfig.is_active == True
                ).first()
                if not config:
                    raise HTTPException(status_code=500, detail="Chatbot config oluşturulamadı")
        
        conversation = ChatbotConversation(
            config_id=config.id,
            session_id=message.session_id,
            messages=[],
            collected_data={},
            detected_language=message.language or "tr"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    config = conversation.config
    
    # Email ve telefon çıkar
    email = extract_email(message.message)
    phone = extract_phone(message.message)
    
    if email:
        conversation.collected_data['email'] = email
    if phone:
        conversation.collected_data['phone'] = phone
    
    # Mesajı kaydet
    conversation.messages.append({
        "role": "user",
        "content": message.message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # AI yanıt oluştur
    ai_reply = await generate_ai_response(
        message.message,
        conversation.messages,
        config,
        conversation.collected_data
    )
    
    # AI yanıtını kaydet
    conversation.messages.append({
        "role": "assistant",
        "content": ai_reply,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Conversation tamamlandı mı kontrol et
    is_completed = False
    if config.goal == ChatbotGoal.EMAIL and conversation.collected_data.get('email'):
        is_completed = True
    elif config.goal == ChatbotGoal.PHONE and conversation.collected_data.get('phone'):
        is_completed = True
    elif config.goal == ChatbotGoal.BOTH and conversation.collected_data.get('email') and conversation.collected_data.get('phone'):
        is_completed = True
    
    if is_completed and not conversation.is_completed:
        conversation.is_completed = True
        conversation.completed_at = datetime.utcnow()
        
        # Lead oluştur
        lead = ChatbotLead(
            conversation_id=conversation.id,
            email=conversation.collected_data.get('email'),
            phone=conversation.collected_data.get('phone'),
            inquiry=message.message[:500],  # İlk mesaj
            language=conversation.detected_language
        )
        db.add(lead)
    
    db.commit()
    
    return {
        "reply": ai_reply,
        "collected_data": conversation.collected_data if is_completed else None,
        "conversation_completed": is_completed
    }


@router.get("/leads")
async def get_chatbot_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 50,
    skip: int = 0
):
    """
    Chatbot'tan toplanan lead'leri listele
    
    Query params:
    - limit: Maksimum sonuç sayısı
    - skip: Pagination offset
    
    Returns:
        Lead listesi (email, phone, conversation summary vb.)
    """
    # Kullanıcının chatbot config'ini bul
    config = db.query(ChatbotConfig).filter(
        ChatbotConfig.user_id == current_user.id
    ).first()
    
    if not config:
        return {"leads": [], "total": 0}
    
    # Config'e ait conversation'ların lead'lerini getir
    leads = db.query(ChatbotLead).join(ChatbotConversation).filter(
        ChatbotConversation.config_id == config.id
    ).order_by(ChatbotLead.created_at.desc()).offset(skip).limit(limit).all()
    
    total = db.query(ChatbotLead).join(ChatbotConversation).filter(
        ChatbotConversation.config_id == config.id
    ).count()
    
    return {
        "leads": [
            {
                "id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "company_name": lead.company_name,
                "inquiry": lead.inquiry,
                "language": lead.language,
                "created_at": lead.created_at.isoformat() if lead.created_at else None
            }
            for lead in leads
        ],
        "total": total
    }


@router.get("/stats")
async def get_chatbot_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Chatbot istatistikleri
    
    Returns:
        - Toplam konuşma sayısı
        - Lead conversion rate
        - Aktif sohbetler
        - Ortalama yanıt süresi
    """
    config = db.query(ChatbotConfig).filter(
        ChatbotConfig.user_id == current_user.id
    ).first()
    
    if not config:
        return {
            "total_conversations": 0,
            "leads_collected": 0,
            "conversion_rate": 0,
            "active_chats": 0
        }
    
    total_conversations = db.query(ChatbotConversation).filter(
        ChatbotConversation.config_id == config.id
    ).count()
    
    leads_collected = db.query(ChatbotLead).join(ChatbotConversation).filter(
        ChatbotConversation.config_id == config.id
    ).count()
    
    active_chats = db.query(ChatbotConversation).filter(
        ChatbotConversation.config_id == config.id,
        ChatbotConversation.is_completed == False
    ).count()
    
    conversion_rate = (leads_collected / total_conversations * 100) if total_conversations > 0 else 0
    
    return {
        "total_conversations": total_conversations,
        "leads_collected": leads_collected,
        "conversion_rate": round(conversion_rate, 2),
        "active_chats": active_chats
    }

