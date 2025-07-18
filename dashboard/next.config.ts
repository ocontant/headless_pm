import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Warning: This allows production builds to successfully complete even if
    // your project has type errors.
    ignoreBuildErrors: true,
  },
  // Docker container support
  output: 'standalone',
  // Enable optimizations for production builds
  experimental: {
    serverComponentsExternalPackages: ['axios'],
  },
};

export default nextConfig;
