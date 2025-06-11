# Multi-stage build for Vue.js frontend

# Stage 1: Build the Vue.js application
# Use a Node.js image to build the static files.
FROM node:18-alpine AS build

# Set the working directory inside the container.
WORKDIR /app

# Copy package.json and lock file.
COPY package.json package-lock.json* ./

# Install dependencies. Using 'npm ci' is often faster and more reliable for CI/CD.
RUN npm ci

# Copy the rest of the frontend source code.
COPY . .

# Build the application for production.
RUN npm run build

# Stage 2: Serve the application with a lean Nginx server
# Use a lightweight Nginx image.
FROM nginx:1.23-alpine

# The official Nginx image doesn't include curl by default.
# We add it here so our healthcheck in docker-compose.yml can work.
RUN apk add --no-cache curl

# Copy the built static files from the 'build' stage.
COPY --from=build /app/dist /usr/share/nginx/html

# Copy our custom Nginx configuration.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 to the outside world.
EXPOSE 80

# The command to start the Nginx server in the foreground.
CMD ["nginx", "-g", "daemon off;"]