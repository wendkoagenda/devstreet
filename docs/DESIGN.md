# Design System — DevStreet

## Product Context
- **Quoi** : Hub builders — forum, communautés, messages, projets Hub, marketplace
- **Pour qui** : développeurs et contributeurs qui passent longtemps dans l’app
- **Espace** : plateforme collab / community tooling
- **Type** : web app / dashboard
- **Memorable thing** : violet soft, calme et lisible — pas d’orange Kinetic, pas le violet Graphite saturé

## Aesthetic Direction
- **Direction** : Industrial / utilitarian adouci
- **Décoration** : minimal
- **Mood** : densément utile, chaleur discrète via un violet désaturé ; surfaces claires pour les sessions longues
- **Références** : charte interne Soft Violet (remplace Kinetic Engine orange + ancien `#220147`)

## Typography
- **Display/Hero** : Poppins — déjà hébergée, cohérente avec le repo
- **Body** : Poppins
- **Data/Tables** : JetBrains Mono (tabular-nums)
- **Code** : JetBrains Mono
- **Loading** : `@fontsource/poppins` + mono système / JetBrains si présent
- **Scale** : 12 / 14 / 16 / 18 / 24 / 32 / 40 px

## Color
- **Approche** : restrained — un accent violet soft + neutres ; le slate porte la structure
- **Primary (structure)** : `#26242E` (`250 12% 16%`) — nav, boutons structurels
- **Brand / accent (soft violet)** : `#765F95` (`265 22% 48%`) — focus, liens brand, chips, CTA colorés
- **Brand strong** : `#5D487A` (`265 26% 38%`) — hover brand
- **Brand soft** : `#F4F2F8` / border `#DAD5E2` — fonds teintés
- **Neutrals** : canvas `#F2F2F0` → cartes `#FFFFFF` → texte `#26242E`
- **Semantic** : success `160 50% 32%`, warning `36 80% 42%`, error `0 65% 48%`, info `210 55% 42%`
- **Dark mode** : lavande soft `265 38% 72%` sur anthracite teinté violet ; chroma abaissée

## Spacing
- **Base** : 8px
- **Densité** : confortable-dense
- **Scale** : 2xs(2) xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48) 3xl(64)

## Layout
- **Approche** : grid-disciplined
- **Grid** : 12 / 8 / 4 colonnes (desktop / tablet / mobile)
- **Max content width** : 1440px
- **Border radius** : sm:4px, md:8px, lg:12px, full:9999px

## Motion
- **Approche** : minimal-fonctionnel
- **Easing** : enter(ease-out) exit(ease-in) move(ease-in-out)
- **Duration** : micro(50-100ms) court(150-250ms) moyen(250-400ms)

## Charte PDF
Document livrable (même format que App Photo) :
`docs/charte-graphique/DevStreet-Charte-graphique.pdf`
(source HTML : `docs/charte-graphique/devstreet-charte-graphique.html`).

## Decisions Log
| Date | Décision | Rationale |
|------|----------|-----------|
| 2026-03-13 | Soft Violet remplace Kinetic orange + `#220147` | User : Kinetic pas pour nous ; violet à adoucir |
| 2026-03-13 | Primary = slate, brand = violet soft | Un seul accent coloré ; structure neutre |
| 2026-03-13 | Fil « stream soft » | Header sans ALL CAPS, onglets pastilles, cartes à rail type, méta mono |
| 2026-11-14 | Charte PDF Soft Violet (7 pages) | Alignée sur le modèle App Photo |
