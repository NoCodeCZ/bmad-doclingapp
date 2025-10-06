/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add for Docker deployment
  output: 'standalone',

  experimental: {
    // Increase body size limit
    serverActions: {
      bodySizeLimit: '50mb'
    }
  },
  typescript: {
    // !! WARN !!
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    // !! WARN !!
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  // Rewrites disabled - using Nginx reverse proxy for routing
  // Frontend calls /api/* which Nginx proxies to backend container
};

module.exports = nextConfig;