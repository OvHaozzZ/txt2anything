/** @type {import('next').NextConfig} */
const nextConfig = {
  // Proxy API requests to FastAPI backend during development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/static/:path*',
        destination: 'http://localhost:8000/static/:path*',
      },
    ];
  },
  // Output standalone build for production
  output: 'standalone',
};

module.exports = nextConfig;
