'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search, Globe, FileCode, Image, Download } from 'lucide-react';
import api from '@/lib/api';

export default function SearchPage() {
  const { user } = useAuth();
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('multilang');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedLanguages, setSelectedLanguages] = useState(['tr', 'en', 'de']);

  const languages = [
    { code: 'tr', name: 'Türkçe' },
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Español' },
    { code: 'ru', name: 'Русский' },
    { code: 'ar', name: 'العربية' },
    { code: 'fr', name: 'Français' },
    { code: 'de', name: 'Deutsch' },
    { code: 'zh', name: '中文' },
  ];

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await api.post('/search/product', {
        query,
        search_type: searchType,
        languages: searchType === 'multilang' ? selectedLanguages : undefined,
      });

      setResults(response.data.results);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Arama başarısız');
    } finally {
      setLoading(false);
    }
  };

  const toggleLanguage = (code: string) => {
    if (selectedLanguages.includes(code)) {
      setSelectedLanguages(selectedLanguages.filter((l) => l !== code));
    } else {
      setSelectedLanguages([...selectedLanguages, code]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Akıllı Ürün Arama</h1>
          <p className="text-sm text-gray-500">
            8 dilde arama • GTIP • OEM • Görüntü işleme
          </p>
          {user && (
            <p className="text-sm text-blue-600 mt-1">
              Kalan Kontör: {user.query_credits}
            </p>
          )}
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Search Box */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Arama Yap</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Search Type */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Arama Tipi
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  onClick={() => setSearchType('multilang')}
                  className={`p-3 border rounded-lg flex items-center gap-2 ${
                    searchType === 'multilang'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300'
                  }`}
                >
                  <Globe className="w-5 h-5" />
                  <span className="text-sm">8 Dilde</span>
                </button>
                <button
                  onClick={() => setSearchType('gtip')}
                  className={`p-3 border rounded-lg flex items-center gap-2 ${
                    searchType === 'gtip'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300'
                  }`}
                >
                  <FileCode className="w-5 h-5" />
                  <span className="text-sm">GTIP Kod</span>
                </button>
                <button
                  onClick={() => setSearchType('oem')}
                  className={`p-3 border rounded-lg flex items-center gap-2 ${
                    searchType === 'oem'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300'
                  }`}
                >
                  <FileCode className="w-5 h-5" />
                  <span className="text-sm">OEM Kod</span>
                </button>
                <button
                  onClick={() => setSearchType('image')}
                  className={`p-3 border rounded-lg flex items-center gap-2 ${
                    searchType === 'image'
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300'
                  }`}
                >
                  <Image className="w-5 h-5" />
                  <span className="text-sm">Görsel</span>
                </button>
              </div>
            </div>

            {/* Language Selection (for multilang) */}
            {searchType === 'multilang' && (
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Diller ({selectedLanguages.length} seçili)
                </label>
                <div className="flex flex-wrap gap-2">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => toggleLanguage(lang.code)}
                      className={`px-3 py-1 text-sm rounded-full border ${
                        selectedLanguages.includes(lang.code)
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-white text-gray-700 border-gray-300'
                      }`}
                    >
                      {lang.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Search Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder={
                  searchType === 'gtip'
                    ? 'Örn: 8409.91'
                    : searchType === 'oem'
                    ? 'Örn: ABC12345'
                    : 'Ürün adı girin...'
                }
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <Button onClick={handleSearch} disabled={loading} className="px-8">
                <Search className="w-5 h-5 mr-2" />
                {loading ? 'Aranıyor...' : 'Ara'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {results.length > 0 && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>{results.length} Sonuç Bulundu</CardTitle>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Excel İndir
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {results.map((result, index) => (
                  <div
                    key={index}
                    className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">
                          {result.name || result.descriptions?.tr || 'N/A'}
                        </h3>
                        {result.gtip_code && (
                          <p className="text-sm text-gray-600 mt-1">
                            GTIP: {result.gtip_code}
                          </p>
                        )}
                        {result.oem_code && (
                          <p className="text-sm text-gray-600">
                            OEM: {result.oem_code}
                          </p>
                        )}
                        {result.category && (
                          <span className="inline-block mt-2 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                            {result.category}
                          </span>
                        )}
                      </div>
                      {result.language && (
                        <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                          {result.language.toUpperCase()}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
