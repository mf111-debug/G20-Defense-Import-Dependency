# 🛡️ G20 Defense Import Dependency Dashboard

## Tracking Arms Import Dependency Across G20 Nations (2010–2024)

**Author:** Mohammed Farran  
**Institution:** Rice University — RCEL 506  
**Live App:** [Defense Import Dependency Dashboard](https://your-streamlit-url-here.streamlit.app)  
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

- 📊 **19 G20 countries** — full coverage with monthly data 2010–2024
- 📈 **Interactive charts** — trend lines, rolling averages, annual comparisons
- 🏆 **Country ranking table** — see which nations are most/least import dependent
- 📅 **Date range slider** — zoom into any time period
- 🗂️ **Raw data viewer** — export and inspect monthly data per country
- 🇸🇦 **Saudi Arabia focus** — Yemen conflict peak annotation and Vision 2030 marker

---

## Data Sources

| Source | Variable | Frequency | Period |
|---|---|---|---|
| [UN Comtrade](https://comtradeplus.un.org) | Arms imports (HS Chapter 93, USD) | Monthly | 2010–2024 |
| [SIPRI Military Expenditure Database](https://www.sipri.org/databases/milex) | Military spending (constant 2024 USD millions) | Annual ÷ 12 | 2010–2024 |

### Important Methodology Notes

**Mirror Data:** Most countries do not self-report arms imports to UN Comtrade. This project uses **mirror data** — exports reported by trading partner countries to the importing nation. This is the standard accepted methodology in defense trade research.

**HS Chapter 93:** Only Chapter 93 (Arms and Ammunition) is used. This is the only HS classification that is 100% military. Chapters 87 (vehicles), 88 (aircraft), and 89 (ships) contain significant civilian trade that cannot be separated from military procurement using public customs data.

**Military Expenditure:** SIPRI figures include personnel, operations, and procurement. The ratio therefore measures the share of total military budget going to imported weapons — not pure procurement dependency. This is acknowledged as a methodological limitation.

**Annual to Monthly Conversion:** SIPRI publishes annual figures. These are divided by 12 to align with monthly UN Comtrade data. Each month in a given year receives an equal share of the annual total.

---

## G20 Coverage

| Country | Code | SIPRI Row |
|---|---|---|
| 🇸🇦 Saudi Arabia | Sau | 193 |
| 🇺🇸 USA | USA | 78 |
| 🇨🇳 China | Chn | 105 |
| 🇮🇳 India | Ind | 100 |
| 🇩🇪 Germany | Ger | 167 |
| 🇬🇧 United Kingdom | UK | 180 |
| 🇫🇷 France | Fra | 166 |
| 🇯🇵 Japan | Jap | 106 |
| 🇮🇹 Italy | Ita | 171 |
| 🇨🇦 Canada | Can | 77 |
| 🇦🇺 Australia | Aus | 93 |
| 🇧🇷 Brazil | Bra | 82 |
| 🇲🇽 Mexico | Mex | 72 |
| 🇮🇩 Indonesia | Indonesia | 114 |
| 🇦🇷 Argentina | Arg | 80 |
| 🇿🇦 South Africa | Afr | 52 |
| 🇷🇺 Russia | Rus | 157 |
| 🇰🇷 South Korea | Kor | 108 |
| 🇹🇷 Türkiye | Tur | 195 |

*Note: European Union is represented by individual member states (Germany, France, Italy)*

---

## Repository Structure

```
G20-Defense-Import-Dependency/
│
├── app.py                              # Main Streamlit dashboard
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
├── SIPRI-Milex-data-1949-2025_v1_2.xlsx  # SIPRI military expenditure database
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
   - Frequency: Monthly
   - Period: 2010–2024

2. Name the file: `TradeData_XXX_YYYY-YYYY.csv` (replace XXX with your country code)

3. Find the country's row in `SIPRI-Milex-data-1949-2025_v1_2.xlsx` sheet `Constant (2024) US$`

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
