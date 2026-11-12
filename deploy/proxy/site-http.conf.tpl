# Site d'un namespace AVANT l'obtention du certificat : uniquement le defi HTTP-01 de Let's Encrypt.
# Gabarit : __DOMAIN__ et __NAMESPACE__ sont remplaces par deploy/vm/deployer.sh (valeurs deja validees).
server {
    listen 80;
    server_name __DOMAIN__;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 404;
    }
}
