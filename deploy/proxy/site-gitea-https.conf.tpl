# Site de la forge Gitea une fois le certificat obtenu (conteneur « gitea », reseau « proxy »).
# Gabarit : __DOMAIN__ est remplace par deploy/vm/gitea.sh (valeur deja validee).
server {
    listen 80;
    server_name __DOMAIN__;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

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

    # Les pushs Git peuvent depasser la limite globale (25 Mo) ; la taille reelle est bornee par Gitea
    client_max_body_size 512m;

    # Variable : resolue a la requete (502 si Gitea est arrete, sans empecher nginx de demarrer)
    set $gitea_upstream http://gitea:3000;

    location / {
        proxy_pass $gitea_upstream;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_request_buffering off;
        proxy_read_timeout 300s;
    }
}
