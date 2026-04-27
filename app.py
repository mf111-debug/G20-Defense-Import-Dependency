import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import glob
import warnings
warnings.filterwarnings('ignore')
from io import StringIO

st.set_page_config(
    page_title="G20 Defense Import Dependency",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Inter:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0D0D0D; color: #FFFFFF; }
.stApp { background-color: #0D0D0D; }
h1,h2,h3 { font-family: 'Rajdhani', sans-serif !important; }
div[data-testid="stSidebarContent"] { background-color: #0F0F0F; }
</style>
""", unsafe_allow_html=True)

# ── Country Config ────────────────────────────────────────────────────────────
COUNTRIES = {
    "Saudi Arabia":   {"prefix": "TradeData_Sau_",       "sipri_name": "Saudi Arabia",              "color": "#C8F542", "flag": "🇸🇦", "region": "Middle East"},
    "USA":            {"prefix": "TradeData_USA_",       "sipri_name": "United States of America",  "color": "#4A9FD5", "flag": "🇺🇸", "region": "Americas"},
    "China":          {"prefix": "TradeData_Chn_",       "sipri_name": "China",                     "color": "#E05252", "flag": "🇨🇳", "region": "Asia"},
    "India":          {"prefix": "TradeData_Ind_",       "sipri_name": "India",                     "color": "#FF9933", "flag": "🇮🇳", "region": "Asia"},
    "Germany":        {"prefix": "TradeData_Ger_",       "sipri_name": "Germany",                   "color": "#FFCC00", "flag": "🇩🇪", "region": "Europe"},
    "United Kingdom": {"prefix": "TradeData_UK_",        "sipri_name": "United Kingdom",            "color": "#CF142B", "flag": "🇬🇧", "region": "Europe"},
    "France":         {"prefix": "TradeData_Fra_",       "sipri_name": "France",                    "color": "#4169E1", "flag": "🇫🇷", "region": "Europe"},
    "Japan":          {"prefix": "TradeData_Jap_",       "sipri_name": "Japan",                     "color": "#FF6B6B", "flag": "🇯🇵", "region": "Asia"},
    "Italy":          {"prefix": "TradeData_Ita_",       "sipri_name": "Italy",                     "color": "#009246", "flag": "🇮🇹", "region": "Europe"},
    "Canada":         {"prefix": "TradeData_Can_",       "sipri_name": "Canada",                    "color": "#FF4444", "flag": "🇨🇦", "region": "Americas"},
    "Australia":      {"prefix": "TradeData_Aus_",       "sipri_name": "Australia",                 "color": "#00C49F", "flag": "🇦🇺", "region": "Asia-Pacific"},
    "Brazil":         {"prefix": "TradeData_Bra_",       "sipri_name": "Brazil",                    "color": "#009C3B", "flag": "🇧🇷", "region": "Americas"},
    "Mexico":         {"prefix": "TradeData_Mex_",       "sipri_name": "Mexico",                    "color": "#006847", "flag": "🇲🇽", "region": "Americas"},
    "Indonesia":      {"prefix": "TradeData_Indonesia_", "sipri_name": "Indonesia",                 "color": "#CE1126", "flag": "🇮🇩", "region": "Asia"},
    "Argentina":      {"prefix": "TradeData_Arg_",       "sipri_name": "Argentina",                 "color": "#74ACDF", "flag": "🇦🇷", "region": "Americas"},
    "South Africa":   {"prefix": "TradeData_Afr_",       "sipri_name": "South Africa",              "color": "#007A4D", "flag": "🇿🇦", "region": "Africa"},
    "Russia":         {"prefix": "TradeData_Rus_",       "sipri_name": "Russia",                    "color": "#D52B1E", "flag": "🇷🇺", "region": "Europe"},
    "South Korea":    {"prefix": "TradeData_Kor_",       "sipri_name": "Korea, South",              "color": "#003478", "flag": "🇰🇷", "region": "Asia"},
    "Türkiye":        {"prefix": "TradeData_Tur_",       "sipri_name": "Türkiye",                   "color": "#E30A17", "flag": "🇹🇷", "region": "Middle East"},
}

REGIONS = sorted(set(v["region"] for v in COUNTRIES.values()))


# ── SIPRI loader (CSV) ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_sipri_csv():
    """Load SIPRI CSV once and cache it."""
    try:
        df = pd.read_csv('G20_Military_Expenditure_1949_2025.csv')
        df = df.set_index('Country')
        return df
    except Exception as e:
        return None


def get_sipri_monthly(country_name, sipri_df):
    """Get monthly SIPRI data for a country from the cached CSV."""
    sipri_name = COUNTRIES[country_name]["sipri_name"]
    if sipri_df is None or sipri_name not in sipri_df.index:
        return None
    row = sipri_df.loc[sipri_name]
    monthly_rows = []
    for yr in range(2010, 2025):
        val = row.get(str(yr), None)
        if val is not None and isinstance(val, (int, float)) and not pd.isna(val):
            for m in range(1, 13):
                monthly_rows.append({
                    'Date': pd.Timestamp(year=yr, month=m, day=1),
                    'Milex_Monthly_M': float(val) / 12
                })
    return pd.DataFrame(monthly_rows) if monthly_rows else None


# ── Arms data loader ──────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_arms_data(country_name):
    """
    Load all UN Comtrade CSV files for a country.
    Robustly handles different column formats across file versions.
    Detects annual vs monthly data automatically.
    """
    prefix = COUNTRIES[country_name]["prefix"]
    files = glob.glob(f"{prefix}*.csv")
    if not files:
        return None

    all_monthly = []

    for fpath in sorted(files):
        df = None
        for enc in ['utf-8', 'latin1', 'cp1252']:
            try:
                raw = open(fpath, 'rb').read()
                text = raw.decode(enc, errors='replace')
                df = pd.read_csv(StringIO(text))
                break
            except Exception:
                continue
        if df is None:
            continue

        # Convert fobvalue to numeric
        df['fobvalue'] = pd.to_numeric(df['fobvalue'], errors='coerce')

        # ── Robust annual/monthly detection ──────────────────────────────────
        # Strategy: search ALL columns to find:
        # (a) A column where all values are 52 → annual indicator
        # (b) A column where all values are valid years 2010-2024 → year column
        # This handles column shifts between different UN Comtrade file versions.

        year_col = None
        is_annual = False

        # Convert all columns to numeric for inspection
        numeric_cols = {}
        for col in df.columns:
            vals = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(vals) > 0:
                numeric_cols[col] = vals

        # Find columns that look like years (all values between 2009-2025)
        year_candidates = [
            col for col, vals in numeric_cols.items()
            if vals.between(2009, 2025).all() and len(vals) > 0
        ]

        # Find columns that contain only 52 (annual aggregate)
        annual_indicators = [
            col for col, vals in numeric_cols.items()
            if vals.isin([52]).all() and len(vals) > 0
        ]

        if annual_indicators and year_candidates:
            # Annual file confirmed
            is_annual = True
            # Prefer column named 'refMonth' or 'period' as year column
            for preferred in ['refMonth', 'period', 'refYear']:
                if preferred in year_candidates:
                    year_col = preferred
                    break
            if year_col is None:
                year_col = year_candidates[0]

        if is_annual and year_col:
            # ANNUAL FILE — group by year, divide by 12
            annual = df.groupby(year_col)['fobvalue'].sum().reset_index()
            annual.columns = ['Year', 'Annual_USD']
            for _, row in annual.iterrows():
                try:
                    yr = int(row['Year'])
                except Exception:
                    continue
                if 2010 <= yr <= 2024:
                    monthly_val = row['Annual_USD'] / 12
                    for m in range(1, 13):
                        all_monthly.append({
                            'Date': pd.Timestamp(year=yr, month=m, day=1),
                            'Arms_USD_M': monthly_val / 1_000_000
                        })
        else:
            # MONTHLY FILE — refMonth has YYYYMM format
            df['refMonth'] = pd.to_numeric(df['refMonth'], errors='coerce')
            df = df.dropna(subset=['refMonth'])
            df['refMonth'] = df['refMonth'].astype(int)
            df = df[df['refMonth'].between(201001, 202412)]
            monthly = df.groupby('refMonth')['fobvalue'].sum().reset_index()
            monthly.columns = ['YearMonth', 'Arms_USD']
            for _, row in monthly.iterrows():
                ym = str(int(row['YearMonth']))[:6]
                try:
                    date = pd.to_datetime(ym, format='%Y%m')
                    all_monthly.append({
                        'Date': date,
                        'Arms_USD_M': row['Arms_USD'] / 1_000_000
                    })
                except Exception:
                    continue

    if not all_monthly:
        return None

    result = pd.DataFrame(all_monthly)
    result = result.groupby('Date')['Arms_USD_M'].sum().reset_index()
    result = result.sort_values('Date').reset_index(drop=True)
    return result


# ── Build combined dataset ────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def build_country_data(country_name):
    sipri_df = load_sipri_csv()
    arms = load_arms_data(country_name)
    milex = get_sipri_monthly(country_name, sipri_df)

    if arms is None or milex is None or len(arms) == 0 or len(milex) == 0:
        return None

    df = pd.merge(arms, milex, on='Date')
    df['Dependency_Pct'] = (df['Arms_USD_M'] / df['Milex_Monthly_M']) * 100
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    return df


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ G20 Defense Dashboard")
    st.markdown("---")

    st.markdown("### 🏳️ Select Countries")
    selected = st.multiselect(
        "Choose countries to compare",
        options=list(COUNTRIES.keys()),
        default=["Saudi Arabia", "South Korea", "Türkiye"],
        format_func=lambda x: f"{COUNTRIES[x]['flag']} {x}"
    )

    st.markdown("### 📅 Time Period")
    start_year = st.slider("From year", 2010, 2023, 2010)
    end_year   = st.slider("To year",   2011, 2024, 2024)

    st.markdown("### 🔧 Display Options")
    show_peaks  = st.checkbox("Label peak for each country", value=True,
                              help="Marks the highest point reached by each country")
    show_events = st.checkbox("Show major world events", value=True,
                              help="Marks COVID-19, Russia-Ukraine war, Saudi Vision 2030")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#555; line-height:1.6;'>
    <b style='color:#888;'>What am I looking at?</b><br>
    What percentage of a country's military budget is spent buying weapons from abroad.<br><br>
    <b style='color:#888;'>Lower = more self-sufficient</b><br>
    A falling number means more weapons are built at home.<br><br>
    <b style='color:#888;'>Data Sources</b><br>
    • UN Comtrade (arms trade, HS Ch.93)<br>
    • SIPRI Military Expenditure 2025<br><br>
    <b style='color:#888;'>Coverage</b><br>
    19 G20 countries · 2010–2024
    </div>
    """, unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='border-bottom:3px solid #C8F542; padding-bottom:18px; margin-bottom:28px;'>
<h1 style='margin:0; font-size:2.2rem; color:#FFF; font-family:Rajdhani,sans-serif;'>
🛡️ G20 Defense Import Dependency
</h1>
<p style='margin:6px 0 0; color:#9E9E9E; font-size:0.95rem;'>
How much of each country's military budget goes to buying weapons from abroad? (2010–2024)
</p>
</div>
""", unsafe_allow_html=True)

if not selected:
    st.info("👈 Select at least one country from the sidebar to get started.")
    st.stop()


# ── Load data ─────────────────────────────────────────────────────────────────
country_data = {}
failed = []

with st.spinner("Loading data..."):
    for country in selected:
        df = build_country_data(country)
        if df is not None and len(df) > 0:
            mask = (df['Year'] >= start_year) & (df['Year'] <= end_year)
            filtered = df[mask].copy()
            if len(filtered) > 0:
                country_data[country] = filtered
            else:
                failed.append(country)
        else:
            failed.append(country)

if failed:
    st.warning(f"⚠️ Could not load data for: {', '.join(failed)}. Check files are uploaded to GitHub.")

if not country_data:
    st.error("No data loaded. Make sure CSV files and G20_Military_Expenditure_1949_2025.csv are in the repo.")
    st.stop()


# ── Stat Cards ────────────────────────────────────────────────────────────────
st.markdown("### At a Glance")
cols = st.columns(min(len(country_data), 4))

for i, (country, df) in enumerate(country_data.items()):
    cfg = COUNTRIES[country]
    current  = df['Dependency_Pct'].iloc[-1]
    peak     = df['Dependency_Pct'].max()
    peak_yr  = df.loc[df['Dependency_Pct'].idxmax(), 'Date'].strftime('%b %Y')
    first    = df['Dependency_Pct'].iloc[0]
    change   = current - first
    arrow    = "▼" if change < 0 else "▲"
    acolor   = "#C8F542" if change < 0 else "#E05252"

    with cols[i % 4]:
        st.markdown(f"""
        <div style='background:#161616; border-left:4px solid {cfg["color"]};
             border-radius:8px; padding:16px 18px; margin-bottom:10px;'>
        <div style='font-size:1.1rem; font-weight:700; color:{cfg["color"]}; margin-bottom:10px;'>
            {cfg["flag"]} {country}
        </div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:10px;'>
            <div>
                <div style='font-size:1.6rem; font-weight:700; color:#FFF;'>{current:.1f}%</div>
                <div style='font-size:0.7rem; color:#888; text-transform:uppercase;'>Current</div>
            </div>
            <div>
                <div style='font-size:1.6rem; font-weight:700; color:#E05252;'>{peak:.1f}%</div>
                <div style='font-size:0.7rem; color:#888; text-transform:uppercase;'>Peak ({peak_yr})</div>
            </div>
            <div>
                <div style='font-size:1.3rem; font-weight:700; color:{acolor};'>{arrow} {abs(change):.1f}%</div>
                <div style='font-size:0.7rem; color:#888; text-transform:uppercase;'>Since {start_year}</div>
            </div>
            <div>
                <div style='font-size:1.1rem; font-weight:600; color:#9E9E9E;'>{cfg["region"]}</div>
                <div style='font-size:0.7rem; color:#888; text-transform:uppercase;'>Region</div>
            </div>
        </div></div>
        """, unsafe_allow_html=True)


# ── Main Trend Chart ──────────────────────────────────────────────────────────
st.markdown("### Foreign Weapons Dependency Over Time")
st.caption("Annual average percentage of military budget spent on importing weapons from abroad — lower = more self-sufficient")

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('#0D0D0D')
ax.set_facecolor('#111111')

for country, df in country_data.items():
    cfg   = COUNTRIES[country]
    color = cfg['color']
    flag  = cfg['flag']

    # Use annual averages for clean plotting
    # (avoids step-function look from annual data distributed across months)
    annual_avg = df.groupby('Year')['Dependency_Pct'].mean().reset_index()
    annual_avg['Date'] = pd.to_datetime(annual_avg['Year'].astype(str) + '-07-01')

    ax.plot(annual_avg['Date'], annual_avg['Dependency_Pct'],
            color=color, linewidth=2.2, marker='o', markersize=4,
            label=f"{flag} {country}")

    if show_peaks:
        idx      = annual_avg['Dependency_Pct'].idxmax()
        peak_val = annual_avg.loc[idx, 'Dependency_Pct']
        peak_dt  = annual_avg.loc[idx, 'Date']
        ax.plot(peak_dt, peak_val, 'o', color=color, markersize=9, zorder=5)
        ax.annotate(
            f"{flag} {peak_val:.1f}%",
            xy=(peak_dt, peak_val),
            xytext=(0, 12), textcoords='offset points',
            fontsize=7.5, color=color, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#1A1A1A',
                      alpha=0.9, edgecolor=color, linewidth=0.8)
        )

if show_events:
    events = [
        ('2016-04-01', 'Vision 2030', '#888888'),
        ('2020-03-01', 'COVID-19',    '#AA8800'),
        ('2022-02-01', 'Russia-Ukraine War', '#CC4444'),
    ]
    ymax = max(df['Dependency_Pct'].max() for df in country_data.values())
    for date_str, label, ecolor in events:
        ed = pd.Timestamp(date_str)
        ax.axvline(ed, color=ecolor, linestyle=':', linewidth=1.2, alpha=0.6)
        ax.text(ed, ymax * 0.95, label, color=ecolor, fontsize=7,
                ha='center', va='top',
                bbox=dict(facecolor='#111', alpha=0.7, edgecolor='none', pad=2))

ax.set_xlabel("Year", fontsize=11, color='#9E9E9E')
ax.set_ylabel("Foreign Weapons Dependency (%)", fontsize=11, color='#9E9E9E')
ax.tick_params(colors='#9E9E9E', labelsize=9)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
for spine in ['bottom','left']:
    ax.spines[spine].set_color('#2A2A2A')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, color='#1A1A1A', linewidth=0.8)
ax.legend(fontsize=9.5, facecolor='#1C1C1C', edgecolor='#333',
          labelcolor='#FFF', loc='upper right', ncol=2, framealpha=0.9)
plt.tight_layout()
st.pyplot(fig)
plt.close()


# ── Annual Bar Chart ──────────────────────────────────────────────────────────
st.markdown("### Year-by-Year Comparison")
st.caption("Average dependency per year — useful for spotting when countries became more or less self-sufficient")

fig2, ax2 = plt.subplots(figsize=(14, 5))
fig2.patch.set_facecolor('#0D0D0D')
ax2.set_facecolor('#111111')

years_range = list(range(start_year, end_year + 1))
n      = len(country_data)
width  = min(0.8 / n, 0.15)
offsets = np.linspace(-(n-1)/2, (n-1)/2, n) * width

for idx, (country, df) in enumerate(country_data.items()):
    cfg    = COUNTRIES[country]
    annual = df.groupby('Year')['Dependency_Pct'].mean()
    x_pos  = [y + offsets[idx] for y in years_range if y in annual.index]
    y_vals = [annual[y] for y in years_range if y in annual.index]
    ax2.bar(x_pos, y_vals, width=width*0.88, color=cfg['color'], alpha=0.85,
            label=f"{cfg['flag']} {country}")

ax2.set_xlabel("Year", fontsize=11, color='#9E9E9E')
ax2.set_ylabel("Avg. Dependency (%)", fontsize=11, color='#9E9E9E')
ax2.tick_params(colors='#9E9E9E', labelsize=9)
ax2.set_xticks(years_range)
ax2.set_xticklabels(years_range, rotation=45)
for spine in ['bottom','left']:
    ax2.spines[spine].set_color('#2A2A2A')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.legend(fontsize=8.5, facecolor='#1C1C1C', edgecolor='#333',
           labelcolor='#FFF', ncol=3, framealpha=0.9)
ax2.grid(True, axis='y', color='#1A1A1A', linewidth=0.8)
plt.tight_layout()
st.pyplot(fig2)
plt.close()


# ── Rankings Table ────────────────────────────────────────────────────────────
st.markdown("### Country Rankings")
st.caption("Sorted highest to lowest current dependency")

rows = []
for country, df in country_data.items():
    cfg     = COUNTRIES[country]
    current = df['Dependency_Pct'].iloc[-1]
    peak    = df['Dependency_Pct'].max()
    peak_yr = df.loc[df['Dependency_Pct'].idxmax(), 'Date'].strftime('%b %Y')
    first   = df['Dependency_Pct'].iloc[0]
    change  = current - first
    trend   = "📉 Declining" if change < -0.5 else ("📈 Rising" if change > 0.5 else "➡️ Stable")
    rows.append({
        'Country': f"{cfg['flag']} {country}",
        'Region': cfg['region'],
        'Current (%)': round(current, 2),
        'Peak (%)': f"{round(peak, 2)} ({peak_yr})",
        f'Change since {start_year}': f"{'▼' if change < 0 else '▲'} {abs(change):.1f}%",
        'Trend': trend
    })

rankings = (pd.DataFrame(rows)
            .sort_values('Current (%)', ascending=False)
            .reset_index(drop=True))
rankings.index += 1
st.dataframe(rankings, use_container_width=True)


# ── Data Explorer ─────────────────────────────────────────────────────────────
with st.expander("🔍 Explore Raw Monthly Data"):
    choice = st.selectbox(
        "Select a country",
        options=list(country_data.keys()),
        format_func=lambda x: f"{COUNTRIES[x]['flag']} {x}"
    )
    if choice:
        raw = country_data[choice][['Date','Arms_USD_M','Milex_Monthly_M','Dependency_Pct']].copy()
        raw.columns = ['Month','Arms Imports (USD M)','Military Budget (USD M)','Dependency (%)']
        raw['Month'] = raw['Month'].dt.strftime('%Y-%m')
        raw = raw.round(2)
        st.dataframe(raw, use_container_width=True)
        st.caption(f"{len(raw)} records for {choice}")


# ── How to read ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💡 How to Read This Dashboard")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div style='background:#161616; border-radius:8px; padding:16px;'>
    <b style='color:#C8F542;'>What is dependency %?</b>
    <p style='color:#AAA; font-size:0.85rem; margin-top:8px;'>
    If a country's military budget is $100B and it buys $5B of weapons from abroad,
    its dependency is 5%. Lower means more weapons are made at home.
    </p></div>""", unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div style='background:#161616; border-radius:8px; padding:16px;'>
    <b style='color:#4A9FD5;'>Why do spikes happen?</b>
    <p style='color:#AAA; font-size:0.85rem; margin-top:8px;'>
    Spikes happen during wars or crises when countries urgently buy weapons.
    Saudi Arabia peaked in 2015 during the Yemen conflict.
    The 2022 spike in some countries reflects the Russia-Ukraine war.
    </p></div>""", unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div style='background:#161616; border-radius:8px; padding:16px;'>
    <b style='color:#FF9933;'>Data note</b>
    <p style='color:#AAA; font-size:0.85rem; margin-top:8px;'>
    This uses HS Chapter 93 (arms & ammunition) only.
    Large weapons like jets and warships are tracked under different codes.
    These numbers show direction and trends, not the complete picture.
    </p></div>""", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#444; font-size:0.8rem; padding:16px 0;'>
G20 Defense Import Dependency Dashboard · Mohammed Farran · Rice University RCEL 506 · April 2026<br>
Data: <a href='https://comtradeplus.un.org' style='color:#666;'>UN Comtrade</a> (HS Ch.93)
+ <a href='https://www.sipri.org/databases/milex' style='color:#666;'>SIPRI Military Expenditure 2025</a>
</div>
""", unsafe_allow_html=True)
