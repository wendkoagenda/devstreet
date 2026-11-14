# Site de la forge Gitea avant l'obtention du certificat : seul le defi HTTP-01 est servi.
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
