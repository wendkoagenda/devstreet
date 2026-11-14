"""Profil typé : un membre peut avoir un profil dev et un profil entreprise.

- ajoute `type` (dev par défaut) et remplace le OneToOne `user` par une clé étrangère ;
- les profils existants deviennent des profils `dev` ; ceux qui avaient une entreprise donnent aussi
  un profil `entreprise` (même entreprise, même propriétaire) et reprennent leurs offres ;
- pose ensuite les contraintes : un profil de chaque type au plus, entreprise obligatoire pour le type `entreprise`
  et interdite pour le type `dev`.

Le retour arrière fusionne chaque profil entreprise dans le profil dev du même membre (ou le convertit
en profil dev s'il n'en a pas), puis rétablit le OneToOne.
"""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

SUFFIXE = '-entreprise'


def _slug_libre(Profil, base):
    racine = f'{base[:160 - len(SUFFIXE) - 6]}{SUFFIXE}'
    slug, index = racine, 2
    while Profil.objects.filter(slug=slug).exists():
        slug = f'{racine}-{index}'
        index += 1
    return slug


def separer_profils(apps, schema_editor):
    """Chaque profil rattaché à une entreprise donne un profil `entreprise` distinct."""
    Profil = apps.get_model('marketplace', 'Profil')
    Offer = apps.get_model('marketplace', 'Offer')

    champs = [f for f in Profil._meta.concrete_fields if f.name not in ('id', 'type', 'slug', 'company', 'is_company_owner')]

    for dev in Profil.objects.filter(company__isnull=False):
        copie = {f.attname: getattr(dev, f.attname) for f in champs}
        entreprise = Profil.objects.create(
            type='entreprise',
            slug=_slug_libre(Profil, dev.slug),
            company_id=dev.company_id,
            is_company_owner=dev.is_company_owner,
            **copie,
        )
        # Les offres publiées par ce recruteur suivent son profil entreprise
        Offer.objects.filter(recruiter_id=dev.id).update(recruiter_id=entreprise.id)
        dev.company = None
        dev.is_company_owner = False
        dev.save(update_fields=['company', 'is_company_owner'])


def fusionner_profils(apps, schema_editor):
    """Retour arrière : le profil dev reprend l'entreprise ; un profil entreprise seul devient un profil dev."""
    Profil = apps.get_model('marketplace', 'Profil')
    Offer = apps.get_model('marketplace', 'Offer')

    for entreprise in Profil.objects.filter(type='entreprise'):
        dev = Profil.objects.filter(user_id=entreprise.user_id, type='dev').first()
        if dev is None:
            entreprise.type = 'dev'
            entreprise.save(update_fields=['type'])
            continue
        dev.company_id = entreprise.company_id
        dev.is_company_owner = entreprise.is_company_owner
        dev.save(update_fields=['company', 'is_company_owner'])
        Offer.objects.filter(recruiter_id=entreprise.id).update(recruiter_id=dev.id)
        entreprise.delete()


def resoudre_contraintes_differees(apps, schema_editor):
    """
    PostgreSQL refuse un ALTER TABLE tant que des vérifications de clés étrangères différées sont en attente
    (« il reste des événements sur les triggers ») : après la migration de données, on les résout tout de suite.
    """
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('SET CONSTRAINTS ALL IMMEDIATE')


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_sync_marketplace_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='profil',
            name='type',
            field=models.CharField(
                choices=[('dev', 'Dev'), ('entreprise', 'Entreprise')],
                default='dev',
                help_text="Profil de développeur ou profil d'entreprise",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='profil',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='marketplace_profils',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Avant la migration de données : au retour arrière, résout les écritures de `fusionner_profils`
        # avant l'ALTER TABLE qui rétablit le OneToOne.
        migrations.RunPython(resoudre_contraintes_differees, resoudre_contraintes_differees),
        migrations.RunPython(separer_profils, fusionner_profils),
        # Après la migration de données : résout les écritures de `separer_profils` avant les contraintes.
        migrations.RunPython(resoudre_contraintes_differees, resoudre_contraintes_differees),
        migrations.AddConstraint(
            model_name='profil',
            constraint=models.UniqueConstraint(fields=('user', 'type'), name='uniq_profil_user_type'),
        ),
        migrations.AddConstraint(
            model_name='profil',
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(('type', 'entreprise'), ('company__isnull', False))
                    | models.Q(('type', 'dev'), ('company__isnull', True))
                ),
                name='profil_type_company_coherent',
            ),
        ),
    ]
