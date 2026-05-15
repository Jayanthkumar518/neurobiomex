# =========================================================
# NeuroBiomeX — BACKEND.PY (FIXED - No hardcoded scores)
# =========================================================

import os
import json
import pickle
import subprocess
import warnings

import numpy as np
import pandas as pd

import librosa
import shap

warnings.filterwarnings("ignore")

# =========================================================
# DIRECTORIES
# =========================================================

MODEL_DIR = "models"
PROCESSED_DIR = "processed"
UPLOAD_DIR = "uploads"
DASHBOARD_DIR = "dashboard"

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DASHBOARD_DIR, exist_ok=True)

# =========================================================
# CLEAR STALE DASHBOARD JSON — call this on app startup
# =========================================================

def clear_stale_results():
    """Delete any cached dashboard JSON so the app starts fresh."""
    path = os.path.join(DASHBOARD_DIR, "dashboard_results.json")
    if os.path.exists(path):
        os.remove(path)

# =========================================================
# LOAD MODELS (lazy — only when needed)
# =========================================================

_models = {}

def _load_model(name):
    if name not in _models:
        _models[name] = pickle.load(open(f"{MODEL_DIR}/{name}", "rb"))
    return _models[name]

def get_micro_model():   return _load_model("microbiome_xgboost.pkl")
def get_micro_scaler():  return _load_model("microbiome_scaler.pkl")
def get_voice_model():   return _load_model("voice_xgboost.pkl")
def get_voice_scaler():  return _load_model("voice_scaler.pkl")

# HRV / autonomic models (optional — loaded only if files exist)
def get_hrv_model():
    p = f"{MODEL_DIR}/hrv_xgboost.pkl"
    return pickle.load(open(p, "rb")) if os.path.exists(p) else None

def get_hrv_scaler():
    p = f"{MODEL_DIR}/hrv_scaler.pkl"
    return pickle.load(open(p, "rb")) if os.path.exists(p) else None

# Metadata / inflammation / AMR models (optional)
def get_meta_model():
    p = f"{MODEL_DIR}/meta_classifier.pkl"
    return pickle.load(open(p, "rb")) if os.path.exists(p) else None

def get_meta_scaler():
    p = f"{MODEL_DIR}/metadata_scaler.pkl"
    return pickle.load(open(p, "rb")) if os.path.exists(p) else None

# =========================================================
# CLEAN TAXONOMY
# =========================================================

def clean_taxonomy_name(tax):
    try:
        split_tax = str(tax).split(";")
        species = split_tax[-1].replace("s__", "").strip()
        genus   = split_tax[-2].replace("g__", "").strip()
        if species not in ["", "__"]:
            return species
        if genus not in ["", "__"]:
            return genus
        return "Unknown"
    except:
        return "Unknown"

# =========================================================
# PROCESS MICROBIOME
# =========================================================

def process_microbiome():
    feature_table = pd.read_csv(
        f"{PROCESSED_DIR}/feature-table.csv", index_col=0
    )
    taxonomy = pd.read_csv(f"{PROCESSED_DIR}/taxonomy.csv")

    if "Taxon" in taxonomy.columns:
        taxonomy_names = taxonomy["Taxon"].apply(clean_taxonomy_name).tolist()
    else:
        taxonomy_names = [f"Feature_{i}" for i in range(len(feature_table.columns))]

    min_len = min(len(taxonomy_names), len(feature_table.columns))
    feature_table = feature_table.iloc[:, :min_len]
    taxonomy_names = taxonomy_names[:min_len]
    feature_table.columns = taxonomy_names

    return feature_table.iloc[[0]]

# =========================================================
# FEATURE ALIGNMENT
# =========================================================

def align_features(X, scaler):
    expected = scaler.feature_names_in_
    aligned = pd.DataFrame(0, index=[0], columns=expected)
    for col in X.columns:
        if col in aligned.columns:
            aligned[col] = X[col].values[0]
    return aligned

# =========================================================
# VOICE FEATURE EXTRACTION
# =========================================================

def extract_voice_features(audio_path):
    y, sr = librosa.load(audio_path, sr=None)

    jitter   = float(np.std(y))
    shimmer  = float(np.mean(np.abs(y)))
    harmonic = librosa.effects.harmonic(y)
    hnr      = float(np.mean(harmonic))

    features = np.array([jitter, shimmer, hnr]).reshape(1, -1)
    metrics = {
        "jitter_percent":  round(jitter  * 100, 2),
        "shimmer_percent": round(shimmer * 100, 2),
        "hnr_db":          round(hnr,           2),
    }
    return features, metrics

# =========================================================
# HRV / AUTONOMIC FEATURE EXTRACTION
# =========================================================

def extract_hrv_features(hrv_csv_path):
    """
    Expects a CSV with columns like: rmssd, sdnn, lf_hf_ratio, pnn50, mean_rr
    Returns (features_array, metrics_dict)
    """
    df = pd.read_csv(hrv_csv_path)
    required = ["rmssd", "sdnn", "lf_hf_ratio", "pnn50", "mean_rr"]
    row = {}
    for col in required:
        row[col] = float(df[col].iloc[0]) if col in df.columns else 0.0

    features = np.array(list(row.values())).reshape(1, -1)
    return features, row

# =========================================================
# SHAP EXPLAINABILITY
# =========================================================

def generate_shap(model, X):
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    shap_values = np.abs(shap_values).mean(axis=0)
    top_idx     = np.argsort(shap_values)[::-1][:10]
    return [
        {"feature": str(X.columns[i]), "importance": float(shap_values[i])}
        for i in top_idx
    ]

# =========================================================
# XGBoost FEATURE IMPORTANCE
# =========================================================

def xgb_feature_importance(model, X):
    importance = model.feature_importances_
    top_idx    = np.argsort(importance)[::-1][:10]
    return [
        {"feature": str(X.columns[i]), "importance": float(importance[i])}
        for i in top_idx
    ]

# =========================================================
# AI RECOMMENDATION ENGINE
# =========================================================

def generate_recommendations(
    overall_score, micro_score, voice_score,
    autonomic_score, inflammation_score, amr_score,
    top_bacteria, shap_features
):
    recs = []

    # Overall risk
    if overall_score < 40:
        recs += [
            "Overall neurodegenerative vulnerability appears low.",
            "Maintain healthy lifestyle, exercise, and dietary diversity.",
            "Routine preventive wellness monitoring recommended.",
        ]
    elif overall_score < 70:
        recs += [
            "Moderate multimodal neurological vulnerability detected.",
            "Periodic neurological evaluation is recommended.",
            "Preventive microbiome monitoring advised.",
        ]
    else:
        recs += [
            "Elevated multimodal neurodegenerative vulnerability detected.",
            "Comprehensive neurological consultation strongly advised.",
            "Advanced longitudinal monitoring recommended.",
        ]

    # Microbiome
    if micro_score > 70:
        recs += [
            "Gut dysbiosis signatures associated with gut-brain dysfunction detected.",
            "16S rRNA or shotgun metagenomic sequencing recommended.",
            "Mediterranean anti-inflammatory dietary intervention advised.",
            "Increase dietary fiber and fermented food intake.",
        ]

    # Voice
    if voice_score > 70:
        recs += [
            "Voice biomarkers suggest elevated vocal motor instability.",
            "Speech and motor-function neurological assessment recommended.",
        ]

    # Autonomic
    if autonomic_score is not None and autonomic_score > 70:
        recs += [
            "Autonomic dysfunction patterns detected via HRV analysis.",
            "Cardio-autonomic monitoring and vagal nerve assessment recommended.",
        ]
    elif autonomic_score is None:
        recs.append("Autonomic (HRV) data not provided — consider including HRV metrics.")

    # Inflammation / AMR
    if inflammation_score is not None and inflammation_score > 70:
        recs.append("Elevated inflammatory microbial patterns detected — cytokine panel advised.")
    if amr_score is not None and amr_score > 70:
        recs.append("AMR-associated microbial signatures detected — antimicrobial stewardship review advised.")

    # Bacteria interpretation
    bacteria_text = " ".join(top_bacteria).lower()
    bacteria_map = {
        "prevotella":    "Prevotella imbalance detected — microbiome diversity restoration recommended.",
        "fusobacterium": "Fusobacterium-associated inflammatory microbial activity detected.",
        "streptococcus": "Streptococcus-associated oral-gut microbial signatures observed.",
        "bacteroides":   "Bacteroides-associated metabolic dysbiosis patterns identified.",
        "akkermansia":   "Akkermansia-associated mucosal gut regulation signatures detected.",
    }
    for key, msg in bacteria_map.items():
        if key in bacteria_text:
            recs.append(msg)

    # SHAP
    top_shap = [x["feature"].lower() for x in shap_features[:5]]
    if any("clostridium" in f for f in top_shap):
        recs.append("Clostridium-associated microbial imbalance detected.")

    # High-risk follow-up
    if overall_score > 65:
        recs += [
            "Longitudinal follow-up every 3–6 months recommended.",
            "Inflammatory biomarker testing (CRP, IL-6, TNF-alpha) suggested.",
            "Multi-omics validation (metagenomics + transcriptomics) recommended.",
        ]

    return list(dict.fromkeys(recs))  # deduplicate, preserve order

# =========================================================
# MAIN PIPELINE
# =========================================================

def run_complete_pipeline(
    table_qza_path=None,
    taxonomy_qza_path=None,
    voice_path=None,
    hrv_csv_path=None,
    metadata_csv_path=None,
):
    # ------------------------------------------------------------------
    # RESET — start with None so nothing is shown unless actually computed
    # ------------------------------------------------------------------
    micro_score        = None
    voice_score        = None
    autonomic_score    = None
    inflammation_score = None
    amr_score          = None

    microbiome_shap  = []
    xgb_importance   = []
    top_bacteria     = []
    voice_metrics    = {}

    pipeline_status = {
        "voice_extraction":         False,
        "microbiome_parsing":       False,
        "hrv_analysis":             False,
        "metadata_analysis":        False,
        "explainability_generated": False,
        "recommendation_engine":    False,
        "multimodal_fusion":        False,
    }

    # ------------------------------------------------------------------
    # QZA → CSV CONVERSION
    # ------------------------------------------------------------------
    if table_qza_path and taxonomy_qza_path:
        subprocess.run(["python", "qza.py"], check=False)

    # ------------------------------------------------------------------
    # MICROBIOME
    # ------------------------------------------------------------------
    if os.path.exists(f"{PROCESSED_DIR}/feature-table.csv"):
        try:
            X_micro         = process_microbiome()
            X_micro_aligned = align_features(X_micro, get_micro_scaler())
            X_micro_scaled  = get_micro_scaler().transform(X_micro_aligned)

            micro_prob  = get_micro_model().predict_proba(X_micro_scaled)[0][1]
            micro_score = float(micro_prob * 100)

            X_scaled_df    = pd.DataFrame(X_micro_scaled, columns=X_micro_aligned.columns)
            microbiome_shap = generate_shap(get_micro_model(), X_scaled_df)
            xgb_importance  = xgb_feature_importance(get_micro_model(), X_scaled_df)
            top_bacteria    = list(X_micro.columns[:10])

            pipeline_status["microbiome_parsing"]       = True
            pipeline_status["explainability_generated"] = True
        except Exception as e:
            print(f"[Microbiome] Error: {e}")

    # ------------------------------------------------------------------
    # VOICE
    # ------------------------------------------------------------------
    if voice_path and os.path.exists(voice_path):
        try:
            voice_features, voice_metrics = extract_voice_features(voice_path)
            voice_scaled = get_voice_scaler().transform(voice_features)
            voice_prob   = get_voice_model().predict_proba(voice_scaled)[0][1]
            voice_score  = float(voice_prob * 100)
            pipeline_status["voice_extraction"] = True
        except Exception as e:
            print(f"[Voice] Error: {e}")

    # ------------------------------------------------------------------
    # HRV / AUTONOMIC (optional)
    # ------------------------------------------------------------------
    if hrv_csv_path and os.path.exists(hrv_csv_path):
        try:
            hrv_model  = get_hrv_model()
            hrv_scaler = get_hrv_scaler()
            if hrv_model and hrv_scaler:
                hrv_feats, _ = extract_hrv_features(hrv_csv_path)
                hrv_scaled   = hrv_scaler.transform(hrv_feats)
                hrv_prob     = hrv_model.predict_proba(hrv_scaled)[0][1]
                autonomic_score = float(hrv_prob * 100)
                pipeline_status["hrv_analysis"] = True
        except Exception as e:
            print(f"[HRV] Error: {e}")

    # ------------------------------------------------------------------
    # METADATA → INFLAMMATION + AMR (optional)
    # ------------------------------------------------------------------
    if metadata_csv_path and os.path.exists(metadata_csv_path):
        try:
            meta_model  = get_meta_model()
            meta_scaler = get_meta_scaler()
            if meta_model and meta_scaler:
                meta_df     = pd.read_csv(metadata_csv_path)
                meta_scaled = meta_scaler.transform(meta_df.iloc[[0]])
                probs = meta_model.predict_proba(meta_scaled)[0]
                inflammation_score = float(probs[0] * 100) if len(probs) > 0 else None
                amr_score          = float(probs[1] * 100) if len(probs) > 1 else None
                pipeline_status["metadata_analysis"] = True
        except Exception as e:
            print(f"[Metadata] Error: {e}")

    # ------------------------------------------------------------------
    # GUARD — need at least one real score
    # ------------------------------------------------------------------
    available_scores = [s for s in [micro_score, voice_score, autonomic_score] if s is not None]
    if not available_scores:
        return None  # Nothing to compute — caller must show "upload data" message

    # ------------------------------------------------------------------
    # MULTIMODAL FUSION (weighted, using only available modalities)
    # ------------------------------------------------------------------
    weights = {
        "micro":        (micro_score,        0.40),
        "voice":        (voice_score,         0.25),
        "autonomic":    (autonomic_score,     0.20),
        "inflammation": (inflammation_score,  0.10),
        "amr":          (amr_score,           0.05),
    }

    total_weight = 0.0
    weighted_sum = 0.0
    for key, (score, w) in weights.items():
        if score is not None:
            weighted_sum += score * w
            total_weight += w

    # Re-normalise so missing modalities don't artificially deflate the score
    overall_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0
    pipeline_status["multimodal_fusion"] = True

    # ------------------------------------------------------------------
    # RISK LEVEL
    # ------------------------------------------------------------------
    if overall_score < 40:
        risk_level = "Low Risk"
    elif overall_score < 70:
        risk_level = "Moderate Risk"
    else:
        risk_level = "High Risk"

    # ------------------------------------------------------------------
    # AI RECOMMENDATIONS
    # ------------------------------------------------------------------
    recommendations = generate_recommendations(
        overall_score, micro_score or 0, voice_score or 0,
        autonomic_score, inflammation_score, amr_score,
        top_bacteria, microbiome_shap,
    )
    pipeline_status["recommendation_engine"] = True

    # ------------------------------------------------------------------
    # CONFIDENCE — average of all available scores
    # ------------------------------------------------------------------
    confidence = round(
        sum(s for s in [micro_score, voice_score, autonomic_score] if s is not None)
        / len([s for s in [micro_score, voice_score, autonomic_score] if s is not None]),
        2
    )

    # ------------------------------------------------------------------
    # BUILD RESULT
    # ------------------------------------------------------------------
    dashboard_results = {
        "overall_score":              round(overall_score, 2),
        "risk_level":                 risk_level,
        "confidence":                 confidence,
        "microbiome_score":           round(micro_score, 2)        if micro_score        is not None else None,
        "voice_score":                round(voice_score, 2)        if voice_score        is not None else None,
        "autonomic_score":            round(autonomic_score, 2)    if autonomic_score    is not None else None,
        "inflammation_score":         round(inflammation_score, 2) if inflammation_score is not None else None,
        "amr_score":                  round(amr_score, 2)          if amr_score          is not None else None,
        "top_bacteria":               top_bacteria,
        "voice_metrics":              voice_metrics,
        "microbiome_shap":            microbiome_shap,
        "xgboost_feature_importance": xgb_importance,
        "recommendations":            recommendations,
        "pipeline_status":            pipeline_status,
    }

    # ------------------------------------------------------------------
    # SAVE
    # ------------------------------------------------------------------
    with open(f"{DASHBOARD_DIR}/dashboard_results.json", "w") as f:
        json.dump(dashboard_results, f, indent=4)

    return dashboard_results


# =========================================================
# CLI TEST
# =========================================================

if __name__ == "__main__":
    clear_stale_results()
    results = run_complete_pipeline(
        table_qza_path="uploads/table.qza",
        taxonomy_qza_path="uploads/taxonomy.qza",
        voice_path="uploads/voice.wav",
    )
    if results:
        print(json.dumps(results, indent=4))
    else:
        print("No data uploaded. Please provide at least one modality.")