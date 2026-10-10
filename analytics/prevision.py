"""
EF-24 : Prévision du volume hebdomadaire de RDV par spécialité sur 4 semaines.
Compare baseline naïve et Holt-Winters (saisonnalité trimestrielle),
évalue MAE/MAPE, sauvegarde les prévisions.
"""
import sys
from pathlib import Path
RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

import pandas as pd
import numpy as np
import json
import warnings
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error

warnings.filterwarnings("ignore")

# --- Chargement ---
df = pd.read_csv(RACINE / "data" / "propre" / "rendez_vous_medirdv_propre.csv", encoding="utf-8")
df["date_rdv"] = pd.to_datetime(df["date_rdv"], errors="coerce")
df["semaine"] = df["date_rdv"].dt.to_period("W").apply(lambda p: p.start_time)

serie = df.groupby(["semaine", "specialite"]).size().unstack(fill_value=0)
toutes_semaines = pd.date_range(serie.index.min(), serie.index.max(), freq="W-MON")
serie = serie.reindex(toutes_semaines, fill_value=0)

print(f"Série : {len(serie)} semaines × {serie.shape[1]} spécialités")

NB_TEST = 8
train, test = serie.iloc[:-NB_TEST], serie.iloc[-NB_TEST:]


def entrainer_hw(y_train, periode=13):
    """Essaie Holt-Winters avec saisonnalité, sinon trend damped pur."""
    # Essai 1 : saisonnalité trimestrielle
    try:
        model = ExponentialSmoothing(
            y_train, trend="add", seasonal="add",
            seasonal_periods=periode, initialization_method="estimated",
        )
        return model.fit(optimized=True), "HW-saisonnier"
    except Exception:
        pass
    # Essai 2 : trend damped sans saisonnalité
    try:
        model = ExponentialSmoothing(
            y_train, trend="add", damped_trend=True,
            initialization_method="estimated",
        )
        return model.fit(optimized=True), "HW-trend"
    except Exception as e:
        return None, f"échec : {e}"


# --- Évaluation ---
resultats = []
for spe in serie.columns:
    y_train, y_test = train[spe], test[spe]

    # Baseline naïve : moyenne 4 dernières semaines
    pred_naive = pd.Series([y_train.iloc[-4:].mean()] * NB_TEST, index=test.index)
    mae_n = mean_absolute_error(y_test, pred_naive)
    mape_n = np.mean(np.abs((y_test - pred_naive) / y_test.replace(0, 1))) * 100

    # Holt-Winters
    fit, methode = entrainer_hw(y_train)
    if fit is not None:
        pred_hw = fit.forecast(NB_TEST)
        mae_hw = mean_absolute_error(y_test, pred_hw)
        mape_hw = np.mean(np.abs((y_test - pred_hw) / y_test.replace(0, 1))) * 100
    else:
        mae_hw, mape_hw = np.nan, np.nan

    resultats.append({
        "specialite": spe,
        "mae_naive": round(mae_n, 2),
        "mape_naive": round(mape_n, 2),
        "mae_hw": round(mae_hw, 2) if not np.isnan(mae_hw) else None,
        "mape_hw": round(mape_hw, 2) if not np.isnan(mape_hw) else None,
        "modele": methode,
    })

df_resultats = pd.DataFrame(resultats).sort_values("mape_hw")
print("\n=== Comparaison modèles (MAPE %) ===")
print(df_resultats.to_string(index=False))

# --- Prévision finale sur 4 semaines (toute la série) ---
NB_FUTUR = 4
previsions = {}
for spe in serie.columns:
    y = serie[spe]
    fit, methode = entrainer_hw(y)
    if fit is None:
        previsions[spe] = {"erreur": methode}
        continue

    pred = fit.forecast(NB_FUTUR)
    residus = y - fit.fittedvalues
    sigma = residus.std()
    dates_futures = pd.date_range(
        serie.index.max() + pd.Timedelta(weeks=1), periods=NB_FUTUR, freq="W-MON"
    )
    previsions[spe] = {
        "modele": methode,
        "points": [
            {
                "semaine": str(d.date()),
                "prevision": int(round(max(0, p))),
                "borne_basse": int(round(max(0, p - 1.96 * sigma))),
                "borne_haute": int(round(max(0, p + 1.96 * sigma))),
            }
            for d, p in zip(dates_futures, pred.values)
        ],
    }

# --- Sauvegarde ---
sortie = RACINE / "data" / "propre" / "previsions.json"
with open(sortie, "w", encoding="utf-8") as f:
    json.dump({"resultats_modeles": resultats, "previsions_4_semaines": previsions},
              f, ensure_ascii=False, indent=2)

print(f"\n✅ Prévisions sauvegardées dans {sortie}")
print("\nAperçu Médecine générale :")
print(json.dumps(previsions.get("Médecine générale", {}), indent=2, ensure_ascii=False))