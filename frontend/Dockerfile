# ============================================================
# Athenec - Frontend (nginx sirviendo estaticos)
# ============================================================
FROM nginx:1.27-alpine

# Copia config personalizada (proxy /api al backend)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia estaticos al webroot
COPY . /usr/share/nginx/html

# Elimina archivos que no deben servirse publicamente
RUN rm -f /usr/share/nginx/html/Dockerfile /usr/share/nginx/html/.dockerignore /usr/share/nginx/html/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
