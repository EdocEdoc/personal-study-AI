# ---- Build Stage ----
FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files first (for caching)
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build the Vite app
RUN yarn build

# ---- Production Stage ----
FROM nginx:alpine

# Copy built files to Nginx web root
COPY --from=build /app/dist /usr/share/nginx/html

# Copy default Nginx configuration (optional)
# This ensures proper SPA routing (redirect all 404s to index.html)
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
