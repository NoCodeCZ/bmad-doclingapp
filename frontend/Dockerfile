# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Accept build arguments with defaults (these are public env vars, safe to hardcode)
ARG NEXT_PUBLIC_SUPABASE_URL=https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY
ARG NEXT_PUBLIC_API_URL=http://backend:8080

# Set as environment variables for build
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/package.json ./package.json

# Expose port
EXPOSE 3000

ENV PORT 3000

# Start the application
CMD ["node", "server.js"]