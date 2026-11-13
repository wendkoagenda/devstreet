# Site d'un namespace une fois le certificat obtenu. Contrat du proxy : 00readme/README_SAME_ORIGIN_COOKIES.md §3.2.
# Gabarit : __DOMAIN__ et __NAMESPACE__ sont remplaces par deploy/vm/deployer.sh (valeurs deja validees).
server {
    listen 80;
    server_name __DOMAIN__;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Django ne redirige pas lui-meme vers HTTPS (SECURE_SSL_REDIRECT = False)
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    http2 on;
    server_name __DOMAIN__;

    ssl_certificate /etc/letsencrypt/live/__DOMAIN__/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/__DOMAIN__/privkey.pem;

    # Noms de conteneurs : voir deploy/compose/compose.yml. Via variables, ils sont resolus a la requete.
    set $backend_upstream http://__NAMESPACE__-backend:8000;
    set $frontend_upstream http://__NAMESPACE__-frontend:8080;

    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 120s;

    # Le prefixe /api n'est jamais retire : Django attend /api/auth/login
    location /api/ {
        proxy_pass $backend_upstream;
    }

    # Django les refuse deja quand ENABLE_ADMIN / ENABLE_API_DOCS sont desactives
    location ~ ^/(admin|swagger|redoc)([/.]|$) {
        proxy_pass $backend_upstream;
    }

    location /static/ {
        alias /srv/public/__NAMESPACE__/static/;
        expires 7d;
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
    }

    # Fichiers envoyes par les utilisateurs : jamais executes sur ce domaine (HTML, SVG...)
    location /media/ {
        alias /srv/public/__NAMESPACE__/media/;
        add_header Content-Disposition "attachment" always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
        add_header Content-Security-Policy "default-src 'none'; sandbox" always;
    }

    # Objets MinIO / S3 en lecture seule (GET/HEAD). Variable = resolution a la requete (502 si MinIO absent).
    set $minio_upstream http://minio-serveur:9000;
    location /stockage/ {
        limit_except GET HEAD {
            deny all;
        }
        rewrite ^/stockage/(.*)$ /$1 break;
        proxy_pass $minio_upstream;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        add_header Content-Disposition "attachment" always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-Frame-Options DENY always;
        add_header Content-Security-Policy "default-src 'none'; sandbox" always;
    }

    location / {
        proxy_pass $frontend_upstream;
    }
}
