#!/usr/bin/env python3
"""
Variables et secrets de deploiement (GitHub Actions) et preparation des VM.

    python git-cli/deploy_env.py definir --branche sandbox          # cree l'environnement, pousse les 5 fichiers locaux
    python git-cli/deploy_env.py etat --branche sandbox             # compare GitHub a la liste de reference
    python git-cli/deploy_env.py preparer-vm --branche sandbox --hote 203.0.113.10 --admin-user ubuntu
    python git-cli/deploy_env.py preparer-vm-gcp --branche prod --projet mon-projet --zone europe-west1-b --instance vm-prod
    python git-cli/deploy_env.py tunnel --branche sandbox           # tunnels locaux base + Grafana + MinIO (8 h)
    # definir / etat / preparer-vm* : HEAD local doit etre egal a --branche (sinon refus).
    # tunnel : lit .env.vm.<branche>, n'exige ni master ni branche locale.

Fichiers locaux (a la racine, ignores par Git, format .env sans commentaire en fin de ligne) :
    backend.env.<branche>, frontend.env.<branche>, .env.deploy.<branche>, observabilite.env.<branche>, minio.env.<branche>, gitea.env.<branche>
Les noms attendus viennent de backend/.env.example, frontend/.env.example et de backend/scripts/deploy_env/spec.py.
Les valeurs vont dans l'environnement GitHub qui porte le nom de la branche, reserve a cette seule branche.
Reserve aux emails de GIT_MASTER_EMAILS (git-cli/access_control.conf), sauf tunnel. Voir 00readme/PLAN_CD.md.
"""
import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import git_utils

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from scripts.deploy_env import spec as reference  # noqa: E402

LOCAL_FILES = {
    "backend": "backend.env.{branche}",
    "frontend": "frontend.env.{branche}",
    "deploy": ".env.deploy.{branche}",
    "observabilite": "observabilite.env.{branche}",
    "minio": "minio.env.{branche}",
    "gitea": "gitea.env.{branche}",
}
# Infos de connexion admin a la VM pour preparer-vm : restent sur le poste, jamais envoyees a GitHub
LOCAL_VM_FILE = ".env.vm.{branche}"
VM_FILE_OPTIONS = {"VM_HOTE": "hote", "VM_ADMIN_USER": "admin_user", "VM_CLE_ADMIN": "cle_admin"}
HOST_PATTERN = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$")
USER_PATTERN = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")
DEPLOY_USER = "deploy"
# Tunnel local : duree alignee sur le TTL du forward Postgres cote VM (8 h)
TUNNEL_HEURES = 8
TUNNEL_LOCAL_DB = 15432
TUNNEL_LOCAL_GRAFANA = 13000
TUNNEL_LOCAL_MINIO = 19001
TUNNEL_REMOTE_DB = "127.0.0.1:5432"
TUNNEL_REMOTE_GRAFANA = "127.0.0.1:3000"
TUNNEL_REMOTE_MINIO = "127.0.0.1:9001"
TUNNEL_RECONNECT_SECONDS = 5
TUNNEL_FAST_FAIL_SECONDS = 15
TUNNEL_MAX_FAST_FAILS = 3


class Failure(Exception):
    """Erreur a afficher telle quelle, sans trace."""


def ensure_master():
    try:
        _, email = git_utils.get_git_identity()
    except RuntimeError as error:
        raise Failure(str(error))
    if email not in git_utils.GIT_MASTER_EMAILS:
        raise Failure(
            f"Cette commande est reservee aux GIT_MASTER_EMAILS ({git_utils.ACCESS_CONTROL_FILE}). Email actuel : {email}"
        )


def ensure_branche_locale(branche):
    """Refuse definir / etat / preparer-vm si HEAD local n'est pas la branche cible (--branche)."""
    code, output = git_utils.run_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=REPO_ROOT,
    )
    if code != 0 or not output:
        raise Failure("Impossible de detecter la branche Git locale.")
    courante = output.strip()
    if courante == "HEAD":
        raise Failure(f"Detached HEAD : placez-vous sur la branche {branche} (git checkout {branche}).")
    if courante != branche:
        raise Failure(
            f"Branche locale « {courante} » : pour --branche {branche}, faites d'abord : git checkout {branche}"
        )


def gh(arguments, input_text=None):
    # Octets et non texte : en mode texte, Windows convertirait chaque \n envoye en \r\n (cle SSH privee corrompue)
    try:
        completed = subprocess.run(
            ["gh", *arguments],
            input=None if input_text is None else input_text.encode("utf-8"),
            capture_output=True,
            cwd=REPO_ROOT,
        )
    except FileNotFoundError:
        raise Failure("La commande gh (GitHub CLI) est introuvable. Installez-la puis lancez : gh auth login")
    return (
        completed.returncode,
        completed.stdout.decode("utf-8", errors="replace").strip(),
        completed.stderr.decode("utf-8", errors="replace").strip(),
    )


def repository():
    code, out, err = gh(["repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"])
    if code != 0 or not out:
        raise Failure(f"Depot GitHub introuvable (gh repo view) : {err}")
    return out


def ensure_ignored(path):
    """Un fichier de valeurs ne doit jamais pouvoir etre commite."""
    code, _ = git_utils.run_command(["git", "check-ignore", "-q", str(path)], cwd=REPO_ROOT)
    if code != 0:
        raise Failure(f"{path.name} n'est pas ignore par Git (.gitignore). Refus de le lire.")


def read_local(source, branche):
    path = REPO_ROOT / LOCAL_FILES[source].format(branche=branche)
    if not path.is_file():
        raise Failure(f"Fichier manquant : {path.name} (a creer a la racine du depot).")
    return read_dotenv(path)


def read_dotenv(path):
    ensure_ignored(path)
    try:
        return reference.parse_dotenv(path.read_text(encoding="utf-8"))
    except reference.SpecError as error:
        raise Failure(f"{path.name} : {error}")


def set_value(repo, branche, name, value, secret):
    kind = "secret" if secret else "variable"
    code, _, err = gh([kind, "set", name, "--env", branche, "--repo", repo], input_text=value)
    if code != 0:
        raise Failure(f"Echec de l'ecriture de {name} (environnement {branche}) : {err}")


def get_environment(repo, branche):
    """Environnement GitHub `branche` (dict de l'API), ou None s'il n'existe pas."""
    code, out, _ = gh(["api", f"repos/{repo}/environments/{branche}"])
    return json.loads(out) if code == 0 else None


def branch_rules(repo, branche):
    """Regles « Deployment branches and tags » de l'environnement : ensemble de (type, nom)."""
    code, out, err = gh(["api", f"repos/{repo}/environments/{branche}/deployment-branch-policies"])
    if code != 0:
        raise Failure(f"Regles de branche de {branche} illisibles : {err}")
    return {(rule.get("type", "branch"), rule["name"]) for rule in json.loads(out).get("branch_policies", [])}


def branch_policy_errors(repo, branche):
    """Ecarts a la regle « environnement utilisable par la seule branche du meme nom ». Liste vide si conforme."""
    environment = get_environment(repo, branche)
    if environment is None:
        return [f"environnement {branche} introuvable sur GitHub (lancez : definir --branche {branche})."]
    policy = environment.get("deployment_branch_policy") or {}
    if not policy.get("custom_branch_policies"):
        return [f"environnement {branche} ouvert a toutes les branches : ses secrets sont lisibles depuis n'importe quelle branche."]
    rules = branch_rules(repo, branche)
    if rules != {("branch", branche)}:
        return [f"environnement {branche} : regles de branche {sorted(name for _, name in rules)}, attendu exactement ['{branche}']."]
    return []


def ensure_environment(repo, branche):
    """
    Cree l'environnement GitHub `branche` s'il manque et le reserve a la branche du meme nom. Idempotent : un
    environnement deja conforme n'est pas modifie (ses autres reglages, poses dans l'interface, sont conserves).
    Sans cette regle, un workflow de n'importe quelle branche pourrait declarer `environment: prod` et lire ses secrets.
    """
    environment = get_environment(repo, branche)
    policy = (environment or {}).get("deployment_branch_policy") or {}
    if environment is None or not policy.get("custom_branch_policies"):
        body = json.dumps({"deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}})
        code, _, err = gh(["api", "--method", "PUT", f"repos/{repo}/environments/{branche}", "--input", "-"], input_text=body)
        if code != 0:
            raise Failure(
                f"Impossible de creer l'environnement {branche} reserve a la branche {branche} : {err}\n"
                "Rien n'a ete ecrit : sans cette regle, ses secrets seraient lisibles depuis toute branche."
            )
    if ("branch", branche) not in branch_rules(repo, branche):
        code, _, err = gh([
            "api", "--method", "POST", f"repos/{repo}/environments/{branche}/deployment-branch-policies",
            "-f", f"name={branche}", "-f", "type=branch",
        ])
        if code != 0:
            raise Failure(f"Impossible de reserver l'environnement {branche} a la branche {branche} : {err}")
    # Une regle en trop (autre branche) n'est jamais retiree d'office : on s'arrete et on la signale
    errors = branch_policy_errors(repo, branche)
    if errors:
        raise Failure(errors[0] + " Corrigez dans Settings > Environments, puis relancez.")


def current_values(repo, branche):
    """Noms des secrets et {nom: valeur} des variables deja dans l'environnement (vides s'il n'existe pas encore)."""
    if get_environment(repo, branche) is None:
        return set(), {}
    code, out, err = gh(["secret", "list", "--env", branche, "--repo", repo, "--json", "name", "--jq", ".[].name"])
    if code != 0:
        raise Failure(f"gh secret list a echoue (droits d'administration du depot requis) : {err}")
    secrets = set(out.split())
    code, out, err = gh(["variable", "list", "--env", branche, "--repo", repo, "--json", "name,value"])
    if code != 0:
        raise Failure(f"gh variable list a echoue (droits d'administration du depot requis) : {err}")
    return secrets, {item["name"]: item["value"] for item in json.loads(out or "[]")}


def delete_value(repo, branche, name, secret):
    kind = "secret" if secret else "variable"
    code, _, err = gh([kind, "delete", name, "--env", branche, "--repo", repo])
    if code != 0:
        raise Failure(f"Echec de la suppression de {kind} {name} (environnement {branche}) : {err}")


def plan_changes(entries, secrets, variables):
    """
    Upsert : (ecritures, suppressions, nombre inchange). Une variable identique n'est pas reecrite ; un secret n'est pas
    relisible, il est donc reecrit (meme resultat). Un nom enregistre avec le mauvais type est supprime apres l'ecriture
    du bon type. Les noms absents des fichiers locaux ne sont jamais supprimes.
    """
    writes, deletes, unchanged = [], [], 0
    for name, value, secret in entries:
        if secret:
            writes.append((name, value, secret, "remplace" if name in secrets else "cree"))
        elif name not in variables:
            writes.append((name, value, secret, "cree"))
        elif variables[name] != value:
            writes.append((name, value, secret, "mis a jour"))
        else:
            unchanged += 1
        if name in (variables if secret else secrets):
            deletes.append((name, not secret))
    return writes, deletes, unchanged


def cmd_definir(args):
    """Idempotent : relancer avec les memes fichiers locaux ne change rien (voir plan_changes)."""
    ensure_master()
    ensure_branche_locale(args.branche)
    definitions = reference.load_spec(REPO_ROOT)
    entries, errors = [], []
    for source in ("backend", "frontend", "deploy", "observabilite", "minio", "gitea"):
        if source == "gitea" and not (REPO_ROOT / LOCAL_FILES[source].format(branche=args.branche)).is_file():
            continue  # forge facultative : un environnement sans gitea.env.<branche> n'en a pas
        values = read_local(source, args.branche)
        problems = reference.check_values(definitions, source, values)
        if source == "gitea":
            problems += [f"{var.name} : obligatoire quand le fichier existe." for var in definitions
                         if var.source == "gitea" and not values.get(var.name)]
        errors.extend(f"{LOCAL_FILES[source].format(branche=args.branche)} : {p}" for p in problems)
        for var in definitions:
            if var.source == source and values.get(var.name):
                entries.append((reference.gh_name(var.name, args.branche), values[var.name], var.secret))
    if errors:
        raise Failure("Fichiers locaux invalides :\n  - " + "\n  - ".join(errors))

    repo = repository()
    policy_errors = branch_policy_errors(repo, args.branche)
    secrets, variables = current_values(repo, args.branche)
    writes, deletes, unchanged = plan_changes(entries, secrets, variables)
    print(f"Depot : {repo}   Environnement : {args.branche}")
    print(f"  environnement  {'pret' if not policy_errors else 'a creer ou a reserver a sa branche'}")
    for name, _, secret, action in writes:
        print(f"  {'secret  ' if secret else 'variable'}  {name} : {action}")
    for name, secret in deletes:
        print(f"  {'secret  ' if secret else 'variable'}  {name} : supprime (mauvais type)")
    print(f"  {unchanged} variable(s) deja a jour. Les valeurs ne sont pas affichees. VM_SSH_* sont ecrites par preparer-vm.")

    if not policy_errors and not writes and not deletes:
        git_utils.print_success(f"Environnement {args.branche} deja a jour : rien a faire.")
        return
    if args.dry_run:
        print("Simulation : rien n'a ete ecrit.")
        return
    if not git_utils.ask_confirm(f"Appliquer ces changements a l'environnement {args.branche}"):
        print("Annule.")
        return
    ensure_environment(repo, args.branche)
    for name, value, secret, _ in writes:
        set_value(repo, args.branche, name, value, secret)
    for name, secret in deletes:
        delete_value(repo, args.branche, name, secret)
    git_utils.print_success(
        f"{len(writes)} valeur(s) ecrite(s), {len(deletes)} supprimee(s), {unchanged} inchangee(s). "
        f"Verifiez avec : etat --branche {args.branche}"
    )


def cmd_etat(args):
    ensure_master()
    ensure_branche_locale(args.branche)
    repo = repository()
    if get_environment(repo, args.branche) is None:
        print(f"Environnement {args.branche} incomplet :")
        print(f"  - environnement {args.branche} introuvable sur GitHub (lancez : definir --branche {args.branche}).")
        raise SystemExit(1)
    secret_names, variables = current_values(repo, args.branche)
    acces = variables.get(reference.gh_name("DEPLOY_ACCES", args.branche)) or None
    errors = branch_policy_errors(repo, args.branche) + reference.check_environment(
        reference.load_spec(REPO_ROOT), args.branche, secret_names, {name for name, value in variables.items() if value}, acces
    )
    if errors:
        print(f"Environnement {args.branche} incomplet :")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)
    git_utils.print_success(f"Environnement {args.branche} conforme a la liste de reference.")


# --- preparer-vm -------------------------------------------------------------

def ssh_command(host, user, known_hosts, key=None):
    command = [
        "ssh",
        "-o", f"UserKnownHostsFile={known_hosts.as_posix()}",
        "-o", "StrictHostKeyChecking=yes",
        "-o", "HostKeyAlgorithms=ssh-ed25519",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=15",
    ]
    if key:
        command += ["-i", str(key), "-o", "IdentitiesOnly=yes"]
    return command + [f"{user}@{host}"]


def run_remote(command, remote, script=None):
    """Execute `remote` sur la VM, `script` (fichier du depot) sur stdin. Octets : pas de conversion de fin de ligne."""
    data = script.read_bytes().replace(b"\r\n", b"\n") if script else None
    return subprocess.run([*command, remote], input=data, check=False).returncode


def pin_host_key(host, known_hosts):
    scan = subprocess.run(
        ["ssh-keyscan", "-T", "10", "-t", "ed25519", host], capture_output=True, text=True, check=False
    )
    lines = [line for line in scan.stdout.splitlines() if line.strip() and not line.startswith("#")]
    if not lines:
        raise Failure(f"Aucune cle d'hote ed25519 recue de {host} (VM allumee ? port 22 ouvert ?).")
    known_hosts.write_text(lines[0] + "\n", encoding="utf-8")
    fingerprint = subprocess.run(
        ["ssh-keygen", "-lf", str(known_hosts)], capture_output=True, text=True, check=False
    ).stdout.strip()
    print(f"Empreinte presentee par {host} :\n  {fingerprint}")
    print("Comparez-la a celle de votre fournisseur (console de la VM) avant de continuer.")
    if not git_utils.ask_confirm("Cette empreinte est bien celle de votre VM"):
        raise Failure("Empreinte non confirmee.")
    return lines[0]


def resolve_cle_admin(cle_admin):
    """Chemin de la cle admin : ~ expandu ; relatif = depuis la racine du depot (ex. .ssh/sshsandbox)."""
    if not cle_admin:
        return None
    path = Path(cle_admin).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def resolve_vm_options(args):
    """Complete les options absentes de preparer-vm avec .env.vm.<branche> (facultatif) : la ligne de commande prime."""
    path = REPO_ROOT / LOCAL_VM_FILE.format(branche=args.branche)
    values = read_dotenv(path) if path.is_file() else {}
    unknown = sorted(set(values) - set(VM_FILE_OPTIONS))
    if unknown:
        raise Failure(f"{path.name} : noms inconnus {', '.join(unknown)} (attendus : {', '.join(VM_FILE_OPTIONS)}).")
    for name, option in VM_FILE_OPTIONS.items():
        if not getattr(args, option) and values.get(name):
            setattr(args, option, values[name])
    missing = [
        f"--{option.replace('_', '-')} (ou {name} dans {path.name})"
        for name, option in VM_FILE_OPTIONS.items()
        if option != "cle_admin" and not getattr(args, option)
    ]
    if missing:
        raise Failure("Infos de la VM manquantes : " + ", ".join(missing) + ".")


def cmd_preparer_vm(args):
    ensure_master()
    ensure_branche_locale(args.branche)
    resolve_vm_options(args)
    if not HOST_PATTERN.match(args.hote):
        raise Failure("Hote invalide (adresse IP ou nom de domaine).")
    if not USER_PATTERN.match(args.admin_user):
        raise Failure("--admin-user doit etre root ou un utilisateur avec sudo sans mot de passe (ex. ubuntu).")
    sudo = "" if args.admin_user == "root" else "sudo -n "
    admin_key = resolve_cle_admin(args.cle_admin)
    if admin_key and not admin_key.is_file():
        raise Failure(f"Cle d'administration introuvable : {admin_key}")
    repo = repository()

    print(f"VM {args.hote} -> environnement {args.branche} du depot {repo}.")
    print("Actions : Docker, utilisateur deploy, pare-feu (22/80/443), fail2ban, mises a jour de securite,")
    print("          puis SSH par cle uniquement (mot de passe et root desactives).")
    if not git_utils.ask_confirm("Preparer cette VM"):
        print("Annule.")
        return

    # Avant de toucher a la VM : si l'environnement ne peut pas etre reserve a sa branche, on s'arrete ici
    ensure_environment(repo, args.branche)

    workdir = Path(tempfile.mkdtemp(prefix="deploy-vm-"))
    try:
        known_hosts = workdir / "known_hosts"
        known_hosts_line = pin_host_key(args.hote, known_hosts)

        admin = ssh_command(args.hote, args.admin_user, known_hosts, admin_key)
        if run_remote(admin, f"{sudo}true") != 0:
            raise Failure("Connexion admin refusee, ou sudo demande un mot de passe (cle chargee dans l'agent ? --cle-admin ?).")

        key_file = workdir / "deploy_key"
        generated = subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", f"deploy-{args.branche}", "-f", str(key_file)],
            check=False,
        )
        if generated.returncode != 0:
            raise Failure("ssh-keygen a echoue.")
        pubkey = Path(f"{key_file}.pub").read_text(encoding="utf-8").strip()

        git_utils.print_step("Phase a : installation et pare-feu")
        remote = f"{sudo}env DEPLOY_PUBKEY={shlex.quote(pubkey)} bash -s -- a"
        if run_remote(admin, remote, REPO_ROOT / "deploy/vm/preparer.sh") != 0:
            raise Failure("La phase a a echoue (voir ci-dessus). Rien n'a ete ecrit sur GitHub.")

        deploy = ssh_command(args.hote, DEPLOY_USER, known_hosts, key_file)
        if run_remote(deploy, "docker info --format '{{.ServerVersion}}'") != 0:
            raise Failure("Connexion de l'utilisateur deploy impossible. Le durcissement SSH n'a PAS ete applique.")

        git_utils.print_step("Ecriture des acces SSH sur GitHub")
        for name, value, secret in (
            ("VM_SSH_HOST", args.hote, True),
            ("VM_SSH_USER", DEPLOY_USER, True),
            ("VM_SSH_PRIVATE_KEY", key_file.read_text(encoding="utf-8"), True),
            ("VM_SSH_KNOWN_HOSTS", known_hosts_line, False),
        ):
            set_value(repo, args.branche, reference.gh_name(name, args.branche), value, secret)

        git_utils.print_step("Phase b : durcissement SSH")
        if run_remote(admin, f"{sudo}bash -s -- b", REPO_ROOT / "deploy/vm/preparer.sh") != 0:
            raise Failure("La phase b a echoue. Les acces SSH sont deja sur GitHub ; corrigez puis relancez.")
        if run_remote(deploy, "true") != 0:
            raise Failure("Apres durcissement, la connexion deploy echoue : verifiez la VM depuis la console du fournisseur.")

        git_utils.print_step("Controle de la VM")
        status = run_remote(deploy, "sh -s", REPO_ROOT / "deploy/vm/verifier.sh")
        if status != 0:
            raise Failure("La VM est preparee mais le controle signale des ecarts (ci-dessus).")
        git_utils.print_success(f"VM preparee. Suite : definir --branche {args.branche}, puis etat --branche {args.branche}.")
    finally:
        # La cle privee de deploiement n'existe plus que dans GitHub
        shutil.rmtree(workdir, ignore_errors=True)


def cmd_preparer_vm_gcp(args):
    """VM GCP sans IP publique : meme preparation que preparer-vm, par le tunnel IAP, sans cle SSH ni secret."""
    ensure_master()
    ensure_branche_locale(args.branche)
    for name, value in (
        ("GCP_PROJECT_ID", args.projet), ("GCP_ZONE", args.zone), ("GCP_INSTANCE", args.instance),
    ):
        problem = reference.validate_value(name, value)
        if problem:
            raise Failure(problem)
    gcloud = shutil.which("gcloud")
    if not gcloud:
        raise Failure("La commande gcloud est introuvable (Google Cloud SDK) : https://cloud.google.com/sdk/docs/install")

    print(f"VM {args.instance} ({args.projet}, {args.zone}) par le tunnel IAP.")
    print("Actions : Docker, utilisateur deploy, pare-feu (80/443 ; SSH reserve au tunnel IAP), fail2ban,")
    print("          mises a jour de securite, SSH par cle uniquement. Aucune cle ni secret n'est cree.")
    print("Votre compte gcloud a besoin de roles/iap.tunnelResourceAccessor et roles/compute.osAdminLogin (voir 00readme/PLAN_CD.md).")
    if not git_utils.ask_confirm("Preparer cette VM"):
        print("Annule.")
        return

    base = [
        gcloud, "compute", "ssh", args.instance, "--project", args.projet, "--zone", args.zone,
        "--tunnel-through-iap", "--ssh-key-expire-after=30m", "--command",
    ]
    git_utils.print_step("Preparation")
    if run_remote(base, "sudo -n bash -s -- g", REPO_ROOT / "deploy/vm/preparer.sh") != 0:
        raise Failure("La preparation a echoue (voir ci-dessus).")
    git_utils.print_step("Controle de la VM")
    if run_remote(base, "sudo -n -H -u deploy sh -s", REPO_ROOT / "deploy/vm/verifier.sh") != 0:
        raise Failure("La VM est preparee mais le controle signale des ecarts (ci-dessus).")
    git_utils.print_success(
        f"VM preparee. Suite : renseignez les GCP_* dans .env.deploy.{args.branche}, puis definir et etat --branche {args.branche}."
    )


# --- tunnel ------------------------------------------------------------------

def tunnel_command(host, user, key=None):
    """Construit la commande ssh -N (base, Grafana, MinIO console), liee a 127.0.0.1."""
    command = [
        "ssh",
        "-N",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
        "-o", "ExitOnForwardFailure=yes",
        "-o", "ConnectTimeout=15",
        "-o", "StrictHostKeyChecking=accept-new",
        "-L", f"127.0.0.1:{TUNNEL_LOCAL_DB}:{TUNNEL_REMOTE_DB}",
        "-L", f"127.0.0.1:{TUNNEL_LOCAL_GRAFANA}:{TUNNEL_REMOTE_GRAFANA}",
        "-L", f"127.0.0.1:{TUNNEL_LOCAL_MINIO}:{TUNNEL_REMOTE_MINIO}",
    ]
    if key:
        command += ["-i", str(key), "-o", "IdentitiesOnly=yes"]
    return command + [f"{user}@{host}"]


def run_tunnel_session(command, duration_seconds, run=subprocess.run, sleep=time.sleep, clock=time.monotonic):
    """
    Maintient le tunnel jusqu'a duration_seconds : reconnexion apres coupure, arret a l'echeance.
    Apres TUNNEL_MAX_FAST_FAILS echecs de suite en moins de TUNNEL_FAST_FAIL_SECONDS : Failure.
    """
    deadline = clock() + duration_seconds
    fast_fails = 0
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            print(f"Duree de {TUNNEL_HEURES} h ecoulee : tunnel arrete.")
            return
        started = clock()
        try:
            result = run(command, timeout=remaining)
        except subprocess.TimeoutExpired:
            print(f"Duree de {TUNNEL_HEURES} h ecoulee : tunnel arrete.")
            return
        except KeyboardInterrupt:
            print("\nTunnel interrompu (Ctrl+C).")
            return
        elapsed = clock() - started
        if result.returncode == 0:
            fast_fails = 0
        elif elapsed < TUNNEL_FAST_FAIL_SECONDS:
            fast_fails += 1
            if fast_fails >= TUNNEL_MAX_FAST_FAILS:
                raise Failure(
                    "Connexion SSH refusee, ou ports locaux 15432 / 13000 / 19001 deja utilises "
                    "(un tunnel tourne peut-etre deja)."
                )
        else:
            fast_fails = 0
        remaining = deadline - clock()
        if remaining <= 0:
            print(f"Duree de {TUNNEL_HEURES} h ecoulee : tunnel arrete.")
            return
        wait = min(TUNNEL_RECONNECT_SECONDS, remaining)
        print(f"Tunnel coupe, reconnexion dans {wait:.0f} s…")
        try:
            sleep(wait)
        except KeyboardInterrupt:
            print("\nTunnel interrompu (Ctrl+C).")
            return


def cmd_tunnel(args):
    """Ouvre les tunnels locaux base + Grafana + MinIO (8 h, keepalive, reconnexion). Lit .env.vm.<branche>."""
    resolve_vm_options(args)
    if not HOST_PATTERN.match(args.hote):
        raise Failure("Hote invalide (adresse IP ou nom de domaine).")
    if not USER_PATTERN.match(args.admin_user):
        raise Failure("--admin-user invalide (ex. ubuntu, sandbox).")
    admin_key = resolve_cle_admin(args.cle_admin)
    if args.cle_admin and (not admin_key or not admin_key.is_file()):
        raise Failure(f"Cle d'administration introuvable : {admin_key or args.cle_admin}")

    command = tunnel_command(args.hote, args.admin_user, admin_key)
    fin = datetime.now() + timedelta(hours=TUNNEL_HEURES)
    print(f"Tunnel vers {args.admin_user}@{args.hote} (arret prevu vers {fin.strftime('%H:%M')}, Ctrl+C pour couper).")
    print(f"  pgAdmin      : Host 127.0.0.1  Port {TUNNEL_LOCAL_DB}  (apres CD - MAINTENANCE db-forward)")
    print(f"  Grafana      : http://localhost:{TUNNEL_LOCAL_GRAFANA}")
    print(f"  Console MinIO : http://localhost:{TUNNEL_LOCAL_MINIO}")
    print("  Keepalive 30 s ; reconnexion auto si la liaison coupe.")
    run_tunnel_session(command, TUNNEL_HEURES * 3600)


def build_parser():
    parser = argparse.ArgumentParser(description="Variables, secrets et preparation des VM de deploiement.")
    commands = parser.add_subparsers(dest="commande", required=True)

    def branch_option(command):
        command.add_argument("--branche", required=True, choices=reference.BRANCHES)

    definir = commands.add_parser("definir", help="cree l'environnement GitHub et y pousse les fichiers locaux")
    branch_option(definir)
    definir.add_argument("--dry-run", action="store_true", help="liste les noms sans rien ecrire")
    definir.set_defaults(action=cmd_definir)

    etat = commands.add_parser("etat", help="compare GitHub a la liste de reference")
    branch_option(etat)
    etat.set_defaults(action=cmd_etat)

    vm = commands.add_parser("preparer-vm", help="prepare une VM Ubuntu LTS et ecrit les acces SSH sur GitHub")
    branch_option(vm)
    vm.add_argument("--hote", help="adresse IP ou nom de la VM (sinon : VM_HOTE de .env.vm.<branche>)")
    vm.add_argument("--admin-user", help="root, ou utilisateur avec sudo sans mot de passe (sinon : VM_ADMIN_USER) ; root : aucun sudo n'est ajoute")
    vm.add_argument(
        "--cle-admin",
        help="chemin de la cle privee SSH admin (sinon : VM_CLE_ADMIN dans .env.vm.<branche>, puis agent SSH) ; relatif = racine du depot",
    )
    vm.set_defaults(action=cmd_preparer_vm)

    vm_gcp = commands.add_parser("preparer-vm-gcp", help="prepare une VM GCP sans IP publique (tunnel IAP)")
    branch_option(vm_gcp)
    vm_gcp.add_argument("--projet", required=True, help="identifiant du projet GCP")
    vm_gcp.add_argument("--zone", required=True, help="zone de la VM (ex. europe-west1-b)")
    vm_gcp.add_argument("--instance", required=True, help="nom de l'instance")
    vm_gcp.set_defaults(action=cmd_preparer_vm_gcp)

    tunnel = commands.add_parser(
        "tunnel",
        help="ouvre les tunnels locaux base (15432), Grafana (13000) et MinIO (19001) (8 h, reconnexion)",
    )
    branch_option(tunnel)
    tunnel.add_argument("--hote", help="adresse IP ou nom de la VM (sinon : VM_HOTE de .env.vm.<branche>)")
    tunnel.add_argument("--admin-user", help="utilisateur SSH admin (sinon : VM_ADMIN_USER)")
    tunnel.add_argument(
        "--cle-admin",
        help="chemin de la cle privee SSH admin (sinon : VM_CLE_ADMIN dans .env.vm.<branche>, puis agent SSH)",
    )
    tunnel.set_defaults(action=cmd_tunnel)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        args.action(args)
    except Failure as error:
        print(f"Erreur : {error}", file=sys.stderr)
        return 1
    except reference.SpecError as error:
        print(f"Erreur : {error}", file=sys.stderr)
        return 1
    except git_utils.UserQuit:
        print("Interrompu.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
