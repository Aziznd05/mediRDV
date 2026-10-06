# Rapport de nettoyage MédiRDV

Date : 2026-10-06 12:07

## 1. Chargement
- Lignes initiales : **2040**

## 2. Doublons
- Lignes supprimées (id_rdv dupliqués) : **25**
- Lignes restantes : **2015**

## 3. Dates
- Dates invalides après parsing : **0**

## 4. Heures
- Heures hors plage 08:00-18:00 : **6** (conservées, à examiner)

## 5. Durées
- Durées invalides remises à NaN : **10**

## 6. Spécialités
- Spécialités après normalisation : **9** (attendu : 9)

## 7. Sexe
- Valeurs distinctes après normalisation : **['F', 'M']**

## 8. Statut
- Valeurs distinctes après normalisation : **['Absent', 'Annulé', 'Confirmé', 'Honoré', 'Planifié']**

## 9. Téléphone
- Téléphones valides avant : **1980**
- Téléphones valides après : **1956**

## 10. Confirme
- Valeurs : **{'Oui': 1041, 'Non': 974}**

## 11. Canal
- Valeurs : **{'Téléphone': 807, 'Guichet': 786, 'Recommandation médecin': 402, 'Non renseigné': 20}**

## 12. Motif d'annulation
- Annulations sans motif : **12** (à compléter)

## 13. Colonnes finales
- Dimensions finales : **(2015, 20)**

## 14. Export
- Fichier exporté : `C:\Users\LONOVO\OneDrive\Desktop\medirdv\data\propre\rendez_vous_medirdv_propre.csv`