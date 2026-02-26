import createMiddleware from 'next-intl/middleware';
import { locales } from './i18n/request';

export default createMiddleware({
  locales,
  defaultLocale: 'tr',
  localePrefix: 'always'
});

export const config = {
  matcher: ['/', '/(tr|en|es|ru|ar|fr|de|zh)/:path*']
};
