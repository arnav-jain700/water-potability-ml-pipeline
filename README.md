# 🌊 Water Potability ML Pipeline: End-to-End Classification & Preprocessing Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-EB5424.svg)](https://xgboost.readthedocs.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg?logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75.svg?logo=Plotly&logoColor=white)](https://plotly.com/)
[![CI/CD Pipeline](https://github.com/arnav-jain700/water-potability-ml-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/arnav-jain700/water-potability-ml-pipeline/actions)
[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aquaguard-water-potability.streamlit.app/)
[![Status](https://img.shields.io/badge/Project_Status-Phases_1--6_Complete-brightgreen.svg)]()

> **Academic Project:** CSD 302 — Machine Learning I Capstone Project  
> **Course Track:** Problem Statement 30 — *[Capstone / Integration] Data-Cleaning, Preprocessing Pipeline, Model Comparison & Ethical Evaluation*  
> **Domain:** Environmental Engineering, Public Health & Sensor Telemetry  
> **Author:** Arnav Jain ([@arnav-jain700](https://github.com/arnav-jain700))  
> 🌐 **Live Web Application:** [aquaguard-water-potability.streamlit.app](https://aquaguard-water-potability.streamlit.app/)

---

## 📌 1. Project Overview & Motivation

Access to safe, non-toxic drinking water is a fundamental human right and a pillar of global public health (**UN Sustainable Development Goal 6**). Traditional laboratory water testing (microbial cultures and mass spectrometry) is precise but suffers from high operational latency, significant equipment costs, and limited throughput across distributed municipal catchments.

### 🎯 Machine Learning Objective
To architect a **leak-free, production-grade data cleaning, outlier mitigation, and preprocessing pipeline** for multi-source water telemetry, followed by training and evaluating cost-sensitive classifiers to predict water safety:

$$\hat{y} \in \{0, 1\}$$

* **Class `0` (Non-Potable / Unsafe):** Exceeds chemical or physical contaminant thresholds; unsafe for human consumption.
* **Class `1` (Potable / Safe):** Conforms to EPA and WHO drinking water quality benchmarks.

---

## ⚠️ 2. Asymmetric Cost Matrix & Evaluation Philosophy

In clinical and public health triage, classification errors carry vastly unequal real-world consequences:

| Error Type | Prediction vs. Reality | Real-World Impact | Priority Metric |
| :--- | :--- | :--- | :--- |
| 🔴 **False Negative (Type II)** | Predicts **Potable** when water is **Toxic** | **Catastrophic Public Health Risk**: Contaminated water enters consumer distribution, causing disease outbreaks or poisoning. | **Recall (Sensitivity)** on Toxic Class / PR-AUC |
| 🟡 **False Positive (Type I)** | Predicts **Toxic** when water is **Potable** | **Operational Inconvenience**: Triggers redundant secondary laboratory re-testing; zero threat to human life. | Secondary Precision check |

> **Evaluation Mandate:** Simple classification accuracy is inadequate and misleading due to class asymmetry. Models are evaluated using **Recall**, **Macro F1-Score**, and **Precision-Recall AUC (PR-AUC)**.

---

## 🗂️ 3. Multi-Source Dataset Architecture

To simulate realistic municipal surveillance, the system combines **7,776 observations** across two complementary data streams:

```
┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
│   Source 1: Global Survey (3,276 rows) │       │ Source 2: Regional Sensors (4,500 rows)│
│   • 9 Chemical Features                │       │ • 9 Chemical Features                  │
│   • Historical Water Bodies            │       │ • EPA/WHO Standard Field Telemetry     │
└───────────────────┬────────────────────┘       └───────────────────┬────────────────────┘
                    │                                                │
                    ▼                                                ▼
              Add Metadata                                     Add Metadata
         [`Data_Source`, `Station_Type`]                  [`Data_Source`, `Station_Type`]
                    │                                                │
                    └───────────────────────┬────────────────────────┘
                                            │
                                  [ pd.concat() ]
                                            │
                                            ▼
                    ┌─────────────────────────────────────────────────┐
                    │      MASTER DATASET: 7,776 Rows, 12 Columns     │
                    │   • 9 Continuous Biochemical Parameters         │
                    │   • 2 Categorical Metadata Columns              │
                    │   • 1 Binary Target (`Potability`: 0 vs 1)      │
                    └─────────────────────────────────────────────────┘
```

1. **Source A (Global Water Survey — 3,276 records):** Historical lake, reservoir, and river samples.
2. **Source B (Regional Sensor Telemetry — 4,500 records):** Field sensor telemetry from automated environmental monitoring stations (*Urban Treatment, Agricultural Runoff, Industrial Catchments*) calibrated against WHO/EPA drinking water distributions with realistic sensor dropouts and noise.

---

## 🔬 4. Feature Dictionary & Physicochemical Standards

| Feature Name | Type | Physical / Chemical Meaning | Safe Range (WHO/EPA) |
| :--- | :--- | :--- | :--- |
| **`ph`** | Float | Acid-base equilibrium ($0-14$ scale). | $6.5 - 8.5$ |
| **`Hardness`** | Float | Capacity to precipitate soap; concentration of $\text{Ca}^{2+}$ and $\text{Mg}^{2+}$ ($\text{mg/L}$). | $150 - 300\text{ mg/L}$ |
| **`Solids`** | Float | Total Dissolved Solids ($\text{TDS}$) in parts per million ($\text{ppm}$). | $< 1000\text{ ppm}$ |
| **`Chloramines`** | Float | Concentration of chloramine disinfectants ($\text{ppm}$). | $\le 4.0\text{ ppm}$ |
| **`Sulfate`** | Float | Dissolved sulfate minerals ($\text{mg/L}$). | $\le 250\text{ mg/L}$ |
| **`Conductivity`** | Float | Electrical conductivity reflecting dissolved ionic charge ($\mu\text{S/cm}$). | $\le 400\text{ }\mu\text{S/cm}$ |
| **`Organic_carbon`** | Float | Total Organic Carbon ($\text{TOC}$) indicating decaying organic matter ($\text{ppm}$). | $\le 2.0 - 4.0\text{ ppm}$ |
| **`Trihalomethanes`** | Float | Carcinogenic disinfection byproducts ($\text{THMs}$) in $\mu\text{g/L}$. | $\le 80\text{ }\mu\text{g/L}$ |
| **`Turbidity`** | Float | Measure of water clarity and suspended particulates ($\text{NTU}$). | $\le 5.0\text{ NTU}$ |
| **`Data_Source`** | Categorical | Origin stream (`Global_Survey_A` vs. `Regional_Network_B`). | Metadata tracking |
| **`Station_Type`** | Categorical | Catchment zone (*Urban, Agricultural, Industrial, Lake, Reservoir, River*). | Environmental context |
| **`Potability`** | Binary (Target) | `0` = Non-Potable / Unsafe, `1` = Potable / Safe. | Ground Truth |

---

## 🛠️ 5. Implementation Roadmap & Technical Details

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               PIPELINE WORKFLOW STATUS                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [x] Phase 1: Problem Framing, Multi-Source Integration & Architecture                  │
│ [x] Phase 2: Exploratory Data Analysis, Tukey's IQR Outlier Capping & KNN Imputation   │
│ [x] Phase 3: Preprocessing Pipeline (StandardScaler, One-Hot Encoding, Stratified Split)│
│ [x] Phase 4: Model Exploration, Baseline vs. Tree Ensembles & Hyperparameter Tuning    │
│ [x] Phase 5: Honest Held-Out Evaluation & Asymmetric Cost-Sensitive Threshold Tuning   │
│ [x] Phase 6: Global Feature Attribution, Grounded Ethics Audit & Viva Preparation      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 📍 Phase 1: Multi-Source Data Ingestion & Harmonization
* Unified dual data sources into a structured 7,776-sample warehouse.
* Injected provenance metadata (`Data_Source`, `Station_Type`) for cross-source drift testing and downstream algorithmic fairness audits.
* Diagnosed baseline target distribution: **$68.4\%$ Unsafe : $31.6\%$ Safe**.

### 🔬 Phase 2: Exploratory Data Analysis, Outliers & Imputation
* **Duplicate Detection:** Audited dataset; confirmed $0$ duplicate records.
* **Skewness Diagnostic:** Detected severe right-skew in `Solids` ($+1.390$).
* **Outlier Capping via Tukey's IQR Fences:**
  * Lower Fence: $Q_1 - 1.5 \times \text{IQR}$ (with physical non-negativity constraint $x \ge 0.0$).
  * Upper Fence: $Q_3 + 1.5 \times \text{IQR}$.
  * Applied **Winsorization / Capping** using `.clip()` to prevent extreme leverage while retaining $100\%$ sample volume.
  * Corrected negative sensor artifact in `Organic_carbon` ($-0.46 \rightarrow 0.0$).
* **Strategic Imputation (KNN vs. Median):**
  * Evaluated Median Imputation vs. 5-Nearest Neighbors (`KNNImputer`).
  * Validated distributions via **Kernel Density Estimation (KDE)** plots; demonstrated that KNN faithfully preserved the natural multivariate probability density curves without artificial variance spikes.

### ⚙️ Phase 3: Preprocessing Pipeline Architecture
* **Stratified Splitting (`stratify=y`):** Partitioned into an $80\%$ Training Set ($6,220$ rows) and a $20\%$ Held-Out Test Set ($1,556$ rows) to lock class prior balance.
* **Leakage Defense:** Enforced strict separation; preprocessors are fitted exclusively on $X_{train}$ and applied to $X_{test}$.
* **Composite `ColumnTransformer`:**
  * Continuous features ($9$): Rescaled to $\mu = 0, \sigma = 1$ via `StandardScaler`.
  * Categorical metadata ($2$): Encoded via `OneHotEncoder(drop='first', handle_unknown='ignore')` to eliminate multicollinearity.
  * Expanded transformed feature space to **15 orthogonal predictors**.

### 🤖 Phase 4: Model Building & Hyperparameter Tuning
* **Stratified 5-Fold Cross-Validation Benchmark:**
  * **Logistic Regression:** ROC-AUC: `0.618`, Macro F1: `0.562` (Struggled with non-linear intervals).
  * **XGBoost Classifier:** ROC-AUC: `0.745`, Macro F1: `0.675`.
  * **Random Forest (Champion):** ROC-AUC: **`0.772`**, Macro F1: **`0.696`**.
* **Hyperparameter Optimization via `RandomizedSearchCV` (125 fits):**
  * Sampled 25 configurations over trees, depths, leaf limits, and class weights.
  * **Winning Configuration:** `n_estimators=400`, `max_depth=None`, `min_samples_leaf=4`, `class_weight='balanced_subsample'`.
  * **Tuned CV Score:** **`0.7789` ROC-AUC** ($\sigma = 0.0139$).

### 🎯 Phase 5: Honest Held-Out Test Evaluation & Cost Diagnostics
* Evaluated on strictly untouched $X_{test}$ ($1,556$ samples):
  * **Tuned Random Forest:** Maintained generalization with **`0.779` ROC-AUC** and strong PR-AUC.
  * Zero sign of overfitting (test metrics mirrored 5-fold CV scores).
* **Asymmetric Cost-Sensitive Threshold Optimization:**
  * Evaluated societal cost: $\text{Cost} = 10 \times FN_{\text{toxic}} + 1 \times FP_{\text{toxic}}$.
  * Scanned decision thresholds $\tau \in [0.10, 0.90]$.
  * **Optimal Operating Point:** $\tau^* \approx 0.65$ (demanding $65\%$ confidence before declaring water potable).
  * **Result:** Eliminated $>60\%$ of dangerous false-potable poisonings while reducing total societal risk score.

### ⚖️ Phase 6: Explainability, Ethics & Capstone Deliverables
* **Global Feature Attribution (Gini Importance):** Verified that biochemical parameters (`ph`, `Sulfate`, `Solids`, `Chloramines`) drive the vast majority of decision splits ($>90\%$), proving the model acts on physical chemistry rather than metadata proxies.
* **Grounded Ethics Audit:** Analyzed environmental justice, geographic sampling disparity (Flint, Michigan parallels), and sensor fouling across industrial catchments.

---

## 📊 6. Key Results Comparison Matrix

| Model | CV ROC-AUC (Mean ± Std) | CV Macro F1 | Test ROC-AUC | Test PR-AUC | Primary Strength / Limitation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Logistic Regression** | $0.618 \pm 0.012$ | $0.562 \pm 0.011$ | $0.618$ | $0.412$ | Fast baseline; fails on non-linear chemical ranges. |
| **XGBoost Classifier** | $0.745 \pm 0.014$ | $0.675 \pm 0.013$ | $0.748$ | $0.554$ | Strong gradient boosting; slightly sensitive to sensor noise. |
| **Baseline Random Forest** | $0.772 \pm 0.011$ | $0.696 \pm 0.012$ | $0.773$ | $0.598$ | Robust bagging ensemble; captures threshold splits. |
| **Tuned Random Forest 🏆** | **$0.779 \pm 0.014$** | **$0.702 \pm 0.011$** | **$0.779$** | **$0.612$** | **Champion: 400 trees, regularized leaves, balanced weights.** |

---

## 📁 7. Repository File Structure

```
water-potability-ml-pipeline/
│
├── .github/workflows/
│   └── ci.yml                         # Automated GitHub Actions CI/CD test workflow
│
├── .streamlit/
│   └── config.toml                    # High-contrast UI theme & server configuration
│
├── dataset/
│   ├── water_potability.csv           # Original Source A benchmark survey (3,276 rows)
│   ├── master_water_potability.csv    # Merged master dataset (7,776 rows × 12 cols)
│   └── cleaned_water_potability.csv   # Post-IQR capped & KNN-imputed dataset
│
├── models/
│   └── water_potability_pipeline.joblib# Serialized atomic production pipeline
│
├── tests/
│   └── test_pipeline.py               # Automated pytest suite (bounds, data, threshold)
│
├── files/
│   └── water_potability_capstone.ipynb# Fully documented, interactive Jupyter Notebook
│
├── app.py                             # Interactive Streamlit Web Application
├── .gitignore                         # Excludes course PDF, checkpoints, and cache
├── README.md                          # Comprehensive project documentation & report
└── requirements.txt                   # Reproducible Python dependencies
```

---

## 🚀 8. Quick Start & Setup

### Prerequisites
* Python 3.10+
* Git

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/arnav-jain700/water-potability-ml-pipeline.git
   cd water-potability-ml-pipeline
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Interactive Streamlit Web Dashboard:**
   ```bash
   streamlit run app.py
   ```

5. **Run Automated Unit Tests (pytest):**
   ```bash
   pytest -v tests/
   ```

6. **Launch the Jupyter Notebook:**
   ```bash
   jupyter notebook files/water_potability_capstone.ipynb
   ```

---

## 🌐 9. Interactive Web Application & Visual Analytics (Streamlit + Plotly)

> 🚀 **Live Production Deployment**: [aquaguard-water-potability.streamlit.app](https://aquaguard-water-potability.streamlit.app/)

The project includes an interactive web dashboard (`app.py`) built with **Streamlit** and **Plotly** for real-time municipal triage:

* **🧭 Plotly Potability Confidence Gauge (Speedometer)**: Curved semi-circular dial displaying potability confidence with delta indicators, color-coded hazard zones ($0-50\%$ Red, $50-65\%$ Amber, $65-100\%$ Emerald), and a dynamic threshold needle.
* **🕸️ Chemical Fingerprint Radar / Spider Chart**: Multidimensional radar plot comparing all 9 chemical features against the **green WHO Safe Benchmark Envelope**; parameter breaches visibly pierce outside the safe boundary into the red alert zone.
* **📋 Physicochemical Regulatory Audit**: Live tabular breakdown auditing each parameter against WHO/EPA guidelines (`min`, `max`, `unit`, and compliance verdict).
* **📁 Batch Telemetry Ingestion & Scoring**: Drag-and-drop CSV upload for multi-sample scoring with cohort donut charts, 2D scatter plots (pH vs. Sulfate), and one-click scored CSV export.
* **🎨 High-Contrast Theming (`.streamlit/config.toml`)**: Clean-tech theme with deep slate text (`#0F172A`) and explicit background contrast to ensure readability across all browsers.

---

## ⚖️ 10. Ethics, Fairness & Sociotechnical Considerations

* **Environmental Justice & Infrastructure Bias:** Aging municipal infrastructure disproportionately affects lower-income and marginalized communities (e.g., Flint, Michigan crisis). Our dataset tracks station types to audit for disparate impact across urban vs. rural catchments.
* **Sensor Quality Drift:** Industrial runoff monitoring stations often experience rapid sensor degradation, risking elevated false-negative rates if not regularly calibrated.
* **Accountability Mandate:** In public water safety, black-box predictions must be accompanied by explainable feature attributions so municipal operators can understand *why* water is flagged unsafe.

---

## 🎓 11. Viva Defense Master Q&A (Top 5 Questions & Answers)

1. **Q: Why did you use Tukey's IQR method instead of standard Z-scores for outlier detection?**  
   *A:* Z-score outlier detection assumes a symmetric, Gaussian distribution ($\mu \pm 3\sigma$). In our dataset, `Solids` exhibited heavy positive skewness ($+1.390$), which distorts the sample mean and standard deviation. Tukey's IQR fences rely on rank-ordered percentiles ($Q_1, Q_3$) which are inherently robust to extreme values.

2. **Q: Why did you cap (Winsorize) outliers instead of dropping them?**  
   *A:* Dropping outlier rows across 9 physical parameters would discard $\approx 18\%$ of the dataset. Winsorization using `.clip()` reins in extreme leverage while retaining 100% of our sample size.

3. **Q: Why did KNN Imputation beat Median Imputation in your distribution audit?**  
   *A:* Median imputation replaces missing entries with a single constant value, creating an artificial, unnatural spike at the center of the distribution. KNN Imputation ($k=5$) leverages multi-dimensional Euclidean distance from complete chemical parameters, preserving multivariate correlations and natural probability curves.

4. **Q: Why did Random Forest outperform Logistic Regression so significantly?**  
   *A:* Water potability is governed by bounded physical intervals (e.g., pH must be within $6.5 - 8.5$). A linear model tries to separate classes with a single linear hyperplane, which cannot isolate bounded intervals without manual polynomial features. Decision trees naturally carve orthogonal safe windows using sequential splits.

5. **Q: Why did you shift the classification threshold from 0.50 to 0.65?**  
   *A:* Classification errors carry asymmetric consequences. A False Negative (declaring contaminated water safe) causes disease outbreaks, while a False Positive merely prompts a lab retest. By setting $\tau^* \approx 0.65$, we demand higher confidence before declaring water potable, eliminating over $60\%$ of dangerous false-potable events.

---

## 👨‍💻 Author & Acknowledgements
* **Developer:** Arnav Jain ([@arnav-jain700](https://github.com/arnav-jain700))
* **Course:** CSD 302 — Machine Learning I
* **Academic Institution:** Lovely Professional University (LPU)
* **Data Sources:** Kaggle Water Potability Benchmark & WHO/EPA Drinking Water Guidelines
