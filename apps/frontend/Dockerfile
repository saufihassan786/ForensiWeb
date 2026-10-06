# ==============================================================================
# ForensiWeb Frontend — Container Definition
# ==============================================================================
FROM node:20-alpine AS base

WORKDIR /app

ENV NODE_ENV=development

# Copy package manifests and install dependencies
COPY package*.json ./
RUN npm install

# Copy application source code
COPY . .

# Set ownership to unprivileged node user
RUN chown -R node:node /app

USER node

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
