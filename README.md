## Chat To Edit Image

A toy project that let users to generate and edit images through text messages.

## Development vs Production

### Development Mode (with hot reloading)
```bash
make dev
```
This will:
- Run Next.js in development mode with hot reloading
- Mount source code as volumes for live updates
- Use `docker-compose.dev.yml` configuration

### Production Mode
```bash
make up
```
This will:
- Build optimized production bundles
- Run in production mode
- Use standard `docker-compose.yml` configuration

## Why Hot Reloading Didn't Work

The original setup was running in production mode because:
1. Dockerfile was building the app with `yarn build`
2. Starting with `yarn start` (production server)
3. No volume mounting for source code
4. No development-specific configuration

The new `make dev` command fixes these issues by using development-specific Docker configuration.
