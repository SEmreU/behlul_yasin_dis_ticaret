/**
 * API Helper Functions
 * Excel export ve diğer API çağrıları için yardımcı fonksiyonlar
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Excel dosyası indir
 */
export async function downloadExcel(endpoint: string, filename: string, params?: Record<string, string>) {
    try {
        // Query string oluştur
        const queryString = params
            ? '?' + new URLSearchParams(params).toString()
            : '';

        const response = await fetch(`${API_BASE_URL}${endpoint}${queryString}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        if (!response.ok) {
            throw new Error('Excel indirme başarısız');
        }

        // Blob olarak al
        const blob = await response.blob();

        // Download link oluştur
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        return true;
    } catch (error) {
        console.error('Excel export error:', error);
        throw error;
    }
}

/**
 * Ziyaretçi listesini Excel olarak indir
 */
export async function exportVisitorsToExcel(limit: number = 1000) {
    return downloadExcel(
        '/api/v1/visitor/export',
        `visitors_${new Date().toISOString().split('T')[0]}.xlsx`,
        { limit: limit.toString() }
    );
}

/**
 * B2B/Marketplace sonuçlarını Excel olarak indir
 */
export async function exportMarketplaceToExcel(query: string, platforms?: string[]) {
    return downloadExcel(
        '/api/v1/marketplace/export',
        `marketplace_${query}_${new Date().toISOString().split('T')[0]}.xlsx`,
        {
            query,
            ...(platforms && { platforms: platforms.join(',') })
        }
    );
}

/**
 * RFQ listesini Excel olarak indir
 */
export async function exportRFQsToExcel(query: string, country?: string) {
    return downloadExcel(
        '/api/v1/marketplace/export-rfqs',
        `rfqs_${query}_${new Date().toISOString().split('T')[0]}.xlsx`,
        {
            query,
            ...(country && { country })
        }
    );
}

/**
 * Harita sonuçlarını Excel olarak indir
 */
export async function exportMapsToExcel(country: string, keywords: string, city?: string) {
    return downloadExcel(
        '/api/v1/maps/export',
        `maps_${country}_${new Date().toISOString().split('T')[0]}.xlsx`,
        {
            country,
            keywords,
            ...(city && { city })
        }
    );
}

/**
 * Email'in yetkili mail olup olmadığını kontrol et
 */
export function isAuthorityEmail(email: string): boolean {
    if (!email) return false;

    const authorityPrefixes = [
        'purchasing@',
        'procurement@',
        'manager@',
        'sales@',
        'director@',
        'ceo@',
        'cto@',
        'cfo@',
        'info@',
        'contact@',
        'export@',
        'import@',
    ];

    const emailLower = email.toLowerCase();
    return authorityPrefixes.some(prefix => emailLower.startsWith(prefix));
}

/**
 * Yetkili mail badge component helper
 */
export function getAuthorityEmailBadge(email: string) {
    if (isAuthorityEmail(email)) {
        return {
            icon: '📧',
            className: 'bg-[#00e5a008] border border-[#00e5a022]',
            tooltip: 'Yetkili Mail'
        };
    }
    return null;
}
