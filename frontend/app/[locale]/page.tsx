'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';

export default function HomePage() {
  // const t = useTranslations();
  const [currentLang, setCurrentLang] = useState('tr');
  const [isScrolled, setIsScrolled] = useState(false);

  // Handle scroll for sticky navigation
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const languages = [
    { code: 'ar', name: 'العربية', flag: '🇸🇦' },
    { code: 'zh', name: '中文', flag: '🇨🇳' },
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'ru', name: 'Русский', flag: '🇷🇺' },
    { code: 'tr', name: 'Türkçe', flag: '🇹🇷' },
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Language Switcher - Fixed Position */}
      <div className="fixed top-2.5 right-[8%] z-50 flex gap-2 bg-white/90 backdrop-blur-sm p-2 rounded-lg shadow-md">
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => setCurrentLang(lang.code)}
            className={`text-2xl hover:scale-110 transition-transform ${currentLang === lang.code ? 'ring-2 ring-blue-500 rounded' : ''
              }`}
            title={lang.name}
          >
            {lang.flag}
          </button>
        ))}
      </div>

      {/* Navigation - becomes white and sticky on scroll */}
      <nav className={`sticky top-0 z-40 transition-all duration-300 ${isScrolled ? 'bg-white shadow-lg py-3' : 'bg-transparent py-8'
        }`}>
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-[#03a9f4] to-[#6632ff] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">Y</span>
              </div>
              <div>
                <h1 className="font-bold text-xl text-gray-900">Yasin Dış Ticaret</h1>
                <p className="text-xs text-gray-600">CAN Group İştiraki</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <Link href="#about" className={`transition-colors font-semibold uppercase text-sm ${isScrolled ? 'text-[#026e9f] hover:text-[#03a9f4]' : 'text-white hover:text-[#a6dcf4]'
                }`}>
                Hakkımızda
              </Link>
              <Link href="#services" className={`transition-colors font-semibold uppercase text-sm ${isScrolled ? 'text-[#026e9f] hover:text-[#03a9f4]' : 'text-white hover:text-[#a6dcf4]'
                }`}>
                Hizmetlerimiz
              </Link>
              <Link href="#modules" className={`transition-colors font-semibold uppercase text-sm ${isScrolled ? 'text-[#026e9f] hover:text-[#03a9f4]' : 'text-white hover:text-[#a6dcf4]'
                }`}>
                Modüller
              </Link>
              <Link href="/login" className="bg-[#03a9f4] text-white px-6 py-2 rounded-lg hover:bg-[#0288d1] transition-colors">
                Giriş Yap
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section with Background Slideshow */}
      <section className="relative h-[600px] flex items-center justify-center overflow-hidden">
        {/* Background Slideshow */}
        <div className="absolute inset-0 z-0">
          {/* Slideshow images - Using gradients as placeholders */}
          <div className="absolute inset-0 opacity-0" style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            animation: 'slideshow 25s infinite'
          }}></div>
          <div className="absolute inset-0 opacity-0" style={{
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            animation: 'slideshow 25s infinite 5s'
          }}></div>
          <div className="absolute inset-0 opacity-0" style={{
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            animation: 'slideshow 25s infinite 10s'
          }}></div>
          <div className="absolute inset-0 opacity-0" style={{
            background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            animation: 'slideshow 25s infinite 15s'
          }}></div>
          <div className="absolute inset-0 opacity-0" style={{
            background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            animation: 'slideshow 25s infinite 20s'
          }}></div>

          {/* Dark overlay */}
          <div className="absolute inset-0 bg-black/50"></div>
        </div>

        {/* Top Wave Separator */}
        <div className="absolute top-0 left-0 right-0 h-16 z-[1]" style={{ transform: 'translateY(-1px)' }}>
          <svg className="w-full h-full" style={{ fill: '#FFFFFF' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2600 130.1" preserveAspectRatio="none">
            <polygon points="0 130.1 2600 69.1 0 69.1 0 130.1" opacity="0.33" style={{ isolation: 'isolate' }}></polygon>
            <polygon points="0 69.1 2600 69.1 0 0 0 69.1" opacity="0.67" style={{ isolation: 'isolate' }}></polygon>
            <polygon points="0 0 2600 69.1 2600 0 0 0" style={{ isolation: 'isolate' }}></polygon>
          </svg>
        </div>

        {/* Bottom Wave Separator */}
        <div className="absolute bottom-0 left-0 right-0 h-20 z-[1]" style={{ transform: 'translateY(1px)' }}>
          <svg className="w-full h-full" style={{ fill: '#FFFFFF', transform: 'rotateX(180deg)' }} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" preserveAspectRatio="none">
            <path d="M0,0S28.6,63.7,89.9,52.5c42.4-7.6,38.1-16.7,94.9-31.9C242,5.4,242,1.8,371,48.4q7.33,2.61,14.42,4.52c70,18.92,122.41-11.28,192.21-28.7a368.79,368.79,0,0,1,49.81-9.08c38.82-4.21,83.68-2.05,138.66,13.76l5.55,1.59c12.94,3.74,23.74,7,33.47,9.8,34.45,9.83,55.52,13.26,111.28,7.81,30.16-3,49.63-11.54,62.12-20.66C996.54,14.27,1000,0,1000,0Z"></path>
          </svg>
        </div>

        {/* Content */}
        <div className="relative z-10 container mx-auto px-4 text-center text-white">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
              Dünya çapında CAN Group iştirakleriyle<br />
              İhracat ve İthalat Yapmaktayız
            </h1>
            <p className="text-2xl md:text-3xl mb-4 font-light">
              Yasin Dış Ticaret Ltd Bir Can Group İştirakidir
            </p>
            <p className="text-xl md:text-2xl mb-8 font-semibold text-[#f79007]">
              Yılardır Değişmeyen Kalite
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
              <Link
                href="/register"
                className="bg-[#f79007] text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-[#e67e00] transition-all transform hover:scale-105 shadow-lg"
              >
                Hemen Başlayın
              </Link>
              <Link
                href="#about"
                className="bg-white text-[#03a9f4] px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition-all transform hover:scale-105 shadow-lg"
              >
                Daha Fazla Bilgi
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold mb-6 text-gray-900">
              Uluslar arası Dış Ticaret hizmetleri veren firmamız
            </h2>
            <p className="text-lg text-gray-700 leading-relaxed mb-8">
              CAN Group bünyesinde faaliyet gösteren Yasin Dış Ticaret, yılların deneyimi ve uzmanlığı ile
              dünya çapında ihracat ve ithalat hizmetleri sunmaktadır. Modern teknoloji ve geleneksel ticaret
              anlayışını birleştirerek, müşterilerimize en kaliteli hizmeti sunmayı hedefliyoruz.
            </p>
            <div className="grid md:grid-cols-3 gap-8 mt-12">
              <div className="text-center">
                <div className="text-[#03a9f4] text-5xl font-bold mb-2">15+</div>
                <div className="text-gray-600">Yıllık Tecrübe</div>
              </div>
              <div className="text-center">
                <div className="text-[#f79007] text-5xl font-bold mb-2">50+</div>
                <div className="text-gray-600">Ülkeye İhracat</div>
              </div>
              <div className="text-center">
                <div className="text-[#00bf87] text-5xl font-bold mb-2">1000+</div>
                <div className="text-gray-600">Mutlu Müşteri</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-bold text-xl mb-4">Yasin Dış Ticaret</h3>
              <p className="text-gray-400">
                CAN Group İştiraki olarak uluslararası dış ticaret hizmetlerinde yılların deneyimi
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Hızlı Linkler</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="#about" className="hover:text-white">Hakkımızda</Link></li>
                <li><Link href="#modules" className="hover:text-white">Modüller</Link></li>
                <li><Link href="/login" className="hover:text-white">Giriş</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">İletişim</h4>
              <ul className="space-y-2 text-gray-400">
                <li>info@yasindisticaret.com</li>
                <li>+90 555 123 45 67</li>
                <li>Ankara, Türkiye</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2026 Yasin Dış Ticaret - CAN Group İştiraki. Tüm hakları saklıdır.</p>
          </div>
        </div>
      </footer>

      <style jsx>{`
        @keyframes slideshow {
          0%, 20% {
            opacity: 1;
          }
          25%, 100% {
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
}
