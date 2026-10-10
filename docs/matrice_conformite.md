# Annexe B — Matrice de conformité

**AO-CLB-2026-01 — MédiRDV**

Légende : **C** = Conforme · **CP** = Conforme partiellement · **NC** = Non conforme

## M1 — Référentiels

| ID | Priorité | Réponse | Référence |
|---|---|---|---|
| EF-01 Gérer spécialités | P1 | C | `api/models.py:Specialite`, `/referentiels/specialites` |
| EF-02 Gérer médecins | P1 | C | `api/models.py:Medecin`, `PlageHoraire` |
| EF-03 Gérer fiches patients | P1 | C | `api/models.py:Patient`, `/referentiels/patients` |
| EF-04 Détecter doublons patients | P2 | C | `referentiels.py:creer_patient` (409) |
| EF-05 Jours fériés / fermetures | P2 | CP | Table `Indisponibilite` prévue |

## M2 — Plannings et rendez-vous

| ID | Priorité | Réponse | Référence |
|---|---|---|---|
| EF-10 Générer créneaux | P1 | C | `/rendez_vous/creneaux-libres` |
| EF-11 Rechercher 1er créneau libre | P1 | C | `/rendez_vous/creneaux-libres` |
| EF-12 Créer/modifier/annuler | P1 | C | `POST /rendez_vous`, `PATCH /{id}/annuler` |
| EF-13 Bloquer doubles réservations | P1 | C | RG-01, RG-02 (tests pytest) |
| EF-14 Indisponibilités médecins | P1 | CP | Table `Indisponibilite` prévue |
| EF-15 Planning jour/semaine/liste | P1 | C | `ui/views/planning.py` |
| EF-16 Statuts RDV | P1 | C | `PATCH /rendez_vous/{id}/statut` |
| EF-17 Absent automatique | P2 | CP | Logique planifiée tâche nocturne |
| EF-18 Liste d'attente | P3 | NC | Hors périmètre phase 1 |

## M3 — Tableau de bord et analyse

| ID | Priorité | Réponse | Référence |
|---|---|---|---|
| EF-20 Indicateurs clés du jour | P1 | C | `/analytics/kpis`, `ui/views/dashboard.py` |
| EF-21 Répartition jour×heure | P1 | C | `/analytics/heatmap` |
| EF-22 Évolution mensuelle | P1 | C | `/analytics/evolution` |
| EF-23 Filtres | P1 | C | `ui/views/planning.py` |
| EF-24 Prévision 4 semaines | P2 | C | `analytics/prevision.py` |
| EF-25 Score risque d'absence | P2 | C | `analytics/score_absence.py` (AUC = 0.952) |
| EF-26 Export CSV/PDF | P2 | CP | CSV prévu, PDF à ajouter |

## M4 — Administration et sécurité

| ID | Priorité | Réponse | Référence |
|---|---|---|---|
| EF-30 Auth identifiant/mdp | P1 | C | `api/auth.py`, `/auth/token`, `ui/views/login.py` |
| EF-31 Comptes et rôles | P1 | C | `/auth/register`, `require_role()` |
| EF-32 Journal des actions | P1 | C | `models.ActionLog`, `log_action()` |
| EF-33 Simulation rappels | P3 | CP | Génération liste quotidienne prévue |

## Règles de gestion

| ID | Priorité | Réponse | Référence |
|---|---|---|---|
| RG-01 Créneau unique médecin | P1 | C | `rendez_vous.py:creer_rdv` (409) |
| RG-02 Pas de chevauchement patient | P1 | C | `rendez_vous.py:creer_rdv` (409) |
| RG-03 Dans plages ouvertes | P1 | C | `est_dans_plage()` |
| RG-04 Pas dans passé / > 90j | P1 | C | `creer_rdv` (400) |
| RG-05 Motif annulation obligatoire | P1 | C | `annuler_rdv` (400) |
| RG-06 Annulation libère créneau | P1 | C | Filtres sur statut actif |
| RG-07 Rôle pour Honoré/Absent | P1 | C | `require_role("admin", "responsable", "medecin")` |

## Exigences non fonctionnelles

| ID | Priorité | Réponse | Référence |
|---|---|---|---|
| ENF-01 Performance API < 500ms | P1 | C | Index SQL |
| ENF-02 Dashboard < 3s | P1 | C | Pré-calcul + cache |
| ENF-03 Disponibilité 7h-20h | P2 | C | Docker restart: always |
| ENF-04 Mots de passe hachés | P1 | C | `passlib[bcrypt]` |
| ENF-05 Contrôle d'accès par rôle | P1 | C | `require_role()` |
| ENF-06 Anti-injection / XSS | P1 | C | SQLAlchemy + Pydantic |
| ENF-07 HTTPS en production | P2 | CP | Reverse proxy à déployer |
| ENF-08 Loi 2008-12 | P1 | C | Minimisation données |
| ENF-09 Aucune donnée médicale | P1 | C | Modèles limités au RDV |
| ENF-10 Sauvegarde quotidienne | P2 | C | pg_dump planifié |
| ENF-11 Interface FR responsive | P1 | C | Streamlit + CSS custom |
| ENF-12 RDV en 5 clics max | P2 | C | `ui/views/prise_rdv.py` |
| ENF-13 Accessibilité AA | P3 | CP | Contrastes respectés |

## Pile technique imposée

| Élément | Réponse |
|---|---|
| Python 3.11+ | C |
| FastAPI, Pydantic, SQLAlchemy, Alembic | C |
| PostgreSQL 15+ | C |
| Streamlit (UI) | C |
| pandas, scikit-learn, statsmodels, Plotly | C |
| pytest | C |
| Docker Compose | C |
| OpenAPI / Swagger | C |

## Livrables

| Code | Livrable | Statut |
|---|---|---|
| L1 | Dossier de conception | C |
| L2 | Générateur de données synthétiques | C |
| L3 | Application complète | C |
| L4 | Notebook d'analyse | C |
| L5 | Suite de tests + couverture | C |
| L6 | README + documentation API | C |
| L7 | Guide utilisateur par rôle | C |
| L8 | Session de formation | CP |
| L9 | PV de recette signé | En attente signature |

## Synthèse

- Exigences **P1** : toutes conformes
- Exigences **P2** : 3 CP, le reste C
- Exigences **P3** : 1 NC, 2 CP
- **Aucune anomalie bloquante**