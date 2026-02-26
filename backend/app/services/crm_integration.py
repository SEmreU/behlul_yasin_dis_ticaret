"""
CRM Integration Service
Salesforce ve HubSpot entegrasyonları
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime


class SalesforceIntegration:
    """
    Salesforce API entegrasyonu
    
    Kullanım:
    1. Salesforce hesabı oluştur
    2. Connected App oluştur
    3. API key ve instance URL al
    4. .env dosyasına ekle:
       SALESFORCE_API_KEY=your_key
       SALESFORCE_INSTANCE_URL=https://your-instance.salesforce.com
    """
    
    def __init__(self, api_key: str, instance_url: str):
        self.api_key = api_key
        self.instance_url = instance_url
        self.base_url = f"{instance_url}/services/data/v57.0"
    
    async def export_leads(self, leads: List[Dict]) -> Dict:
        """
        Lead'leri Salesforce'a aktar
        
        Args:
            leads: Lead listesi
            
        Returns:
            {
                "success": True,
                "exported": 10,
                "failed": 0,
                "errors": []
            }
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        exported = 0
        failed = 0
        errors = []
        
        async with httpx.AsyncClient() as client:
            for lead in leads:
                try:
                    payload = {
                        "FirstName": lead.get('first_name', ''),
                        "LastName": lead.get('last_name', 'Unknown'),
                        "Company": lead.get('company', 'Unknown'),
                        "Email": lead.get('email'),
                        "Phone": lead.get('phone'),
                        "Country": lead.get('country'),
                        "City": lead.get('city'),
                        "Industry": lead.get('industry'),
                        "LeadSource": lead.get('source', 'Yasin Trade Intelligence'),
                        "Description": lead.get('notes', '')
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/sobjects/Lead",
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    if response.status_code == 201:
                        exported += 1
                    else:
                        failed += 1
                        errors.append({
                            "lead": lead.get('email'),
                            "error": response.text
                        })
                        
                except Exception as e:
                    failed += 1
                    errors.append({
                        "lead": lead.get('email'),
                        "error": str(e)
                    })
        
        return {
            "success": failed == 0,
            "exported": exported,
            "failed": failed,
            "errors": errors
        }
    
    async def export_contacts(self, contacts: List[Dict]) -> Dict:
        """
        Kontakları Salesforce'a aktar
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        exported = 0
        failed = 0
        errors = []
        
        async with httpx.AsyncClient() as client:
            for contact in contacts:
                try:
                    payload = {
                        "FirstName": contact.get('first_name', ''),
                        "LastName": contact.get('last_name', 'Unknown'),
                        "Email": contact.get('email'),
                        "Phone": contact.get('phone'),
                        "Title": contact.get('title'),
                        "Department": contact.get('department')
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/sobjects/Contact",
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    if response.status_code == 201:
                        exported += 1
                    else:
                        failed += 1
                        errors.append({
                            "contact": contact.get('email'),
                            "error": response.text
                        })
                        
                except Exception as e:
                    failed += 1
                    errors.append({
                        "contact": contact.get('email'),
                        "error": str(e)
                    })
        
        return {
            "success": failed == 0,
            "exported": exported,
            "failed": failed,
            "errors": errors
        }


class HubSpotIntegration:
    """
    HubSpot API entegrasyonu
    
    Kullanım:
    1. HubSpot hesabı oluştur
    2. Settings → Integrations → API key
    3. .env dosyasına ekle:
       HUBSPOT_API_KEY=your_key
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
    
    async def export_contacts(self, contacts: List[Dict]) -> Dict:
        """
        Kontakları HubSpot'a aktar
        
        Args:
            contacts: Kontak listesi
            
        Returns:
            {
                "success": True,
                "exported": 10,
                "failed": 0,
                "errors": []
            }
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        exported = 0
        failed = 0
        errors = []
        
        async with httpx.AsyncClient() as client:
            for contact in contacts:
                try:
                    payload = {
                        "properties": {
                            "email": contact.get('email'),
                            "firstname": contact.get('first_name', ''),
                            "lastname": contact.get('last_name', ''),
                            "company": contact.get('company'),
                            "phone": contact.get('phone'),
                            "country": contact.get('country'),
                            "city": contact.get('city'),
                            "industry": contact.get('industry'),
                            "website": contact.get('website'),
                            "hs_lead_status": "NEW"
                        }
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/crm/v3/objects/contacts",
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    if response.status_code == 201:
                        exported += 1
                    else:
                        failed += 1
                        errors.append({
                            "contact": contact.get('email'),
                            "error": response.text
                        })
                        
                except Exception as e:
                    failed += 1
                    errors.append({
                        "contact": contact.get('email'),
                        "error": str(e)
                    })
        
        return {
            "success": failed == 0,
            "exported": exported,
            "failed": failed,
            "errors": errors
        }
    
    async def export_companies(self, companies: List[Dict]) -> Dict:
        """
        Firmaları HubSpot'a aktar
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        exported = 0
        failed = 0
        errors = []
        
        async with httpx.AsyncClient() as client:
            for company in companies:
                try:
                    payload = {
                        "properties": {
                            "name": company.get('name'),
                            "domain": company.get('website'),
                            "country": company.get('country'),
                            "city": company.get('city'),
                            "industry": company.get('industry'),
                            "phone": company.get('phone'),
                            "description": company.get('description', '')
                        }
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/crm/v3/objects/companies",
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    if response.status_code == 201:
                        exported += 1
                    else:
                        failed += 1
                        errors.append({
                            "company": company.get('name'),
                            "error": response.text
                        })
                        
                except Exception as e:
                    failed += 1
                    errors.append({
                        "company": company.get('name'),
                        "error": str(e)
                    })
        
        return {
            "success": failed == 0,
            "exported": exported,
            "failed": failed,
            "errors": errors
        }


class CRMExportService:
    """CRM export servisi - Salesforce ve HubSpot"""
    
    @staticmethod
    async def export_to_salesforce(
        data: List[Dict],
        data_type: str,  # "leads" veya "contacts"
        api_key: str,
        instance_url: str
    ) -> Dict:
        """
        Salesforce'a veri aktar
        
        Args:
            data: Veri listesi
            data_type: "leads" veya "contacts"
            api_key: Salesforce API key
            instance_url: Salesforce instance URL
            
        Returns:
            Export sonucu
        """
        salesforce = SalesforceIntegration(api_key, instance_url)
        
        if data_type == "leads":
            return await salesforce.export_leads(data)
        elif data_type == "contacts":
            return await salesforce.export_contacts(data)
        else:
            raise ValueError(f"Invalid data_type: {data_type}")
    
    @staticmethod
    async def export_to_hubspot(
        data: List[Dict],
        data_type: str,  # "contacts" veya "companies"
        api_key: str
    ) -> Dict:
        """
        HubSpot'a veri aktar
        
        Args:
            data: Veri listesi
            data_type: "contacts" veya "companies"
            api_key: HubSpot API key
            
        Returns:
            Export sonucu
        """
        hubspot = HubSpotIntegration(api_key)
        
        if data_type == "contacts":
            return await hubspot.export_contacts(data)
        elif data_type == "companies":
            return await hubspot.export_companies(data)
        else:
            raise ValueError(f"Invalid data_type: {data_type}")
