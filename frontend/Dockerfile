FROM nginx:alpine

# ONLY FOR PRODUCTION PHASE! SG 08.06
# # Clean default nginx folder
RUN rm -rf /usr/share/nginx/html/*

# Copy index.html from root
COPY index.html /usr/share/nginx/html/

# Copy everything inside frontend/ to web root
COPY frontend/ /usr/share/nginx/html/

EXPOSE 80