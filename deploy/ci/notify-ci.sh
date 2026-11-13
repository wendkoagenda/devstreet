#!/usr/bin/env bash
# Envoie une notification de CI Slack et/ou Teams depuis CI - ORCHESTRATEUR.
# Variables attendues : REF_LABEL, SHA, ACTOR, RUN_URL, STATUT (succes|echec),
#   EVENEMENT, SLACK_NOTIF_WEBHOOK et/ou TEAMS_NOTIF_WEBHOOK (facultatifs),
#   ETAPE, PR_NUMBER (facultatifs).
# Ne fait jamais echouer le job : avertissement si aucun webhook ou si un curl echoue.

set -eu

# Vrai si la variable facultative est definie et non vide (sans expansion d'une variable absente sous set -u).
est_renseignee() {
  [[ -v "$1" && -n "${!1}" ]]
}

sha_court="${SHA:0:8}"
sujet="$(git log -1 --format=%s "$SHA" 2>/dev/null || true)"
if [ -z "$sujet" ]; then
  sujet="(sujet indisponible)"
fi

if [ "$STATUT" = "succes" ]; then
  titre="CI reussie"
  banniere="SUCCES"
  couleur_slack="#2EB67D"
  style_teams="good"
  couleur_texte="good"
else
  titre="CI echouee"
  banniere="ECHEC"
  couleur_slack="#E01E5A"
  style_teams="attention"
  couleur_texte="attention"
fi

lignes=(
  "[$banniere] $titre — $REF_LABEL"
  "Evenement : ${EVENEMENT:?EVENEMENT est obligatoire}"
  "Commit : $sha_court"
  "Sujet : $sujet"
  "Acteur : ${ACTOR:?ACTOR est obligatoire}"
)
if est_renseignee PR_NUMBER; then
  lignes+=("Pull request : #$PR_NUMBER")
fi
if [ "$STATUT" != "succes" ] && est_renseignee ETAPE; then
  lignes+=("Etape : $ETAPE")
fi
lignes+=("Run : $RUN_URL")

texte="$(printf '%s\n' "${lignes[@]}")"

resume() {
  {
    echo "### Notification CI ($STATUT)"
    echo '```'
    printf '%s\n' "$texte"
    echo '```'
  } >> "$GITHUB_STEP_SUMMARY"
}

if ! est_renseignee SLACK_NOTIF_WEBHOOK && ! est_renseignee TEAMS_NOTIF_WEBHOOK; then
  echo "::warning::Aucun webhook de notification configure (SLACK_NOTIF_WEBHOOK / TEAMS_NOTIF_WEBHOOK)."
  resume
  echo "Aucun webhook : notification ignoree." >> "$GITHUB_STEP_SUMMARY"
  exit 0
fi

envoyer_slack() {
  local payload
  payload="$(python3 <<'PY'
import json, os

succes = os.environ["STATUT"] == "succes"
fields = [
    {"type": "mrkdwn", "text": f"*Ref*\n`{os.environ['REF_LABEL']}`"},
    {"type": "mrkdwn", "text": f"*Evenement*\n{os.environ.get('EVENEMENT') or '(inconnu)'}"},
    {"type": "mrkdwn", "text": f"*Commit*\n`{os.environ['SHA_COURT']}`"},
    {"type": "mrkdwn", "text": f"*Acteur*\n{os.environ.get('ACTOR') or '(inconnu)'}"},
]
if os.environ.get("PR_NUMBER"):
    fields.append({"type": "mrkdwn", "text": f"*Pull request*\n#{os.environ['PR_NUMBER']}"})
if not succes and os.environ.get("ETAPE"):
    fields.append({"type": "mrkdwn", "text": f"*Etape*\n`{os.environ['ETAPE']}`"})

blocks = [
    {
        "type": "header",
        "text": {"type": "plain_text", "text": os.environ["BANNIERE"], "emoji": False},
    },
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*{os.environ['TITRE']}*"},
    },
    {"type": "divider"},
    {"type": "section", "fields": fields},
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*Sujet*\n{os.environ['SUJET']}"},
    },
    {
        "type": "actions",
        "elements": [{
            "type": "button",
            "text": {"type": "plain_text", "text": "Ouvrir le run", "emoji": False},
            "url": os.environ["RUN_URL"],
            "style": "primary" if succes else "danger",
        }],
    },
]
payload = {
    "attachments": [{
        "color": os.environ["COULEUR_SLACK"],
        "blocks": blocks,
    }],
}
print(json.dumps(payload))
PY
)"
  if curl -fsS --max-time 15 -H 'Content-Type: application/json' -d "$payload" "$SLACK_NOTIF_WEBHOOK" >/dev/null; then
    echo "Notification Slack envoyee."
  else
    echo "::warning::Echec de l'envoi Slack (curl)."
  fi
}

envoyer_teams() {
  local payload
  payload="$(python3 <<'PY'
import json, os

succes = os.environ["STATUT"] == "succes"
faits = [
    {"title": "Ref", "value": os.environ["REF_LABEL"]},
    {"title": "Evenement", "value": os.environ.get("EVENEMENT") or "(inconnu)"},
    {"title": "Commit", "value": os.environ["SHA_COURT"]},
    {"title": "Sujet", "value": os.environ["SUJET"]},
    {"title": "Acteur", "value": os.environ.get("ACTOR") or "(inconnu)"},
]
if os.environ.get("PR_NUMBER"):
    faits.append({"title": "Pull request", "value": "#" + os.environ["PR_NUMBER"]})
if not succes and os.environ.get("ETAPE"):
    faits.append({"title": "Etape", "value": os.environ["ETAPE"]})

body = [
    {
        "type": "Container",
        "style": os.environ["STYLE_TEAMS"],
        "bleed": True,
        "items": [{
            "type": "TextBlock",
            "text": os.environ["BANNIERE"],
            "weight": "Bolder",
            "size": "ExtraLarge",
            "color": os.environ["COULEUR_TEXTE"],
            "horizontalAlignment": "Center",
        }],
    },
    {
        "type": "TextBlock",
        "text": os.environ["TITRE"],
        "weight": "Bolder",
        "size": "Large",
        "color": os.environ["COULEUR_TEXTE"],
        "spacing": "Medium",
    },
    {"type": "FactSet", "facts": faits, "spacing": "Medium"},
    {
        "type": "ActionSet",
        "actions": [{
            "type": "Action.OpenUrl",
            "title": "Ouvrir le run",
            "url": os.environ["RUN_URL"],
            "style": "positive" if succes else "destructive",
        }],
    },
]
card = {
    "type": "message",
    "attachments": [{
        "contentType": "application/vnd.microsoft.card.adaptive",
        "contentUrl": None,
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": body,
            "msteams": {"width": "Full"},
        },
    }],
}
print(json.dumps(card))
PY
)"
  if curl -fsS --max-time 15 -H 'Content-Type: application/json' -d "$payload" "$TEAMS_NOTIF_WEBHOOK" >/dev/null; then
    echo "Notification Teams envoyee."
  else
    echo "::warning::Echec de l'envoi Teams (curl)."
  fi
}

export TEXTE="$texte"
export TITRE="$titre"
export BANNIERE="$banniere"
export SHA_COURT="$sha_court"
export SUJET="$sujet"
export COULEUR_SLACK="$couleur_slack"
export STYLE_TEAMS="$style_teams"
export COULEUR_TEXTE="$couleur_texte"

if est_renseignee SLACK_NOTIF_WEBHOOK; then
  envoyer_slack
fi
if est_renseignee TEAMS_NOTIF_WEBHOOK; then
  envoyer_teams
fi

resume
exit 0
