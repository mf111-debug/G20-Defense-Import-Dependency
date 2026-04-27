import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import warnings
warnings.filterwarnings('ignore')
from io import StringIO

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="G20 Defense Import Dependency Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0D0D0D; color: #FFFFFF; }
.stApp { background-color: #0D0D0D; }
h1, h2, h3 { font-family: 'Rajdhani', sans-serif !important; letter-spacing: 1px; }
div[data-testid="stSidebarContent"] { background-color: #111111; }
</style>
""", unsafe_allow_html=True)

# ── G20 Country Configuration ─────────────────────────────────────────────────
# file_prefix: prefix used in your filenames (e.g. "TradeData_USA_")
# sipri_row:   0-based row index in SIPRI "Constant (2024) US$" sheet
# color:       chart color for this country
# partner_filter: set to None — each file is already filtered by partner

COUNTRY_CONFIG = {
    "Saudi Arabia":        {"file_prefix": "TradeData_Sau_",       "sipri_row": 193, "color": "#C8F542"},
    "USA":                 {"file_prefix": "TradeData_USA_",       "sipri_row": 78,  "color": "#4A9FD5"},
    "China":               {"file_prefix": "TradeData_Chn_",       "sipri_row": 105, "color": "#E05252"},
    "India":               {"file_prefix": "TradeData_Ind_",       "sipri_row": 100, "color": "#FF9933"},
    "Germany":             {"file_prefix": "TradeData_Ger_",       "sipri_row": 167, "color": "#FFCC00"},
    "United Kingdom":      {"file_prefix": "TradeData_UK_",        "sipri_row": 180, "color": "#CF142B"},
    "France":              {"file_prefix": "TradeData_Fra_",       "sipri_row": 166, "color": "#002395"},
    "Japan":               {"file_prefix": "TradeData_Jap_",       "sipri_row": 106, "color": "#BC002D"},
    "Italy":               {"file_prefix": "TradeData_Ita_",       "sipri_row": 171, "color": "#009246"},
    "Canada":              {"file_prefix": "TradeData_Can_",       "sipri_row": 77,  "color": "#FF0000"},
    "Australia":           {"file_prefix": "TradeData_Aus_",       "sipri_row": 93,  "color": "#00843D"},
    "Brazil":              {"file_prefix": "TradeData_Bra_",       "sipri_row": 82,  "color": "#009C3B"},
    "Mexico":              {"file_prefix": "TradeData_Mex_",       "sipri_row": 72,  "color": "#006847"},
    "Indonesia":           {"file_prefix": "TradeData_Indonesia_", "sipri_row": 114, "color": "#CE1126"},
    "Argentina":           {"file_prefix": "TradeData_Arg_",       "sipri_row": 80,  "color": "#74ACDF"},
    "South Africa":        {"file_prefix": "TradeData_Afr_",       "sipri_row": 52,  "color": "#007A4D"},
    "Russia":              {"file_prefix": "TradeData_Rus_",       "sipri_row": 157, "color": "#D52B1E"},
    "South Korea":         {"file_prefix": "TradeData_Kor_",       "sipri_row": 108, "color": "#003478"},
    "Türkiye":             {"file_prefix": "TradeData_Tur_",       "sipri_row": 195, "color": "#E30A17"},
}

COUNTRY_FLAGS = {
    "Saudi Arabia": "🇸🇦", "USA": "🇺🇸", "China": "🇨🇳", "India": "🇮🇳",
    "Germany": "🇩🇪", "United Kingdom": "🇬🇧", "France": "🇫🇷", "Japan": "🇯🇵",
    "Italy": "🇮🇹", "Canada": "🇨🇦", "Australia": "🇦🇺", "Brazil": "🇧🇷",
    "Mexico": "🇲🇽", "Indonesia": "🇮🇩", "Argentina": "🇦🇷", "South Africa": "🇿🇦",
    "Russia": "🇷🇺", "South Korea": "🇰🇷", "Türkiye": "🇹🇷",
}

# ── Data Loading Functions ────────────────────────────────────────────────────
@st.cache_data
def load_arms_data(country_name):
    """Load all CSV files for a country and return clean monthly DataFrame."""
    config = COUNTRY_CONFIG[country_name]
    prefix = config["file_prefix"]

    # Find all files matching this country's prefix
    files = glob.glob(f"{prefix}*.csv")

    if not files:
        return None

    all_data = []
    for fpath in sorted(files):
        try:
            with open(fpath, 'rb') as f:
                raw = f.read()
            text = raw.decode('utf-8', errors='replace')
            df = pd.read_csv(StringIO(text))
            df['value'] = pd.to_numeric(df['fobvalue'], errors='coerce')
            monthly = df.groupby('refMonth')['value'].sum().reset_index()
            monthly.columns = ['YearMonth', 'Arms_Imports_USD']
            all_data.append(monthly)
        except Exception:
            continue

    if not all_data:
        return None

    arms = pd.concat(all_data, ignore_index=True)
    # Convert YearMonth to numeric, drop any non-numeric rows
    arms['YearMonth'] = pd.to_numeric(arms['YearMonth'], errors='coerce')
    arms = arms.dropna(subset=['YearMonth'])
    arms['YearMonth'] = arms['YearMonth'].astype(int)
    # Remove duplicates (in case year ranges overlap)
    arms = arms.drop_duplicates(subset='YearMonth')
    arms = arms[arms['YearMonth'].between(201001, 202412)]
    arms['Date'] = pd.to_datetime(
        arms['YearMonth'].astype(str).str[:6],
        format='%Y%m', errors='coerce'
    )
    arms = arms.dropna(subset=['Date'])
    arms = arms[['Date', 'Arms_Imports_USD']].sort_values('Date').reset_index(drop=True)
    arms['Arms_Imports_USD_M'] = arms['Arms_Imports_USD'] / 1_000_000
    return arms


@st.cache_data
def load_sipri_data(country_name):
    """Load SIPRI military expenditure for a country and return monthly DataFrame."""
    config = COUNTRY_CONFIG[country_name]
    row_idx = config["sipri_row"]

    try:
        import openpyxl
        wb = openpyxl.load_workbook(
            'SIPRI-Milex-data-1949-2025_v1_2.xlsx',
            read_only=True, data_only=True
        )
        ws = wb['Constant (2024) US$']
        rows = list(ws.iter_rows(values_only=True))
        years_row = rows[5]
        country_row = rows[row_idx]

        milex_annual = []
        for i in range(len(years_row)):
            if isinstance(years_row[i], (int, float)) and 2010 <= years_row[i] <= 2024:
                val = country_row[i]
                if isinstance(val, (int, float)) and not pd.isna(val):
                    milex_annual.append({
                        'Year': int(years_row[i]),
                        'Annual_Milex_USD_M': float(val)
                    })

        if not milex_annual:
            return None

        milex_df = pd.DataFrame(milex_annual)
        monthly_rows = []
        for _, row in milex_df.iterrows():
            for month in range(1, 13):
                monthly_rows.append({
                    'Date': pd.Timestamp(year=int(row['Year']), month=month, day=1),
                    'Milex_Monthly_USD_M': row['Annual_Milex_USD_M'] / 12
                })
        return pd.DataFrame(monthly_rows)

    except Exception as e:
        st.error(f"SIPRI load error for {country_name}: {e}")
        return None


@st.cache_data
def build_dependency(country_name):
    """Merge arms and SIPRI data, compute Import Dependency %."""
    arms = load_arms_data(country_name)
    milex = load_sipri_data(country_name)
    if arms is None or milex is None:
        return None
    df = pd.merge(arms, milex, on='Date')
    df['Import_Dependency_Pct'] = (df['Arms_Imports_USD_M'] / df['Milex_Monthly_USD_M']) * 100
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    return df


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ G20 Defense Dashboard")
    st.markdown("---")

    st.markdown("### 🌍 Country Selection")
    selected = st.multiselect(
        "Select countries",
        options=list(COUNTRY_CONFIG.keys()),
        default=["Saudi Arabia", "USA", "China"],
        format_func=lambda x: f"{COUNTRY_FLAGS.get(x,'')} {x}"
    )

    st.markdown("### 📅 Date Range")
    start_year = st.slider("Start Year", 2010, 2023, 2010)
    end_year = st.slider("End Year", 2011, 2024, 2024)

    st.markdown("### 📊 Chart Options")
    show_rolling = st.checkbox("Show trend line", value=True,
                             help="Smooths monthly noise to show the overall direction")
    show_peak = st.checkbox("Label peak for each country", value=True,
                            help="Marks the highest point reached by each country")
    show_events = st.checkbox("Show major world events", value=True,
                              help="Marks COVID-19, Russia-Ukraine war, and Saudi Vision 2030")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#666;'>
    <b>Data Sources</b><br>
    • UN Comtrade (HS Ch. 93)<br>
    • SIPRI Milex 2025 Database<br><br>
    <b>Proxy</b><br>
    Import Dependency % =<br>
    Arms Imports / Military Spending × 100<br><br>
    <b>RCEL 506 — Rice University</b><br>
    Mohammed Farran — April 2026
    </div>
    """, unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='border-bottom:2px solid #C8F542; padding-bottom:16px; margin-bottom:24px;'>
<h1 style='margin:0; font-size:2rem; color:#FFFFFF;'>
🛡️ G20 Defense Import Dependency Dashboard
</h1>
<p style='margin:4px 0 0; color:#9E9E9E; font-size:0.9rem;'>
Chapter 93 Arms Imports as % of Military Expenditure — Monthly 2010–2024
</p>
</div>
""", unsafe_allow_html=True)

if not selected:
    st.warning("Please select at least one country from the sidebar.")
    st.stop()

# ── Load data ─────────────────────────────────────────────────────────────────
country_data = {}
failed = []
for country in selected:
    df = build_dependency(country)
    if df is not None and len(df) > 0:
        # Apply date filter
        mask = (df['Year'] >= start_year) & (df['Year'] <= end_year)
        filtered = df[mask].copy()
        if len(filtered) > 0:
            country_data[country] = filtered
        else:
            failed.append(country)
    else:
        failed.append(country)

if failed:
    st.warning(f"Could not load data for: {', '.join(failed)}. Check that CSV files are uploaded.")

if not country_data:
    st.error("No data loaded. Upload your CSV and SIPRI files to the same folder as app.py.")
    st.stop()

# ── Key Metrics Row ───────────────────────────────────────────────────────────
st.markdown("### Key Statistics")
cols = st.columns(min(len(country_data), 4))

for i, (country, df) in enumerate(country_data.items()):
    col = cols[i % 4]
    config = COUNTRY_CONFIG[country]
    current = df['Import_Dependency_Pct'].iloc[-1]
    peak = df['Import_Dependency_Pct'].max()
    peak_date = df.loc[df['Import_Dependency_Pct'].idxmax(), 'Date'].strftime('%b %Y')
    mean_val = df['Import_Dependency_Pct'].mean()
    reduction = ((peak - current) / peak * 100) if peak > 0 else 0

    with col:
        st.markdown(f"""
        <div style='background:#1C1C1C; border-left:4px solid {config["color"]};
             border-radius:6px; padding:14px; margin-bottom:8px;'>
        <div style='font-size:1rem; font-weight:700; color:{config["color"]};'>
        {COUNTRY_FLAGS.get(country,'')} {country}
        </div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:8px;'>
        <div><div style='font-size:1.4rem; font-weight:700; color:#FFFFFF;'>{current:.2f}%</div>
        <div style='font-size:0.7rem; color:#9E9E9E;'>CURRENT</div></div>
        <div><div style='font-size:1.4rem; font-weight:700; color:#E05252;'>{peak:.2f}%</div>
        <div style='font-size:0.7rem; color:#9E9E9E;'>PEAK ({peak_date})</div></div>
        <div><div style='font-size:1.4rem; font-weight:700; color:#9E9E9E;'>{mean_val:.2f}%</div>
        <div style='font-size:0.7rem; color:#9E9E9E;'>AVERAGE</div></div>
        <div><div style='font-size:1.4rem; font-weight:700; color:#C8F542;'>{reduction:.1f}%</div>
        <div style='font-size:0.7rem; color:#9E9E9E;'>FROM PEAK</div></div>
        </div></div>
        """, unsafe_allow_html=True)


# ── Main Trend Chart ──────────────────────────────────────────────────────────
st.markdown("### Import Dependency Trend")

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('#0D0D0D')
ax.set_facecolor('#141414')

for country, df in country_data.items():
    config = COUNTRY_CONFIG[country]
    color = config['color']
    flag = COUNTRY_FLAGS.get(country, '')

    # Raw line (faint)
    ax.plot(df['Date'], df['Import_Dependency_Pct'],
            color=color, linewidth=0.8, alpha=0.3)

    if show_rolling:
        rolling = df['Import_Dependency_Pct'].rolling(window=12, min_periods=6).mean()
        ax.plot(df['Date'], rolling, color=color, linewidth=2.2,
                label=f"{flag} {country}")
    else:
        ax.plot(df['Date'], df['Import_Dependency_Pct'],
                color=color, linewidth=1.8, label=f"{flag} {country}")

if show_events:
    events = [
        ('2016-04-01', 'Vision 2030', '#888888'),
        ('2020-03-01', 'COVID-19', '#AA8800'),
        ('2022-02-01', 'Russia-Ukraine War', '#CC4444'),
    ]
    ymax = max(df['Import_Dependency_Pct'].max() for df in country_data.values()) if country_data else 5
    for date_str, label, ecolor in events:
        ed = pd.Timestamp(date_str)
        ax.axvline(ed, color=ecolor, linestyle=':', linewidth=1.2, alpha=0.6)
        ax.text(ed, ymax * 0.95, label, color=ecolor, fontsize=7,
                ha='center', va='top',
                bbox=dict(facecolor='#111', alpha=0.7, edgecolor='none', pad=2))

if show_peak:
    for country, df in country_data.items():
        config = COUNTRY_CONFIG[country]
        idx = df['Import_Dependency_Pct'].idxmax()
        peak_val = df.loc[idx, 'Import_Dependency_Pct']
        peak_date = df.loc[idx, 'Date']
        flag = COUNTRY_FLAGS.get(country, '')
        ax.annotate(f'{flag} {country}\nPeak: {peak_val:.1f}%',
                    xy=(peak_date, peak_val),
                    xytext=(peak_date, peak_val * 1.08),
                    fontsize=7, color=config['color'], fontweight='bold',
                    ha='center',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#1C1C1C', alpha=0.8, edgecolor=config['color']))

ax.set_title("G20 Arms Import Dependency — Monthly Data (Chapter 93 / Military Spending)",
             fontsize=13, fontweight='bold', color='#FFFFFF', pad=10)
ax.set_xlabel("Date", fontsize=11, color='#9E9E9E')
ax.set_ylabel("Import Dependency (%)", fontsize=11, color='#9E9E9E')
ax.tick_params(colors='#9E9E9E')
for spine in ['bottom', 'left']:
    ax.spines[spine].set_color('#333333')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(fontsize=9, facecolor='#1C1C1C', edgecolor='#333333',
          labelcolor='#FFFFFF', loc='upper right', ncol=2)
ax.grid(True, color='#1F1F1F', linewidth=0.7)
plt.tight_layout()
st.pyplot(fig)
plt.close()


# ── Annual Comparison Bar Chart ───────────────────────────────────────────────
st.markdown("### Annual Average Comparison")

fig2, ax2 = plt.subplots(figsize=(14, 5))
fig2.patch.set_facecolor('#0D0D0D')
ax2.set_facecolor('#141414')

years_range = list(range(start_year, end_year + 1))
n = len(country_data)
width = 0.8 / n
offsets = np.linspace(-(n-1)/2, (n-1)/2, n) * width

for idx, (country, df) in enumerate(country_data.items()):
    config = COUNTRY_CONFIG[country]
    annual = df.groupby('Year')['Import_Dependency_Pct'].mean()
    x_pos = [y + offsets[idx] for y in years_range if y in annual.index]
    y_vals = [annual[y] for y in years_range if y in annual.index]
    ax2.bar(x_pos, y_vals, width=width*0.9, color=config['color'], alpha=0.85,
            label=f"{COUNTRY_FLAGS.get(country,'')} {country}")

ax2.set_title("Annual Average Import Dependency by Country",
              fontsize=13, fontweight='bold', color='#FFFFFF', pad=10)
ax2.set_xlabel("Year", fontsize=11, color='#9E9E9E')
ax2.set_ylabel("Import Dependency (%)", fontsize=11, color='#9E9E9E')
ax2.tick_params(colors='#9E9E9E')
ax2.set_xticks(years_range)
ax2.set_xticklabels(years_range, rotation=45)
for spine in ['bottom', 'left']:
    ax2.spines[spine].set_color('#333333')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.legend(fontsize=8, facecolor='#1C1C1C', edgecolor='#333333',
           labelcolor='#FFFFFF', ncol=3)
ax2.grid(True, axis='y', color='#1F1F1F', linewidth=0.7)
plt.tight_layout()
st.pyplot(fig2)
plt.close()


# ── G20 Ranking Table ─────────────────────────────────────────────────────────
st.markdown("### G20 Country Ranking (Latest Data)")

ranking_rows = []
for country, df in country_data.items():
    current = df['Import_Dependency_Pct'].iloc[-1]
    peak = df['Import_Dependency_Pct'].max()
    mean_val = df['Import_Dependency_Pct'].mean()
    reduction = ((peak - current) / peak * 100) if peak > 0 else 0
    ranking_rows.append({
        'Country': f"{COUNTRY_FLAGS.get(country,'')} {country}",
        'Current (%)': round(current, 2),
        'Peak (%)': round(peak, 2),
        'Average (%)': round(mean_val, 2),
        'Reduction from Peak (%)': round(reduction, 1)
    })

ranking_df = pd.DataFrame(ranking_rows).sort_values('Current (%)', ascending=False)
ranking_df = ranking_df.reset_index(drop=True)
st.dataframe(ranking_df, use_container_width=True)


# ── Raw Data Expander ─────────────────────────────────────────────────────────
with st.expander("📊 View Raw Monthly Data"):
    for country, df in country_data.items():
        st.markdown(f"**{COUNTRY_FLAGS.get(country,'')} {country}** — {len(df)} monthly observations")
        display = df[['Date','Arms_Imports_USD_M','Milex_Monthly_USD_M','Import_Dependency_Pct']].copy()
        display.columns = ['Date','Arms Imports (USD M)','Military Spending (USD M)','Import Dependency (%)']
        display['Import Dependency (%)'] = display['Import Dependency (%)'].round(3)
        display['Arms Imports (USD M)'] = display['Arms Imports (USD M)'].round(2)
        display['Military Spending (USD M)'] = display['Military Spending (USD M)'].round(2)
        st.dataframe(display, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#555; font-size:0.8rem; padding:16px 0;'>
RCEL 506 — Applied Statistics and Data Science for Engineering Leaders<br>
Rice University | Mohammed Farran | April 2026<br>
Data: UN Comtrade (HS Chapter 93) + SIPRI Military Expenditure Database 2025
</div>
""", unsafe_allow_html=True)
