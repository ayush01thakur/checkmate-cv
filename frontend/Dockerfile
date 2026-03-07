FROM nginx:alpine

# Fix Windows line endings in nginx config
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
RUN sed -i 's/\r//' /etc/nginx/conf.d/default.conf

COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/

EXPOSE 80