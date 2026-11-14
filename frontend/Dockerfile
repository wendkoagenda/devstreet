FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .

# Pas de valeur par defaut : definir VITE_API_URL et VITE_API_V1_URL en build-arg (--build-arg ou arguments de build de l'outil de deploiement).
# Ce sont des chemins ou URL publics (integres au JavaScript), jamais des secrets.
ARG VITE_API_URL
ARG VITE_API_V1_URL
# Facultative : absente = fichiers servis depuis /media/ ; true = fichiers lus via /api/v1/files/ (stockage S3/MinIO)
ARG VITE_USE_S3
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_V1_URL=$VITE_API_V1_URL
ENV VITE_USE_S3=$VITE_USE_S3

RUN test -n "$VITE_API_URL" || (echo "ERROR: VITE_API_URL is empty. Pass it as a build argument." && exit 1)
RUN test -n "$VITE_API_V1_URL" || (echo "ERROR: VITE_API_V1_URL is empty. Pass it as a build argument." && exit 1)
RUN npm run build

# Image sans root : nginx ecoute sur 8080 (un port < 1024 exige root)
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY nginx.main.conf /etc/nginx/nginx.conf
COPY security-headers.conf /etc/nginx/security-headers.conf
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Utilisateur nginx sans privileges de l'image (uid 101), explicite
USER 101

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
