# Build Stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Set API URL for production build (relative /api so Nginx handles proxying without CORS issues)
ARG VITE_API_BASE_URL=""
ARG VITE_API_V1_PREFIX="/api/v1"
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_API_V1_PREFIX=$VITE_API_V1_PREFIX

RUN npm run build

# Production Stage
FROM nginx:1.25-alpine AS runner

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
