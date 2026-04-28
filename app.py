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
    "Saudi Arabia":   {"prefix": "TradeData_Sau_",       "sipri_name": "Saudi Arabia",             "color": "#C8F542", "flag": "🇸🇦"},
    "USA":            {"prefix": "TradeData_USA_",       "sipri_name": "United States of America", "color": "#4A9FD5", "flag": "🇺🇸"},
    "China":          {"prefix": "TradeData_Chn_",       "sipri_name": "China",                    "color": "#E05252", "flag": "🇨🇳"},
    "India":          {"prefix": "TradeData_Ind_",       "sipri_name": "India",                    "color": "#FF9933", "flag": "🇮🇳"},
    "Germany":        {"prefix": "TradeData_Ger_",       "sipri_name": "Germany",                  "color": "#FFCC00", "flag": "🇩🇪"},
    "United Kingdom": {"prefix": "TradeData_UK_",        "sipri_name": "United Kingdom",           "color": "#CF142B", "flag": "🇬🇧"},
    "France":         {"prefix": "TradeData_Fra_",       "sipri_name": "France",                   "color": "#4169E1", "flag": "🇫🇷"},
    "Japan":          {"prefix": "TradeData_Jap_",       "sipri_name": "Japan",                    "color": "#FF6B6B", "flag": "🇯🇵"},
    "Italy":          {"prefix": "TradeData_Ita_",       "sipri_name": "Italy",                    "color": "#009246", "flag": "🇮🇹"},
    "Canada":         {"prefix": "TradeData_Can_",       "sipri_name": "Canada",                   "color": "#FF4444", "flag": "🇨🇦"},
    "Australia":      {"prefix": "TradeData_Aus_",       "sipri_name": "Australia",                "color": "#00C49F", "flag": "🇦🇺"},
    "Brazil":         {"prefix": "TradeData_Bra_",       "sipri_name": "Brazil",                   "color": "#009C3B", "flag": "🇧🇷"},
    "Mexico":         {"prefix": "TradeData_Mex_",       "sipri_name": "Mexico",                   "color": "#006847", "flag": "🇲🇽"},
    "Indonesia":      {"prefix": "TradeData_Indonesia_", "sipri_name": "Indonesia",                "color": "#CE1126", "flag": "🇮🇩"},
    "Argentina":      {"prefix": "TradeData_Arg_",       "sipri_name": "Argentina",                "color": "#74ACDF", "flag": "🇦🇷"},
    "South Africa":   {"prefix": "TradeData_Afr_",       "sipri_name": "South Africa",             "color": "#007A4D", "flag": "🇿🇦"},
    "Russia":         {"prefix": "TradeData_Rus_",       "sipri_name": "Russia",                   "color": "#D52B1E", "flag": "🇷🇺"},
    "South Korea":    {"prefix": "TradeData_Kor_",       "sipri_name": "Korea, South",             "color": "#003478", "flag": "🇰🇷"},
    "Türkiye":        {"prefix": "TradeData_Tur_",       "sipri_name": "Türkiye",                  "color": "#E30A17", "flag": "🇹🇷"},
}


# ── SIPRI loader ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_sipri_csv():
    try:
        df = pd.read_csv('G20_Military_Expenditure_1949_2025.csv')
        df = df.set_index('Country')
        # Ensure year columns are accessible as strings
        df.columns = [str(c) for c in df.columns]
        return df
    except Exception as e:
        return None


def get_sipri_monthly(country_name, sipri_df):
    sipri_name = COUNTRIES[country_name]["sipri_name"]
    if sipri_df is None or sipri_name not in sipri_df.index:
        return None
    row = sipri_df.loc[sipri_name]
    monthly_rows = []
    for yr in range(2010, 2025):
        val = row.get(str(yr), None)
        if val is None:
            val = row.get(yr, None)
        if val is not None:
            try:
                fval = float(val)
                if not pd.isna(fval) and fval > 0:
                    for m in range(1, 13):
                        monthly_rows.append({
                            'Date': pd.Timestamp(year=yr, month=m, day=1),
                            'Milex_Monthly_M': fval / 12
                        })
            except Exception:
                continue
    return pd.DataFrame(monthly_rows) if monthly_rows else None


# ── Arms data loader ──────────────────────────────────────────────────────────
def parse_one_file(fpath):
    """
    Parse a single UN Comtrade CSV file.
    Returns list of {year: int, annual_usd: float} dicts or empty list.
    Also returns a debug string.
    """
    # Try multiple encodings
    df = None
    for enc in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']:
        try:
            df = pd.read_csv(fpath, encoding=enc, low_memory=False)
            break
        except Exception:
            continue
    if df is None:
        return [], f"FAILED to read file with any encoding"

    df['fobvalue'] = pd.to_numeric(df['fobvalue'], errors='coerce')

    # Find year column: look for a column where all values are 4-digit years 2010-2024
    # Find annual indicator: look for a column where all values are 52
    year_col = None
    has_52_col = False

    for col in df.columns:
        vals = pd.to_numeric(df[col], errors='coerce').dropna()
        if len(vals) == 0:
            continue
        if vals.isin([52]).all():
            has_52_col = True
        if vals.between(2009, 2026).all() and vals.nunique() <= 20:
            # This looks like a year column (≤20 unique values, all in year range)
            if year_col is None:
                year_col = col

    # Prefer specific column names
    for preferred in ['refMonth', 'period', 'refYear', 'refPeriodId']:
        if preferred in df.columns:
            vals = pd.to_numeric(df[preferred], errors='coerce').dropna()
            if len(vals) > 0 and vals.between(2009, 2026).all() and vals.nunique() <= 20:
                year_col = preferred
                break

    if not has_52_col or year_col is None:
        # Try treating as monthly (YYYYMM format)
        for col in ['refMonth', 'period']:
            if col in df.columns:
                vals = pd.to_numeric(df[col], errors='coerce').dropna()
                if vals.between(201001, 202412).any():
                    # Monthly format
                    df['_ym'] = pd.to_numeric(df[col], errors='coerce')
                    df = df[df['_ym'].between(201001, 202412)]
                    df['_year'] = (df['_ym'] // 100).astype(int)
                    annual = df.groupby('_year')['fobvalue'].sum().reset_index()
                    results = []
                    for _, row in annual.iterrows():
                        yr = int(row['_year'])
                        if 2010 <= yr <= 2024:
                            results.append({'year': yr, 'annual_usd': float(row['fobvalue'])})
                    return results, f"MONTHLY format, year col={col}, years={[r['year'] for r in results]}"
        return [], f"Could not detect format. has_52={has_52_col}, year_col={year_col}, cols={list(df.columns[:6])}"

    # Annual format
    annual = df.groupby(year_col)['fobvalue'].sum().reset_index()
    annual.columns = ['Year', 'fobvalue']
    results = []
    for _, row in annual.iterrows():
        try:
            yr = int(float(row['Year']))
        except Exception:
            continue
        if 2010 <= yr <= 2024:
            results.append({'year': yr, 'annual_usd': float(row['fobvalue'])})

    return results, f"ANNUAL format, year_col={year_col}, years={[r['year'] for r in results]}"


@st.cache_data(show_spinner=False)
def load_arms_data(country_name):
    prefix = COUNTRIES[country_name]["prefix"]
    files = sorted(glob.glob(f"{prefix}*.csv"))
    if not files:
        return None, [f"No files found matching {prefix}*.csv"]

    all_monthly = []
    debug_lines = [f"Found {len(files)} file(s): {[f.split('/')[-1] for f in files]}"]

    for fpath in files:
        fname = fpath.split('/')[-1]
        results, debug_msg = parse_one_file(fpath)
        debug_lines.append(f"  {fname}: {debug_msg}")

        for r in results:
            yr = r['year']
            monthly_val = r['annual_usd'] / 12
            for m in range(1, 13):
                all_monthly.append({
                    'Date': pd.Timestamp(year=yr, month=m, day=1),
                    'Arms_USD_M': monthly_val / 1_000_000
                })

    if not all_monthly:
        return None, debug_lines

    result = pd.DataFrame(all_monthly)
    result = result.groupby('Date')['Arms_USD_M'].sum().reset_index()
    result = result.sort_values('Date').reset_index(drop=True)
    debug_lines.append(f"  TOTAL: {len(result)} monthly rows, years {result['Date'].dt.year.min()}-{result['Date'].dt.year.max()}")
    return result, debug_lines


@st.cache_data(show_spinner=False)
def build_country_data(country_name):
    sipri_df = load_sipri_csv()
    arms, debug = load_arms_data(country_name)
    milex = get_sipri_monthly(country_name, sipri_df)
    if arms is None or milex is None:
        return None, debug
    df = pd.merge(arms, milex, on='Date')
    df['Dependency_Pct'] = (df['Arms_USD_M'] / df['Milex_Monthly_M']) * 100
    df['Year'] = df['Date'].dt.year
    return df, debug


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
    show_peaks  = st.checkbox("Label peak for each country", value=True)
    show_events = st.checkbox("Show major world events", value=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#555; line-height:1.6;'>
    <b style='color:#888;'>What am I looking at?</b><br>
    What percentage of a country's military budget is spent buying weapons from abroad.<br><br>
    <b style='color:#888;'>Lower = more self-sufficient</b><br>
    Data: UN Comtrade (HS Ch.93) + SIPRI 2025
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
        df, debug = build_country_data(country)
        if df is not None and len(df) > 0:
            mask = (df['Year'] >= start_year) & (df['Year'] <= end_year)
            filtered = df[mask].copy()
            if len(filtered) > 0:
                country_data[country] = filtered
            else:
                failed.append(f"{country} (no data in {start_year}-{end_year})")
        else:
            failed.append(country)

if failed:
    st.warning(f"⚠️ Could not load: {', '.join(failed)}")

if not country_data:
    st.error("No data loaded. Enable '🔍 Show file debug info' in the sidebar to diagnose.")
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
             border-radius:8px; padding:16px; margin-bottom:10px;'>
        <div style='font-size:1rem; font-weight:700; color:{cfg["color"]}; margin-bottom:8px;'>
            {cfg["flag"]} {country}</div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:8px;'>
            <div><div style='font-size:1.5rem; font-weight:700;'>{current:.1f}%</div>
            <div style='font-size:0.7rem; color:#888;'>CURRENT</div></div>
            <div><div style='font-size:1.5rem; font-weight:700; color:#E05252;'>{peak:.1f}%</div>
            <div style='font-size:0.7rem; color:#888;'>PEAK ({peak_yr})</div></div>
            <div><div style='font-size:1.2rem; font-weight:700; color:{acolor};'>{arrow} {abs(change):.1f}%</div>
            <div style='font-size:0.7rem; color:#888;'>SINCE {start_year}</div></div>
        </div></div>""", unsafe_allow_html=True)


# ── World Events Definition ───────────────────────────────────────────────────
WORLD_EVENTS = [
    ('2011-01-01', 'Arab Spring',               '#7B68EE'),
    ('2011-03-01', 'Libya Civil War',            '#9068BE'),
    ('2013-09-01', 'Syria Escalation',           '#BA55D3'),
    ('2014-03-01', 'Russia Annexes Crimea',      '#9370DB'),
    ('2015-03-01', 'Yemen War Begins',           '#FF8C00'),
    ('2016-04-01', 'Saudi Vision 2030',          '#AAAAAA'),
    ('2016-07-01', 'Turkey Failed Coup',         '#E30A17'),
    ('2017-01-01', 'Trump Defense Build-Up',     '#4A9FD5'),
    ('2018-03-01', 'India-Pakistan Tensions',    '#FF9933'),
    ('2019-05-01', 'US-China Trade War',         '#4682B4'),
    ('2020-03-01', 'COVID-19 Pandemic',          '#CCAA00'),
    ('2020-09-01', 'Armenia-Azerbaijan War',     '#DAA520'),
    ('2021-08-01', 'Afghanistan Withdrawal',     '#708090'),
    ('2022-02-01', 'Russia-Ukraine War',         '#CC4444'),
    ('2022-08-01', 'Taiwan Strait Crisis',       '#E05252'),
    ('2023-04-01', 'Sudan Civil War',            '#8B6914'),
    ('2023-10-01', 'Middle East Escalation',     '#CD853F'),
    ('2024-01-01', 'NATO Defense Push',          '#336699'),
]

# ── Main Chart ────────────────────────────────────────────────────────────────
st.markdown("### Foreign Weapons Dependency Over Time")
st.caption("Annual average — lower = more self-sufficient")

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('#0D0D0D')
ax.set_facecolor('#111111')

for country, df in country_data.items():
    cfg = COUNTRIES[country]
    annual_avg = df.groupby('Year')['Dependency_Pct'].mean().reset_index()
    annual_avg['Date'] = pd.to_datetime(annual_avg['Year'].astype(str) + '-07-01')
    ax.plot(annual_avg['Date'], annual_avg['Dependency_Pct'],
            color=cfg['color'], linewidth=2.2, marker='o', markersize=4,
            label=f"{cfg['flag']} {country}")
    if show_peaks:
        idx = annual_avg['Dependency_Pct'].idxmax()
        pv  = annual_avg.loc[idx, 'Dependency_Pct']
        pd_ = annual_avg.loc[idx, 'Date']
        ax.plot(pd_, pv, 'o', color=cfg['color'], markersize=9, zorder=5)
        ax.annotate(f"{cfg['flag']} {pv:.1f}%", xy=(pd_, pv),
                    xytext=(0, 12), textcoords='offset points',
                    fontsize=7.5, color=cfg['color'], fontweight='bold', ha='center',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#1A1A1A',
                              alpha=0.9, edgecolor=cfg['color'], linewidth=0.8))

if show_events:
    visible_events = [
        (d, l, c) for d, l, c in WORLD_EVENTS
        if pd.Timestamp(f'{start_year}-01-01') <= pd.Timestamp(d) <= pd.Timestamp(f'{end_year}-12-31')
    ]
    for date_str, label, ecolor in visible_events:
        ed = pd.Timestamp(date_str)
        ax.axvline(ed, color=ecolor, linestyle=':', linewidth=1.0, alpha=0.5)

ax.set_xlabel("Year", fontsize=11, color='#9E9E9E')
ax.set_ylabel("Dependency (%)", fontsize=11, color='#9E9E9E')
ax.tick_params(colors='#9E9E9E', labelsize=9)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
for sp in ['bottom','left']:
    ax.spines[sp].set_color('#2A2A2A')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, color='#1A1A1A', linewidth=0.8)
ax.legend(fontsize=9.5, facecolor='#1C1C1C', edgecolor='#333',
          labelcolor='#FFF', loc='upper right', ncol=2, framealpha=0.9)
plt.tight_layout()
st.pyplot(fig)
plt.close()


# ── Annual Bar Chart ──────────────────────────────────────────────────────────
# ── Events Legend ────────────────────────────────────────────────────────────
if show_events:
    visible_events = [
        (d, l, c) for d, l, c in WORLD_EVENTS
        if pd.Timestamp(f'{start_year}-01-01') <= pd.Timestamp(d) <= pd.Timestamp(f'{end_year}-12-31')
    ]
    if visible_events:
        st.markdown("**Key Events shown on chart:**")
        pills = " &nbsp;".join([
            f"<span style='background:#1A1A1A; border-left:3px solid {c}; "
            f"padding:3px 8px; border-radius:3px; font-size:0.78rem; color:#CCC;'>"
            f"{pd.Timestamp(d).strftime('%Y')} &nbsp;{l}</span>"
            for d, l, c in visible_events
        ])
        st.markdown(f"<div style='line-height:2.2;'>{pills}</div>", unsafe_allow_html=True)
        st.markdown("")

st.markdown("### Year-by-Year Comparison")
fig2, ax2 = plt.subplots(figsize=(14, 5))
fig2.patch.set_facecolor('#0D0D0D')
ax2.set_facecolor('#111111')
years_range = list(range(start_year, end_year + 1))
n = len(country_data)
width = min(0.8/n, 0.15)
offsets = np.linspace(-(n-1)/2, (n-1)/2, n) * width
for idx, (country, df) in enumerate(country_data.items()):
    cfg = COUNTRIES[country]
    annual = df.groupby('Year')['Dependency_Pct'].mean()
    x_pos = [y + offsets[idx] for y in years_range if y in annual.index]
    y_vals = [annual[y] for y in years_range if y in annual.index]
    ax2.bar(x_pos, y_vals, width=width*0.88, color=cfg['color'], alpha=0.85,
            label=f"{cfg['flag']} {country}")
ax2.set_xlabel("Year", fontsize=11, color='#9E9E9E')
ax2.set_ylabel("Avg. Dependency (%)", fontsize=11, color='#9E9E9E')
ax2.tick_params(colors='#9E9E9E', labelsize=9)
ax2.set_xticks(years_range)
ax2.set_xticklabels(years_range, rotation=45)
for sp in ['bottom','left']:
    ax2.spines[sp].set_color('#2A2A2A')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.legend(fontsize=8.5, facecolor='#1C1C1C', edgecolor='#333',
           labelcolor='#FFF', ncol=3, framealpha=0.9)
ax2.grid(True, axis='y', color='#1A1A1A', linewidth=0.8)
plt.tight_layout()
st.pyplot(fig2)
plt.close()


# ── Rankings ──────────────────────────────────────────────────────────────────
st.markdown("### Country Rankings")
rows = []
for country, df in country_data.items():
    cfg = COUNTRIES[country]
    current = df['Dependency_Pct'].iloc[-1]
    peak    = df['Dependency_Pct'].max()
    peak_yr = df.loc[df['Dependency_Pct'].idxmax(), 'Date'].strftime('%b %Y')
    first   = df['Dependency_Pct'].iloc[0]
    change  = current - first
    trend   = "📉 Declining" if change < -0.5 else ("📈 Rising" if change > 0.5 else "➡️ Stable")
    rows.append({'Country': f"{cfg['flag']} {country}",
                 'Current (%)': round(current, 2),
                 'Peak (%)': f"{round(peak,2)} ({peak_yr})",
                 f'Change since {start_year}': f"{'▼' if change<0 else '▲'} {abs(change):.1f}%",
                 'Trend': trend})
st.dataframe(pd.DataFrame(rows).sort_values('Current (%)', ascending=False)
             .reset_index(drop=True), use_container_width=True)


# ── Data Explorer ─────────────────────────────────────────────────────────────
with st.expander("🔍 Explore Raw Data"):
    choice = st.selectbox("Select country", list(country_data.keys()),
                          format_func=lambda x: f"{COUNTRIES[x]['flag']} {x}")
    if choice:
        raw = country_data[choice][['Date','Arms_USD_M','Milex_Monthly_M','Dependency_Pct']].copy()
        raw.columns = ['Month','Arms Imports (USD M)','Military Budget (USD M)','Dependency (%)']
        raw['Month'] = raw['Month'].dt.strftime('%Y-%m')
        st.dataframe(raw.round(2), use_container_width=True)


# ── How to read ───────────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div style='background:#161616;border-radius:8px;padding:16px;'>
    <b style='color:#C8F542;'>What is dependency %?</b>
    <p style='color:#AAA;font-size:0.85rem;margin-top:8px;'>
    If a military budget is $100B and $5B goes to foreign weapons, dependency = 5%. Lower = more self-sufficient.
    </p></div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div style='background:#161616;border-radius:8px;padding:16px;'>
    <b style='color:#4A9FD5;'>Why do spikes happen?</b>
    <p style='color:#AAA;font-size:0.85rem;margin-top:8px;'>
    Wars or crises cause countries to urgently buy weapons abroad. Saudi Arabia peaked in 2015 during Yemen conflict.
    </p></div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div style='background:#161616;border-radius:8px;padding:16px;'>
    <b style='color:#FF9933;'>Data note</b>
    <p style='color:#AAA;font-size:0.85rem;margin-top:8px;'>
    Uses HS Chapter 93 only (arms & ammunition). Large weapons like jets are tracked separately.
    </p></div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""<div style='text-align:center;color:#444;font-size:0.8rem;padding:16px 0;'>
G20 Defense Import Dependency · Mohammed Farran · Rice University RCEL 506 · April 2026<br>
Data: UN Comtrade (HS Ch.93) + SIPRI Military Expenditure 2025
</div>""", unsafe_allow_html=True)
