
---

## Document 3 — Guide utilisateur

Crée `docs/guide_utilisateur.md` :

```markdown
# Guide utilisateur MédiRDV

## Connexion

1. Ouvrir http://localhost:8501
2. Saisir nom d'utilisateur et mot de passe
3. Cliquer sur **Se connecter**

**Compte de démo** : `admin` / `AdminBaobabs2026!`

## Rôles et accès

- **Agent d'accueil** : prise de RDV, gestion patients
- **Médecin** : consultation planning, marquage Honoré/Absent
- **Responsable des opérations** : suivi complet + analytics
- **Direction** : tableau de bord synthétique
- **Administrateur** : tous droits + gestion utilisateurs

## Tableau de bord

Affiche :
- **KPI du jour** : RDV prévus, honorés, absents, taux d'absence 30j
- **Heatmap** : répartition par jour et heure
- **Top spécialités** : volume par spécialité
- **Évolution mensuelle** : volume + absences

## Planning

1. Choisir une **date de début**
2. Filtrer par **période** (Jour / Semaine / Mois)
3. Filtrer par **statut** si besoin
4. Consulter le tableau des RDV avec badges de statut

## Prise de rendez-vous

1. **Recherche** : ID médecin + date de début + nb jours
2. Cliquer sur **Chercher les créneaux libres**
3. **Sélectionner** un créneau
4. Remplir : ID patient, ID spécialité, canal, agent
5. Cliquer sur **Créer le rendez-vous**

⚠️ Erreurs possibles :
- `RG-01` : le créneau est déjà pris
- `RG-02` : le patient a déjà un RDV qui chevauche
- `RG-04` : date dans le passé ou > 90 jours

## Patients

- **Liste** : onglet *Liste*, recherche par nom/prénom/téléphone
- **Création** : onglet *Nouveau*, formulaire
- Détection automatique des doublons (EF-04)

## Déconnexion

Bouton ** Se déconnecter** en bas de la sidebar.

## Support

Direction des opérations — Clinique Les Baobabs