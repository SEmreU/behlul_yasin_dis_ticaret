import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin();

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
  // Disable turbopack to avoid font resolution issues
  experimental: {
    turbo: undefined,
  },
};

export default withNextIntl(nextConfig);
