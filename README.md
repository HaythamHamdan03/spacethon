# SatGuard AI — Autonomous Satellite Fault Detection

**Team Invisible Hand · SPACETHON 2026 · 1st Place**  
King Fahd University of Petroleum & Minerals · April 28–29, 2026

> *"The invisible hand watching your satellite — so your engineers don't have to."*

🔴 **Live Dashboard:** [satguard-ai.onrender.com](https://satguard-ai.onrender.com)

---

## Overview

SatGuard AI is an autonomous satellite fault detection system that uses deep learning to monitor satellite telemetry data in real time, identify anomalous behavior, and generate structured fault alerts — without any human intervention.

Built in **48 hours** during SPACETHON 2026, the system was validated on real NASA spacecraft telemetry data from the SMAP satellite, achieving **92.9% precision** and **84.2% recall**.

| Metric | Value |
|---|---|
| Precision | 92.9% |
| Recall | 84.2% |
| False Alarms | 1% (79 / 8,179 points) |
| True Positives | 1,033 anomaly minutes caught |
| Award | 🥇 1st Place — 6,500 SAR |

---

## The Problem

Satellites are humanity's most critical infrastructure. They orbit at hundreds of kilometers — unreachable by any maintenance crew. When something goes wrong, engineers have minutes to detect and respond before a fault cascades into mission failure.

Current monitoring systems fall short because:
- **Fixed threshold alerts** miss gradual degradation
- **Rule-based FDIR systems** only catch anticipated anomalies
- **Single-channel monitoring** misses multi-sensor correlated faults
- **Human monitoring** is expensive, fatiguing, and error-prone

The core issue: satellite telemetry is a time-series. Whether a reading is anomalous depends entirely on what came before it. Simple threshold systems have no memory.

---

## The Solution

SatGuard AI replaces fixed-threshold monitoring with a deep learning model that:
1. Learns what **normal** satellite behavior looks like from historical telemetry
2. Raises an alarm whenever the current signal deviates from learned normality
3. Does this **without any labeled fault data** (unsupervised learning)

---

## Dataset — NASA SMAP

| Property | Detail |
|---|---|
| Source | NASA Jet Propulsion Laboratory — Kaggle |
| Spacecraft | SMAP (Soil Moisture Active Passive) — launched Jan 31, 2015 |
| Orbit | 685 km sun-synchronous polar orbit |
| Features | 25 sensor channels per timestep |
| Timestep | 1 minute per data point |
| Anomaly labels | Manually annotated by NASA engineers |

**Why channel P-2:**
- Normal behavior: completely flat at -1.0 for 5,320 minutes
- Anomaly: sudden violent oscillation between -1.0 and +1.0
- Onset: minute 5,320 (~3.7 days into test period)
- Duration: 1,225 minutes (~20.4 hours)
- Physical interpretation: power relay flickering

---

## AI Model Architecture

The final model is an **LSTM Autoencoder** — specifically designed for unsupervised anomaly detection in time-series data.

```
Input (50 timesteps × 25 features)
    ↓
LSTM Encoder (64 units, tanh)       — compresses to 64-dim vector
    ↓
RepeatVector (50)                   — prepares for sequential decoding
    ↓
LSTM Decoder (64 units, tanh)       — reconstructs time sequence
    ↓
TimeDistributed Dense (25 outputs)  — reconstructed 25-feature window
```

| Parameter | Value |
|---|---|
| Optimizer | Adam |
| Loss | Mean Squared Error |
| Epochs | 50 |
| Batch size | 32 |
| Training time | ~3 min on Google Colab T4 GPU |
| Model size | 712 KB (.keras) |
| Total parameters | ~16,569 |

### Anomaly Detection Logic

**Reconstruction Error:** For each 50-minute window, the model reconstructs it. High reconstruction error = anomaly signal.

**Self-Calibrating Threshold (3σ):**
```
threshold = mean(train_errors) + 3 × std(train_errors)
```
Computed threshold for P-2: **0.4887**

**10-Minute Consecutive Filter:** Only flags an anomaly if the error exceeds threshold for 10+ consecutive minutes — eliminates transient noise spikes.

---

## Data Preprocessing

1. **Outlier Removal (3σ clipping):** 420 outlier points removed from P-2 test signal
2. **Normalization:** StandardScaler fit on training data only (no data leakage)
3. **Sliding Window:** 50-minute windows, stride 1

| Split | Windows |
|---|---|
| Training | 2,830 windows (2,880 minutes) |
| Test | 8,257 windows (8,179 minutes) |

---

## The Model Journey — 5 Iterations

| # | Model | Channel | Precision | Key Learning |
|---|---|---|---|---|
| 1 | Isolation Forest (1 feature) | S-1 | 4.2% | Ignores time — flags everything |
| 2 | Isolation Forest (25 features) | D-2 | 45.6% | Better, but D-2 was a binary on/off signal |
| 3 | Dense Autoencoder | E-3 | 15.1% | No time awareness — anomaly smoother than normal |
| 4 | LSTM Autoencoder | P-2 | 78.6% | Breakthrough — temporal memory works |
| ✅ 5 | **LSTM + Consecutive Filter + 3σ Clipping** | **P-2** | **92.9%** | **Final model** |

---

## Results

| Metric | Value | Meaning |
|---|---|---|
| Precision 92.9% | 93 / 100 alarms were real | When we raise an alarm, we are right |
| Recall 84.2% | 1,033 / 1,225 minutes caught | Detected 84% of the full 20-hour fault event |
| False positive rate 1% | 79 / 8,179 total points | Extremely low false alarm rate |
| True positives 1,033 | Correctly flagged anomaly minutes | Tracked fault from onset through recovery |

---

## Dashboard

A full-stack interactive web dashboard visualizes the model's results in real time.

### Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| Charts | Chart.js |
| Backend | Flask (Python) |
| Data | results_v2.json — pre-computed model outputs |
| Deployment | Render.com — satguard-ai.onrender.com |

### Pages

**Dashboard:** Live metrics, telemetry signal chart, AI reconstruction error chart, spacecraft status panel, simulation controls, autonomous alert log, fault alert popup

**How It Works:** 6 explanation cards + full 10-step pipeline visualization — designed for non-technical audiences

**Results:** 4 metric cards, model journey table showing all 5 iterations from 4.2% to 92.9%

---

## Local Development

```bash
git clone https://github.com/HaythamHamdan03/spacethon.git
cd spacethon
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`

---

## Project Structure

```
spacethon/
├── app.py                  # Flask app — serves dashboard and /api/data
├── results_v2.json         # Pre-computed model outputs (signal, errors, flags)
├── satellite_lstm_model.keras  # Trained LSTM Autoencoder weights
├── requirements.txt        # Flask, gunicorn, requests
├── render.yaml             # Render deployment config (web + keepalive cron)
├── keepalive.py            # Pings /health every 14 min to prevent cold start
└── templates/
    └── index.html          # Full dashboard UI
```

---

## System Architecture

```
NASA SMAP Dataset
    → 3σ Outlier Removal (420 points removed)
    → StandardScaler Normalization
    → Sliding Window (50-min, stride 1)
    → LSTM Autoencoder Training (50 epochs)
    → Reconstruction Error per Window
    → 3σ Threshold (0.4887)
    → 10-Min Consecutive Filter
    → results_v2.json
    → Flask /api/data
    → Interactive Dashboard
```

---

## Competition

| | |
|---|---|
| Event | SPACETHON 2026 — AI & Space Hackathon |
| Organizers | Aerospace Engineering Club, KFUPM Student Affairs, Saudi Space Community |
| Duration | 48 hours (April 28–29, 2026) |
| Venue | KFUPM Building 63 Main Hall, Dhahran, Saudi Arabia |
| Prize pool | 12,000 SAR |
| Result | **1st Place — 6,500 SAR** |

---

## Team — Invisible Hand

| Member | Role |
|---|---|
| Haytham Hamdan | AI model development, data pipeline, dashboard, deployment |
| Saleh Khaled | Ideation, research, presentation design |
| Alwalid Alfaleet | Research, presentation design, pitch |

> *"We came in not fully knowing the idea. We fought to get real NASA data. We built a real neural network from scratch and took it from 4.2% to 92.9% precision through five iterations in one night. That is what this was."* — Haytham Hamdan

---

## References

- Hundman et al. (2018). *Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding.* KDD 2018. NASA JPL.
- Fleith, P. (2023). *NASA Anomaly Detection Dataset — SMAP & MSL.* Kaggle.
- Kotowski et al. (2024). *ESA Benchmark for Anomaly Detection in Satellite Telemetry.* arXiv:2406.17826.
