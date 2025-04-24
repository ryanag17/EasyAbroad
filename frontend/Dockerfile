# Use official NGINX image
FROM nginx:alpine

# Remove default NGINX static files
RUN rm -rf /usr/share/nginx/html/*

# Copy your frontend files into the NGINX web root
COPY . /usr/share/nginx/html

# Optional: Expose port (not strictly needed with docker-compose)
EXPOSE 80
