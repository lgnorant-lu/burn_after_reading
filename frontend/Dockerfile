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

# Declare the build argument and set it as an environment variable
# so it's available to the 'npm run build' command.
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

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

# Expose port 3000 to align with the nginx.conf.
EXPOSE 3000

# The command to start the Nginx server in the foreground.
CMD ["nginx", "-g", "daemon off;"]