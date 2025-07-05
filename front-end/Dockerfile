# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build args for environment variables
ARG VITE_API_URL=http://localhost:5000
ENV VITE_API_URL=$VITE_API_URL

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
