import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // Enable hot reloading in Docker
  webpack: (config: any, { dev, isServer }) => {
    if (dev && !isServer) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      };
    }
    return config;
  },
};

export default nextConfig;
