FROM nginx:alpine

# Clean default files
RUN rm -rf /usr/share/nginx/html/*

# Copy frontend files from build context's parent
COPY ../ /usr/share/nginx/html

EXPOSE 80