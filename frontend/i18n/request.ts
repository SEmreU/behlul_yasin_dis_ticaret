import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';

// Desteklenen diller
export const locales = ['tr', 'en', 'es', 'ru', 'ar', 'fr', 'de', 'zh'] as const;
export type Locale = (typeof locales)[number];

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  // Geçerli locale kontrolü
  if (!locale || !locales.includes(locale as Locale)) {
    locale = 'tr'; // Varsayılan Türkçe
  }

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default
  };
});
