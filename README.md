## Chat To Edit Image

A toy project that let users to generate and edit images through text messages using either Stable Diffusion or Flux models.

## Model Selection

The server supports two AI models:
- **Stable Diffusion 2.1**: Default model, supports negative prompts, lower memory usage
- **FLUX.1 Dev**: Higher quality output, no negative prompts, higher memory usage

Model selection is done at server startup via environment variable or command line argument.

## Development vs Production

### Development Mode (with hot reloading)
```bash
make dev
```
This will:
- Run Next.js in development mode with hot reloading
- Mount source code as volumes for live updates
- Use `docker-compose.dev.yml` configuration
- Use Stable Diffusion model by default

### Production Mode
```bash
make up
```
This will:
- Build optimized production bundles
- Run in production mode
- Use standard `docker-compose.yml` configuration
- Use Stable Diffusion model by default

### Using Different Models

#### With Stable Diffusion (default):
```bash
make up
# or
docker-compose up --build
```

#### With Flux:
```bash
docker-compose -f docker-compose.flux.yml up --build
```

#### Custom Model Selection:
```bash
# Set environment variable
export MODEL_TYPE=flux
make up

# Or use docker-compose override
cp docker-compose.override.yml.example docker-compose.override.yml
# Edit docker-compose.override.yml to set MODEL_TYPE=flux
docker-compose up --build
```

## Why Hot Reloading Didn't Work

The original setup was running in production mode because:
1. Dockerfile was building the app with `yarn build`
2. Starting with `yarn start` (production server)
3. No volume mounting for source code
4. No development-specific configuration

The new `make dev` command fixes these issues by using development-specific Docker configuration.
