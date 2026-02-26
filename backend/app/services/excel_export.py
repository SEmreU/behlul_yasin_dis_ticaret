"""
Universal Excel Export Service
Tüm modüller için Excel/CSV export fonksiyonları
"""

import pandas as pd
from io import BytesIO
from typing import List, Dict, Any
from datetime import datetime


class ExcelExportService:
    """Universal Excel export servisi - Tüm modüller için"""
    
    @staticmethod
    def export_visitors(visitors: List[Dict]) -> BytesIO:
        """
        Ziyaretçi listesini Excel'e aktar
        
        Args:
            visitors: Ziyaretçi listesi
            
        Returns:
            Excel dosyası (BytesIO)
        """
        df = pd.DataFrame([{
            'Tarih': v.get('created_at', datetime.now()),
            'Firma': v.get('company_name', 'N/A'),
            'Ülke': v.get('country', 'N/A'),
            'Şehir': v.get('city', 'N/A'),
            'IP Adresi': v.get('ip_address', 'N/A'),
            'Sayfa URL': v.get('page_url', 'N/A'),
            'Referrer': v.get('referrer', 'N/A'),
            'Tarayıcı': v.get('user_agent', 'N/A')
        } for v in visitors])
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ziyaretçiler', index=False)
            
            # Sütun genişliklerini ayarla
            worksheet = writer.sheets['Ziyaretçiler']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_b2b_results(results: Dict[str, List[Dict]]) -> BytesIO:
        """
        B2B arama sonuçlarını Excel'e aktar
        
        Args:
            results: {
                'alibaba': [...],
                'made-in-china': [...],
                ...
            }
            
        Returns:
            Excel dosyası (BytesIO)
        """
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for platform, items in results.items():
                if not items:
                    continue
                
                # Her platform için ayrı sheet
                df = pd.DataFrame(items)
                
                # Sheet ismi max 31 karakter
                sheet_name = platform[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Sütun genişliklerini ayarla
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(df.columns):
                    max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    col_letter = chr(65 + idx) if idx < 26 else f"A{chr(65 + idx - 26)}"
                    worksheet.column_dimensions[col_letter].width = min(max_length, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_marketplace_rfqs(rfqs: List[Dict]) -> BytesIO:
        """
        RFQ (Request for Quotation) listesini Excel'e aktar
        
        Args:
            rfqs: RFQ listesi
            
        Returns:
            Excel dosyası (BytesIO)
        """
        df = pd.DataFrame([{
            'Platform': r.get('source', 'N/A'),
            'Başlık': r.get('title', 'N/A'),
            'Firma': r.get('company', 'N/A'),
            'Ülke': r.get('country', 'N/A'),
            'Miktar': r.get('quantity', 'N/A'),
            'Tarih': r.get('posted_date', 'N/A'),
            'URL': r.get('url', 'N/A'),
            'Not': r.get('note', '')
        } for r in rfqs])
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='RFQ Listesi', index=False)
            
            worksheet = writer.sheets['RFQ Listesi']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_map_results(companies: List[Dict]) -> BytesIO:
        """
        Harita sonuçlarını Excel'e aktar
        
        Args:
            companies: Firma listesi
            
        Returns:
            Excel dosyası (BytesIO)
        """
        df = pd.DataFrame([{
            'Firma Adı': c.get('name', 'N/A'),
            'Adres': c.get('address', 'N/A'),
            'Telefon': c.get('phone', 'N/A'),
            'Email': c.get('email', 'N/A'),
            'Website': c.get('website', 'N/A'),
            'Kategori': c.get('category', 'N/A'),
            'Rating': c.get('rating', 'N/A'),
            'Latitude': c.get('latitude', 'N/A'),
            'Longitude': c.get('longitude', 'N/A')
        } for c in companies])
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Firmalar', index=False)
            
            worksheet = writer.sheets['Firmalar']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_companies(companies: List[Dict]) -> BytesIO:
        """
        Firma listesini Excel'e aktar
        
        Args:
            companies: Firma listesi
            
        Returns:
            Excel dosyası (BytesIO)
        """
        df = pd.DataFrame([{
            'Firma Adı': c.get('name', 'N/A'),
            'Ülke': c.get('country', 'N/A'),
            'Şehir': c.get('city', 'N/A'),
            'Sektör': c.get('industry', 'N/A'),
            'Email': c.get('email', 'N/A'),
            'Telefon': c.get('phone', 'N/A'),
            'Website': c.get('website', 'N/A'),
            'Kaynak': c.get('source', 'N/A'),
            'Eklenme Tarihi': c.get('created_at', 'N/A')
        } for c in companies])
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Firmalar', index=False)
            
            worksheet = writer.sheets['Firmalar']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_campaigns(campaigns: List[Dict]) -> BytesIO:
        """
        Email kampanyalarını Excel'e aktar
        
        Args:
            campaigns: Kampanya listesi
            
        Returns:
            Excel dosyası (BytesIO)
        """
        df = pd.DataFrame([{
            'Kampanya Adı': c.get('name', 'N/A'),
            'Durum': c.get('status', 'N/A'),
            'Gönderilen': c.get('sent_count', 0),
            'Açılan': c.get('opened_count', 0),
            'Tıklanan': c.get('clicked_count', 0),
            'Açılma Oranı': f"{c.get('open_rate', 0):.1f}%",
            'Tıklama Oranı': f"{c.get('click_rate', 0):.1f}%",
            'Oluşturulma': c.get('created_at', 'N/A'),
            'Gönderilme': c.get('sent_at', 'N/A')
        } for c in campaigns])
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Kampanyalar', index=False)
            
            worksheet = writer.sheets['Kampanyalar']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_to_csv(data: List[Dict], filename: str = "export.csv") -> BytesIO:
        """
        Genel CSV export
        
        Args:
            data: Veri listesi
            filename: Dosya adı
            
        Returns:
            CSV dosyası (BytesIO)
        """
        df = pd.DataFrame(data)
        
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')  # BOM ekle (Excel için)
        output.seek(0)
        
        return output
