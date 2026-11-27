/** @type {import('next').NextConfig} */
const apiOrigin = process.env.NOMAD_API_INTERNAL_URL ?? "http://localhost:8000";

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      { source: "/health", destination: `${apiOrigin}/health` },
      {
        source: "/api/knowledge/:path*",
        destination: `${apiOrigin}/api/knowledge/:path*`,
      },
      {
        source: "/api/ai/:path*",
        destination: `${apiOrigin}/api/ai/:path*`,
      },
    ];
  },
};

export default nextConfig;
