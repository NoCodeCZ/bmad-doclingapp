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
  // Only configure rewrites if API URL is available (runtime, not build time)
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!apiUrl) {
      return [];
    }
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;