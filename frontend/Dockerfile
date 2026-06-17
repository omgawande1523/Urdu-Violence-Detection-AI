FROM node:18-alpine

WORKDIR /app

# Copy dependency files
COPY frontend/package.json ./

# Install packages (using --legacy-peer-deps to avoid React 19 warnings if any)
RUN npm install --legacy-peer-deps

# Copy frontend source code
COPY frontend/ ./

EXPOSE 3000

CMD ["npm", "run", "dev"]
