# Wallboard — small Node 22 image, no npm dependencies.
# Build:  docker build -t wallboard .
# Run:    docker run -d -p 8080:8080 -v /volume1/docker/wallboard:/data --name wallboard wallboard
FROM node:22-alpine

ENV NODE_ENV=production \
    PORT=8080 \
    DATA_DIR=/data \
    CRAWL_INTERVAL_MINUTES=60

WORKDIR /app
COPY package.json ./
COPY server ./server
COPY public ./public

# /data holds state.json (layouts, timers, tasks), feed-cache.json and custom widgets.
RUN mkdir -p /data && chown -R node:node /data
VOLUME ["/data"]
USER node
EXPOSE 8080

HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- "http://127.0.0.1:${PORT}/api/health" >/dev/null || exit 1

CMD ["node", "server/index.js"]
