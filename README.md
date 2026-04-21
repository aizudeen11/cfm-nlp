# 🌏 SEACEN Capital Flows Monitor

An interactive web-based monitoring tool for tracking macro-financial indicators and capital flows across SEACEN economies.

This project integrates **data automation**, **cloud-based storage**, and **interactive visualization** to support economic analysis and policy insights.

---

## 🚀 Overview

The SEACEN Capital Flows Monitor is divided into two main analytical sections:

- **Section 1** → High-frequency macro-financial indicators  
- **Section 2** → External sector data (BOP & IIP)

Both sections are powered by an automated data pipeline that processes raw datasets and serves clean data for visualization.

---

## 📊 Features

### 📈 Section 1: Macroeconomic & Financial Indicators
Interactive charts covering:
- GDP Growth  
- Volatility Index (VIX) *(global benchmark)*  
- Policy Rate  
- Monthly Inflation  
- Foreign Exchange Rates  
- Credit Default Swap (CDS)  
- Liquidity Indicators  
- Financial Stress Index  
- Sovereign Bond Yields  
- Stock Price Index  
- IIF Capital Flows  

📌 *Coverage: Selected SEACEN economies (except VIX)*

---

### 🌐 Section 2: External Sector Monitoring
- Quarterly and annual:
  - Balance of Payments (BOP)  
  - International Investment Position (IIP)  

📌 *Coverage: Selected SEACEN economies only*

📌 *Data sourced from international datasets (e.g., IMF)*

---

## 🧩 Project Structure

```bash id="z4p1lu"
.
├── main.py
├── section2.py
├── to_gsheet/
│   ├── data.py
│   ├── data_section_2.py
│   ├── data_download.py
│   └── ...