FROM node:20-alpine
WORKDIR /app
RUN apk add --no-cache git && \
    git clone https://github.com/Kethen/aemu_postoffice.git /tmp/aemu && \
    cp -r /tmp/aemu/server_njs/* . && \
    rm -rf /tmp/aemu && \
    npm install && npx tsc
EXPOSE 27313/tcp
EXPOSE 27313/udp
CMD ["node", "aemu_postoffice.js"]
