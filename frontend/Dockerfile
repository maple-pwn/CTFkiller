FROM node:20-alpine

WORKDIR /app

RUN addgroup -g 10001 appgroup && \
    adduser -u 10001 -G appgroup -D appuser

COPY package*.json /app/
RUN npm install && npm cache clean --force

COPY --chown=appuser:appgroup . /app

RUN npm run build

USER appuser

EXPOSE 3000

CMD ["npm", "start"]
