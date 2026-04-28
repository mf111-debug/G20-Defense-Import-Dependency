# 🛡️ G20 Defense Import Dependency Dashboard

## Tracking Arms Import Dependency Across G20 Nations (2010–2024)

**Author:** Mohammed Farran  
**Institution:** Rice University — RCEL 506  
**Live App:** [Defense Import Dependency Dashboard](https://g20-defense-import-dependency-nerr78rngknr6pvh9wjg2x.streamlit.app)  
**Date:** April 2026

---

## What This Project Does

This dashboard measures and visualizes how dependent each G20 country is on importing foreign weapons — defined as **arms import dependency**: the percentage of a country's military budget spent on importing Chapter 93 arms and ammunition from abroad.

**Simple formula:**
```
Import Dependency % = (Arms Imports USD / Military Spending USD) × 100
```

When this number goes **down**, a country is buying fewer weapons from abroad — meaning it is producing more locally. When it goes **up**, foreign dependency is increasing.

---

## Why This Matters

Defense localization is a major policy priority for many countries:

- **Saudi Arabia** targets 50% local defense production by 2030 (Vision 2030)
- **South Korea** transformed from a major importer to a top global arms exporter
- **Türkiye** significantly reduced foreign dependency since the 2000s
- **India** launched "Make in India" defense initiative
- **Brazil, Indonesia, Argentina** are building domestic defense industries

This dashboard gives researchers, policymakers, and defense analysts a free, data-driven tool to track these trends across all G20 nations in one place.

---

## Key Features

- 📊 **19 G20 countries** — full coverage with annual data 2010–2024
- 📈 **Interactive charts** — annual trends, country comparisons, world events timeline
- 🏆 **Country ranking table** — see which nations are most/least import dependent
- 📅 **Date range slider** — zoom into any time period
- 🗂️ **Raw data viewer** — export and inspect annual data per country
- 🌍 18 major world events — from Arab Spring to NATO expansion, shown on the timeline

---

## Data Sources

| Source | Variable | Frequency | Period |
|---|---|---|---|
| [UN Comtrade](https://comtradeplus.un.org) | Arms imports (HS Chapter 93, USD) | **Annual** | 2010–2024 |
| [SIPRI Military Expenditure Database](https://www.sipri.org/databases/milex) | Military spending (constant 2024 USD millions) | **Annual** | 2010–2024 |

### Important Methodology Notes

**Mirror Data:** Most countries do not self-report arms imports to UN Comtrade. This project uses **mirror data** — exports reported by trading partner countries to the importing nation. This is the standard accepted methodology in defense trade research.

**HS Chapter 93:** Only Chapter 93 (Arms and Ammunition) is used. This is the only HS classification that is 100% military. Chapters 87 (vehicles), 88 (aircraft), and 89 (ships) contain significant civilian trade that cannot be separated from military procurement using public customs data.

**Military Expenditure:** SIPRI figures include personnel, operations, and procurement. The ratio therefore measures the share of total military budget going to imported weapons — not pure procurement dependency. This is acknowledged as a methodological limitation.

**Annual Data:** Both UN Comtrade and SIPRI publish annual figures. The dependency ratio is calculated directly year-by-year — no conversion needed. Each data point on the chart represents one full calendar year.

---

## G20 Coverage

| Country | File Prefix | Region |
|---|---|---|
| 🇸🇦 Saudi Arabia | TradeData_Sau_ | Middle East |
| 🇺🇸 USA | TradeData_USA_ | Americas |
| 🇨🇳 China | TradeData_Chn_ | Asia |
| 🇮🇳 India | TradeData_Ind_ | Asia |
| 🇩🇪 Germany | TradeData_Ger_ | Europe |
| 🇬🇧 United Kingdom | TradeData_UK_ | Europe |
| 🇫🇷 France | TradeData_Fra_ | Europe |
| 🇯🇵 Japan | TradeData_Jap_ | Asia |
| 🇮🇹 Italy | TradeData_Ita_ | Europe |
| 🇨🇦 Canada | TradeData_Can_ | Americas |
| 🇦🇺 Australia | TradeData_Aus_ | Asia-Pacific |
| 🇧🇷 Brazil | TradeData_Bra_ | Americas |
| 🇲🇽 Mexico | TradeData_Mex_ | Americas |
| 🇮🇩 Indonesia | TradeData_Indonesia_ | Asia |
| 🇦🇷 Argentina | TradeData_Arg_ | Americas |
| 🇿🇦 South Africa | TradeData_Afr_ | Africa |
| 🇷🇺 Russia | TradeData_Rus_ | Europe |
| 🇰🇷 South Korea | TradeData_Kor_ | Asia |
| 🇹🇷 Türkiye | TradeData_Tur_ | Middle East |

*Note: European Union is represented by individual member states (Germany, France, Italy)*

---

## Repository Structure

```
G20-Defense-Import-Dependency/
│
├── app.py                              # Main Streamlit dashboard
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
├── G20_Military_Expenditure_1949_2025.csv  # SIPRI military expenditure database
│
├── TradeData_Sau_2010-2020.csv         # Saudi Arabia arms imports
├── TradeData_Sau_2021-2024.csv
├── TradeData_USA_2010-2015.csv         # USA arms imports
├── TradeData_USA_2016-2020.csv
├── TradeData_USA_2021-2024.csv
├── TradeData_Chn_2010-2020.csv         # China
├── TradeData_Chn_2021-2024.csv
├── TradeData_Ind_2010-2020.csv         # India
├── TradeData_Ind_2021-2024.csv
├── TradeData_Ger_2010-2015.csv         # Germany
├── TradeData_Ger_2016-2020.csv
├── TradeData_Ger_2021-2024.csv
├── TradeData_UK_2010-2015.csv          # United Kingdom
├── TradeData_UK_2016-2020.csv
├── TradeData_UK_2021-2024.csv
├── TradeData_Fra_2010-2015.csv         # France
├── TradeData_Fra_2016-2020.csv
├── TradeData_Fra_2021-2024.csv
├── TradeData_Jap_2010-2020.csv         # Japan
├── TradeData_Jap_2021-2024.csv
├── TradeData_Ita_2010-2020.csv         # Italy
├── TradeData_Ita_2021-2024.csv
├── TradeData_Can_2010-2020.csv         # Canada
├── TradeData_Can_2021-2024.csv
├── TradeData_Aus_2010-2020.csv         # Australia
├── TradeData_Aus_2021-2024.csv
├── TradeData_Bra_2010-2020.csv         # Brazil
├── TradeData_Bra_2021-2024.csv
├── TradeData_Mex_2010-2020.csv         # Mexico
├── TradeData_Mex_2021-2024.csv
├── TradeData_Indonesia_2010-2020.csv   # Indonesia
├── TradeData_Indonesia_2021-2024.csv
├── TradeData_Arg_2010-2020.csv         # Argentina
├── TradeData_Arg_2021-2024.csv
├── TradeData_Afr_2010-2015.csv         # South Africa
├── TradeData_Afr_2016-2020.csv
├── TradeData_Afr_2021-2024.csv
├── TradeData_Rus_2010-2020.csv         # Russia
├── TradeData_Rus_2021-2024.csv
├── TradeData_Kor_2010-2020.csv         # South Korea
├── TradeData_Kor_2021-2024.csv
├── TradeData_Tur_2010-2020.csv         # Türkiye
└── TradeData_Tur_2021-2024.csv
```

---

## How to Run Locally

**Step 1 — Clone the repository:**
```bash
git clone https://github.com/mf111-debug/G20-Defense-Import-Dependency.git
cd G20-Defense-Import-Dependency
```

**Step 2 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 3 — Run the app:**
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## How to Add New Countries

To add a country not currently in the dashboard:

1. Download monthly Chapter 93 export data from [UN Comtrade](https://comtradeplus.un.org):
   - Reporters: All
   - Trade Flow: Exports
   - Partner: [your country]
   - Commodity: 93
   - Frequency: **Annual**
   - Period: 2010–2024

2. Name the file: `TradeData_XXX_YYYY-YYYY.csv` (replace XXX with your country code)

3. Find the country name exactly as written in \ `G20_Military_Expenditure_1949_2025.csv` sheet `Constant (2024) US$`

4. Add to `COUNTRY_CONFIG` in `app.py`:
```python
"Country Name": {
    "file_prefix": "TradeData_XXX_",
    "sipri_row": ROW_NUMBER,
    "color": "#HEXCOLOR",
}
```

---

## Limitations

- Chapter 93 covers only arms and ammunition — excludes aircraft, ships, and military vehicles
- Military expenditure includes salaries and operations, not just procurement
- Mirror data may undercount imports from countries with poor reporting practices
- Russia data post-2022 may be incomplete due to sanctions-related reporting gaps
- Results represent directional trends, not absolute localization percentages

---

## Academic Context

This dashboard was originally developed as part of a final project for **RCEL 506: Applied Statistics and Data Science for Engineering Leaders** at Rice University (April 2026), focusing on Saudi Arabia's defense localization trajectory toward its Vision 2030 target of 50% local production.

The project was later expanded to cover all G20 nations to provide comparative context and broader research utility.

---

## License

Data is sourced from publicly available databases (UN Comtrade, SIPRI). Code is open source — feel free to use, modify, and build on this for your own research.

---

## Contact

**Mohammed Farran**  
Rice University — RCEL 506  
April 2026
