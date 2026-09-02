# 🌊 Water Potability ML Pipeline: End-to-End Classification & Preprocessing Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-EB5424.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Project_Status-Phases_1--3_Complete-brightgreen.svg)]()

> **Academic Project:** CSD 302 — Machine Learning I Capstone  
> **Track:** Problem Statement 30 — *[Capstone / Integration] Data-Cleaning, Preprocessing Pipeline, Model Comparison & Ethical Evaluation*  
> **Target Problem:** Automated Water Potability Classification from Multi-Source Environmental Sensor Telemetry

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
│ [ ] Phase 4: Model Exploration, Baseline vs. Gradient Boosted Trees & Hyperparameter Tuning
│ [ ] Phase 5: Honest Held-Out Evaluation, Cost-Sensitive Thresholding & Diagnostics     │
│ [ ] Phase 6: Ethical Audit, Feature Attribution & Viva Defense Preparation             │
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

---

## 📁 6. Repository File Structure

```
water-potability-ml-pipeline/
│
├── dataset/
│   ├── water_potability.csv           # Original Source A benchmark survey (3,276 rows)
│   ├── master_water_potability.csv    # Merged master dataset (7,776 rows)
│   └── cleaned_water_potability.csv   # Post-IQR capped & KNN-imputed dataset
│
├── files/
│   └── water_potability_capstone.ipynb# Complete, fully documented Jupyter Notebook
│
├── .gitignore                         # Excludes cache, checkpoints, and course PDFs
├── README.md                          # Comprehensive project documentation
└── requirements.txt                   # Reproducible Python dependencies
```

---

## 🚀 7. Quick Start & Setup

### Prerequisites
* Python 3.10+
* Git

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/arnav-jain700/water-potability-ml-pipeline.git
   cd water-potability-ml-pipeline
   ```

2. **Create and activate a virtual environment (optional):**
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

4. **Launch the Jupyter Notebook:**
   ```bash
   jupyter notebook files/water_potability_capstone.ipynb
   ```

---

## ⚖️ 8. Ethics, Fairness & Sociotechnical Considerations

* **Environmental Justice & Infrastructure Bias:** Aging municipal infrastructure disproportionately affects lower-income and marginalized communities (e.g., Flint, Michigan crisis). Our dataset tracks station types to audit for disparate impact across urban vs. rural catchments.
* **Sensor Quality Drift:** Industrial runoff monitoring stations often experience rapid sensor degradation, risking elevated false-negative rates if not regularly calibrated.
* **Accountability Mandate:** In public water safety, black-box predictions must be accompanied by explainable feature attributions so municipal operators can understand *why* water is flagged unsafe.

---

## 👨‍💻 Author & Acknowledgements
* **Developer:** Arnav Jain ([@arnav-jain700](https://github.com/arnav-jain700))
* **Course:** CSD 302 — Machine Learning I
* **Data Sources:** Kaggle Water Potability Benchmark & WHO/EPA Drinking Water Guidelines
