/**
 * Yasin Dış Ticaret - Ziyaretçi Tracking Widget
 *
 * Kullanım:
 * <script src="https://yourdomain.com/tracking-widget.js"></script>
 * <script>
 *   YasinTracker.init('YOUR_API_KEY');
 * </script>
 */

(function (window) {
  'use strict';

  const API_URL = 'http://localhost:8000/api/v1';

  const YasinTracker = {
    sessionId: null,
    apiKey: null,

    /**
     * Tracking sistemini başlat
     * @param {string} apiKey - API anahtarı
     */
    init: function (apiKey) {
      this.apiKey = apiKey;
      this.sessionId = this.generateSessionId();
      this.trackVisitor();
    },

    /**
     * Unique session ID oluştur
     */
    generateSessionId: function () {
      return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    },

    /**
     * GPS lokasyonu al (kullanıcı iznine bağlı)
     */
    getLocation: function () {
      return new Promise((resolve) => {
        if (!navigator.geolocation) {
          resolve({ granted: false });
          return;
        }

        navigator.geolocation.getCurrentPosition(
          (position) => {
            resolve({
              granted: true,
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            });
          },
          (error) => {
            console.log('Location permission denied or error:', error.message);
            resolve({ granted: false });
          }
        );
      });
    },

    /**
     * Ziyaretçi tracking verilerini gönder
     */
    trackVisitor: async function () {
      try {
        // GPS lokasyonunu al (opsiyonel)
        const location = await this.getLocation();

        const payload = {
          session_id: this.sessionId,
          latitude: location.granted ? location.latitude : null,
          longitude: location.granted ? location.longitude : null,
          location_permission_granted: location.granted,
        };

        // API'ye gönder
        const response = await fetch(`${API_URL}/visitor/track`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Visitor tracked:', data);

          // Eğer firma tanımlandıysa, kullanıcıya bilgi göster
          if (data.identified_company) {
            this.showIdentificationBanner(data.identified_company);
          }
        }
      } catch (error) {
        console.error('Tracking error:', error);
      }
    },

    /**
     * Firma tanımlama banner'ı göster
     */
    showIdentificationBanner: function (company) {
      const banner = document.createElement('div');
      banner.id = 'yasin-tracker-banner';
      banner.innerHTML = `
        <div style="
          position: fixed;
          bottom: 20px;
          right: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.3);
          max-width: 350px;
          z-index: 9999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        ">
          <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
            🎯 Firma Tanımlandı
          </div>
          <div style="font-size: 14px; opacity: 0.95;">
            <strong>${company.name}</strong>
            ${company.country ? `<br/>${company.country}` : ''}
          </div>
          <button onclick="document.getElementById('yasin-tracker-banner').remove()" style="
            position: absolute;
            top: 10px;
            right: 10px;
            background: transparent;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
          ">&times;</button>
        </div>
      `;
      document.body.appendChild(banner);

      // 10 saniye sonra otomatik kapat
      setTimeout(() => {
        const el = document.getElementById('yasin-tracker-banner');
        if (el) el.remove();
      }, 10000);
    },
  };

  // Global scope'a ekle
  window.YasinTracker = YasinTracker;
})(window);
