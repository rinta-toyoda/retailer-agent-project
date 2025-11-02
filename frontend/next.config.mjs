/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Use 'export' for static site generation (S3 + CloudFront)
  // Use 'standalone' for Docker container deployment
  output: process.env.NEXT_OUTPUT_MODE || 'export',

  // Disable image optimization for static export (not supported)
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '4566',
        pathname: '/retailer-product-images/**',
      },
      {
        protocol: 'https',
        hostname: '*.cloudfront.net',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '*.amazonaws.com',
        pathname: '/**',
      },
    ],
  },

  // Trailing slash for S3 compatibility
  trailingSlash: true,
};

export default nextConfig;
