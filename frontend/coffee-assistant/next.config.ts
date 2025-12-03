import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'shop.zuscoffee.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'zuscoffee.com',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
