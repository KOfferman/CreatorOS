FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package.json
COPY web/package.json web/package.json
RUN npm install

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules node_modules
COPY . .
RUN npm --workspace web run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/web/.next web/.next
COPY --from=builder /app/web/public web/public
COPY --from=builder /app/web/package.json web/package.json
COPY --from=builder /app/web/next.config.js web/next.config.js
COPY --from=builder /app/node_modules node_modules

EXPOSE 3000
CMD ["npm", "run", "start", "--prefix", "web"]
