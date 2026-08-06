# Build von diesem Dockerfile aus dem frontend/-Ordner:
#   docker build -t medic-frontend \
#     --build-arg NEXT_PUBLIC_API_URL=https://<backend-url> .
#
# WICHTIG: NEXT_PUBLIC_API_URL wird von Next.js beim "next build" fest in
# das Client-Bundle eingebacken (nicht erst zur Laufzeit gelesen!). Ohne
# --build-arg faellt es auf http://localhost:8000 zurueck, was in Azure
# nicht funktioniert. Bei einer Aenderung der Backend-URL muss das Image
# daher neu gebaut werden.

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
