import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Dashboard Analisis E-Commerce Public",
    page_icon="🛒",
    layout="wide",
)

BRAZIL_THEME = {
    "bg_dark": "#0A0F0C",
    "bg_panel": "#121A15",
    "bg_plot": "#151F19",
    "green_dark": "#0B5D1E",
    "green_primary": "#1F8A3A",
    "green_soft": "#7BC67B",
    "green_lime": "#B7E36C",
    "yellow": "#F4C430",
    "text_light": "#EAF6EE",
    "text_muted": "#B8D1BF",
    "white": "#FFFFFF",
}

SEGMENT_ORDER = ["Champions", "Loyal Customers", "Potential Loyalists", "At Risk", "Lost / Inactive"]
SEGMENT_COLOR_MAP = {
    "Champions": "#0B5D1E",
    "Loyal Customers": "#1F8A3A",
    "Potential Loyalists": "#57B36A",
    "At Risk": "#7BC67B",
    "Lost / Inactive": "#B7E36C",
}

INTERPRETASI_EDA_Q1 = """**Interpretasi EDA Plot Q1:**
- Persebaran total orders bulanan menunjukkan pola distribusi yang tercermin dari nilai skewness dan jumlah outlier pada output angka penting. Kondisi ini menandakan adanya bulan-bulan tertentu dengan performa yang jauh berbeda dari mayoritas bulan lainnya.
- Persebaran total revenue bulanan menunjukkan pola distribusi yang tercermin dari nilai skewness dan jumlah outlier pada output angka penting. Kondisi ini menandakan adanya bulan-bulan tertentu dengan performa revenue yang jauh berbeda dari mayoritas bulan lainnya."""

INTERPRETASI_EDA_Q2 = """**Interpretasi EDA Plot Q2:**
- Persebaran total item terjual per kategori cenderung tidak merata dan tercermin pada nilai skewness serta jumlah outlier pada output angka penting. Ini menunjukkan adanya beberapa kategori yang performanya sangat menonjol dibanding mayoritas kategori lain.
- Persebaran revenue item per kategori juga menunjukkan konsentrasi pada sebagian kecil kategori, terlihat dari nilai skewness dan outlier yang teridentifikasi. Artinya kontribusi revenue antar kategori belum tersebar secara seimbang."""

INTERPRETASI_EDA_Q3 = """**Interpretasi EDA Plot Q3:**
- Distribusi order antar state menunjukkan pola yang tercermin pada nilai skewness dan jumlah outlier pada output angka menunjukkan bahwa terdapat beberapa state dengan jumlah order jauh di atas state lainnya sehingga pasar bersifat terkonsentrasi."""

INTERPRETASI_EDA_Q4 = """**Interpretasi EDA Plot Q4:**
- Persebaran recency pelanggan terlihat dari nilai skewness dan jumlah outlier pada output angka penting; pola ini menunjukkan sebagian pelanggan memiliki jarak transaksi terakhir yang sangat berbeda dari mayoritas.
- Persebaran frequency pelanggan menunjukkan adanya kelompok pelanggan dengan intensitas belanja ekstrem (outlier), sehingga frekuensi pembelian cenderung tidak merata.
- Persebaran monetary pelanggan juga menampilkan outlier bernilai tinggi, yang menandakan sebagian kecil pelanggan berkontribusi jauh lebih besar terhadap total nilai transaksi."""

st.markdown(
    """
    <style>
    :root {
        --br-bg-dark: #0A0F0C;
        --br-bg-panel: #121A15;
        --br-bg-plot: #151F19;
        --br-green-dark: #0B5D1E;
        --br-green: #1F8A3A;
        --br-green-soft: #7BC67B;
        --br-green-lime: #B7E36C;
        --br-yellow: #F4C430;
        --br-text-light: #EAF6EE;
        --br-text-muted: #B8D1BF;
    }
    .stApp {
        background: radial-gradient(circle at top left, #1A2A1F 0%, #0A0F0C 38%, #080B09 100%);
        color: var(--br-text-light);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #132019 0%, #0F1713 100%);
        border-right: 1px solid #2D4434;
    }
    h1, h2, h3 {
        color: #DDFBE7;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #16241C 0%, #0F1814 100%);
        border: 1px solid #2E4A38;
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    }
    div[data-testid="stMetricLabel"] {
        color: #A8D8B4;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color: #EAF6EE;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        background: #132019;
        border-radius: 10px 10px 0 0;
        border: 1px solid #2D4434;
        color: #A7D6B2;
        font-weight: 600;
        margin-right: 4px;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, #1F8A3A 0%, #0B5D1E 100%);
        color: #F4FFF7;
        border-bottom: 2px solid #F4C430;
    }
    div[data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid #2E4A38;
    }
    .insight-box {
        background: linear-gradient(145deg, #16251C 0%, #0F1814 100%);
        border-left: 7px solid #F4C430;
        border: 1px solid #2E4A38;
        color: #EAF6EE;
        padding: 0.8rem 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_static_data():
    data_file = Path(__file__).resolve().parent / "main_data.csv"
    df = pd.read_csv(data_file, keep_default_na=False)
    return {row["section"]: json.loads(row["payload"]) for _, row in df.iterrows()}


def ensure_datetime(df, col="order_purchase_timestamp"):
    if df.empty or col not in df.columns:
        return df
    out = df.copy()
    out[col] = pd.to_datetime(out[col])
    return out


def filter_period(df, start_date, end_date, col="order_purchase_timestamp"):
    if df.empty or col not in df.columns:
        return df
    return df[(df[col] >= pd.Timestamp(start_date)) & (df[col] <= pd.Timestamp(end_date))].copy()


def iqr_outlier_count(series):
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return 0
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - (1.5 * iqr)
    upper = q3 + (1.5 * iqr)
    return int(((s < lower) | (s > upper)).sum())


def build_plot_stats(df, variables):
    rows = []
    for var in variables:
        if var not in df.columns:
            continue
        s = pd.to_numeric(df[var], errors="coerce").dropna()
        rows.append(
            {
                "variabel": var,
                "skewness": round(float(s.skew()), 3) if not s.empty else None,
                "jumlah_outlier_iqr": iqr_outlier_count(s),
            }
        )
    return pd.DataFrame(rows)


def robust_qcut_from_rank(series, reverse_labels=False):
    s = pd.to_numeric(series, errors="coerce")
    ranks = s.rank(method="first", ascending=True)
    bins = min(5, int(ranks.nunique()))
    if bins <= 1:
        return pd.Series([3.0] * len(series), index=series.index)
    labels = list(range(1, bins + 1))
    if reverse_labels:
        labels = labels[::-1]
    return pd.qcut(ranks, q=bins, labels=labels, duplicates="drop").astype(float)


def segment_customer_eda(score):
    if score >= 13:
        return "Champions"
    if score >= 10:
        return "Loyal Customers"
    if score >= 7:
        return "Potential Loyalists"
    if score >= 5:
        return "At Risk"
    return "Lost / Inactive"


def render_dist_box(df, col, title):
    if col not in df.columns or df.empty:
        st.info(f"Tidak ada data untuk {title}.")
        return

    left, right = st.columns(2)
    with left:
        fig_hist = px.histogram(
            df,
            x=col,
            nbins=30,
            title=f"Distribusi {title}",
            color_discrete_sequence=[BRAZIL_THEME["green_soft"]],
        )
        fig_hist.update_layout(
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=BRAZIL_THEME["bg_plot"],
            font=dict(color=BRAZIL_THEME["text_light"]),
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with right:
        fig_box = px.box(
            df,
            x=col,
            title=f"Box Plot {title}",
            color_discrete_sequence=[BRAZIL_THEME["green_lime"]],
        )
        fig_box.update_layout(
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=BRAZIL_THEME["bg_plot"],
            font=dict(color=BRAZIL_THEME["text_light"]),
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_box, use_container_width=True)


DATA = load_static_data()

meta = DATA["metadata"]
monthly_stats_all = ensure_datetime(pd.DataFrame(DATA["monthly_stats"]))
category_sales_monthly_all = ensure_datetime(pd.DataFrame(DATA.get("category_sales_monthly", [])))
geo_stats_monthly_all = ensure_datetime(pd.DataFrame(DATA.get("geo_stats_monthly", [])))
segment_counts_monthly_all = ensure_datetime(pd.DataFrame(DATA.get("segment_counts_monthly", [])))
geo_points_monthly_all = ensure_datetime(pd.DataFrame(DATA.get("geo_points_monthly", [])))
rfm_stats_base = pd.DataFrame(DATA["rfm_stats"])
eda_q1_agg_all = ensure_datetime(pd.DataFrame(DATA.get("eda_q1_agg", [])))
eda_q2_agg_monthly_all = ensure_datetime(pd.DataFrame(DATA.get("eda_q2_agg_monthly", [])))
eda_q3_agg_monthly_all = ensure_datetime(pd.DataFrame(DATA.get("eda_q3_agg_monthly", [])))
eda_plot_q4_source_all = ensure_datetime(pd.DataFrame(DATA.get("eda_plot_q4_source", [])))

available_start = pd.to_datetime(meta["period_start"]).date()
available_end = pd.to_datetime(meta["period_end"]).date()

if "filter_start" not in st.session_state:
    st.session_state["filter_start"] = available_start
if "filter_end" not in st.session_state:
    st.session_state["filter_end"] = available_end

st.title("Dashboard Analisis E-Commerce Public Dataset")
st.markdown(
    """
    <div style="
        background: linear-gradient(95deg, #0B5D1E 0%, #1F8A3A 60%, #F4C430 100%);
        padding: 1rem 1.2rem;
        border-radius: 14px;
        color: #F8FFF9;
        border: 2px solid #D2AE2F;
        margin-bottom: 0.8rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.38);
    ">
        Dashboard ini disusun mengikuti analisis terbaru di notebook (SMART business questions),
        dengan data simulasi bulanan periode Januari 2017 - Agustus 2018 agar tetap ringan saat deployment.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filter Interaktif")
    top_n_categories = st.slider("Jumlah kategori teratas", 5, 20, 10)

    with st.form("date_filter_form"):
        selected_range = st.date_input(
            "Rentang waktu analisis",
            value=(st.session_state["filter_start"], st.session_state["filter_end"]),
            min_value=available_start,
            max_value=available_end,
        )
        apply_range = st.form_submit_button("Terapkan Rentang Waktu")

    if apply_range:
        if isinstance(selected_range, tuple) and len(selected_range) == 2:
            st.session_state["filter_start"], st.session_state["filter_end"] = selected_range
        else:
            st.warning("Pilih tanggal mulai dan tanggal akhir.")

start_date = st.session_state["filter_start"]
end_date = st.session_state["filter_end"]

if start_date > end_date:
    st.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
    st.stop()

monthly_stats = filter_period(monthly_stats_all, start_date, end_date)
if monthly_stats.empty:
    st.warning("Tidak ada data pada rentang waktu yang dipilih.")
    st.stop()

category_sales = (
    filter_period(category_sales_monthly_all, start_date, end_date)
    .groupby("product_category_name_english", as_index=False)["total_sold"]
    .sum()
    .sort_values("total_sold", ascending=False)
)

geo_stats = (
    filter_period(geo_stats_monthly_all, start_date, end_date)
    .groupby("customer_state", as_index=False)[["total_orders", "unique_customers"]]
    .sum()
    .sort_values("total_orders", ascending=False)
)

seg_count = (
    filter_period(segment_counts_monthly_all, start_date, end_date)
    .groupby("segment", as_index=False)["count"]
    .sum()
)
seg_count["segment"] = pd.Categorical(seg_count["segment"], categories=SEGMENT_ORDER, ordered=True)
seg_count = seg_count.sort_values("segment")

geo_points_pool = filter_period(geo_points_monthly_all, start_date, end_date)
if geo_points_pool.empty:
    geo_points_pool = pd.DataFrame(DATA["geo_points"])

max_points = len(geo_points_pool)
if max_points == 0:
    st.warning("Tidak ada titik geospasial pada rentang waktu yang dipilih.")
    st.stop()

min_points = min(500, max_points)
default_points = min(2000, max_points)
with st.sidebar:
    map_step = 500 if max_points >= 1000 else max(10, max_points // 10)
    map_sample_size = st.slider("Jumlah titik pada peta", min_points, max_points, default_points, step=map_step)

geo_points = geo_points_pool.head(map_sample_size)

kpi_total_orders = int(monthly_stats["order_count"].sum())
kpi_total_revenue = float(monthly_stats["total_revenue"].sum())
kpi_active_states = int((geo_stats["total_orders"] > 0).sum()) if not geo_stats.empty else 0
kpi_unique_customers = int(seg_count["count"].sum()) if not seg_count.empty else 0

rfm_stats = rfm_stats_base.copy()
if not rfm_stats.empty:
    for col in ["recency", "frequency", "monetary"]:
        rfm_stats.loc[rfm_stats["metric"] == "count", col] = float(kpi_unique_customers)

# EDA dashboard datasets (sinkron dari section tambahan main_data.csv)
eda_q1_agg = filter_period(eda_q1_agg_all, start_date, end_date)
if eda_q1_agg.empty and not monthly_stats.empty:
    eda_q1_agg = monthly_stats[["order_purchase_timestamp", "order_count", "total_revenue"]].rename(
        columns={"order_count": "total_orders"}
    )
    eda_q1_agg["avg_revenue_per_order"] = eda_q1_agg["total_revenue"] / eda_q1_agg["total_orders"]

eda_q2_agg = (
    filter_period(eda_q2_agg_monthly_all, start_date, end_date)
    .groupby("product_category_name_english", as_index=False)[["total_sold", "unique_orders", "total_item_revenue"]]
    .sum()
    .sort_values("total_sold", ascending=False)
)
if not eda_q2_agg.empty:
    eda_q2_agg["item_share_pct"] = (
        eda_q2_agg["total_sold"] / eda_q2_agg["total_sold"].sum() * 100
    )

eda_q3_agg = (
    filter_period(eda_q3_agg_monthly_all, start_date, end_date)
    .groupby("customer_state", as_index=False)[["total_orders", "unique_customers"]]
    .sum()
    .sort_values("total_orders", ascending=False)
)
if not eda_q3_agg.empty:
    eda_q3_agg["order_share_pct"] = (
        eda_q3_agg["total_orders"] / eda_q3_agg["total_orders"].sum() * 100
    )

eda_q4_source = filter_period(eda_plot_q4_source_all, start_date, end_date)
if not eda_q4_source.empty:
    eda_q4_source = eda_q4_source.copy()
    eda_q4_source["payment_value"] = pd.to_numeric(eda_q4_source["payment_value"], errors="coerce").fillna(0)

if eda_q4_source.empty:
    eda_q4_rfm = pd.DataFrame(columns=["customer_unique_id", "recency", "frequency", "monetary", "segment"])
    eda_q4_segment = pd.DataFrame(columns=["segment", "total_customers", "avg_recency", "avg_frequency", "avg_monetary", "customer_share_pct"])
else:
    snapshot_date = pd.Timestamp(end_date) + pd.Timedelta(days=1)
    eda_q4_rfm = (
        eda_q4_source
        .groupby("customer_unique_id", as_index=False)
        .agg(
            recency=("order_purchase_timestamp", lambda x: (snapshot_date - x.max()).days),
            frequency=("order_id", "nunique"),
            monetary=("payment_value", "sum"),
        )
    )
    eda_q4_rfm["r_score"] = robust_qcut_from_rank(eda_q4_rfm["recency"], reverse_labels=True)
    eda_q4_rfm["f_score"] = robust_qcut_from_rank(eda_q4_rfm["frequency"], reverse_labels=False)
    eda_q4_rfm["m_score"] = robust_qcut_from_rank(eda_q4_rfm["monetary"], reverse_labels=False)
    eda_q4_rfm["rfm_score"] = eda_q4_rfm[["r_score", "f_score", "m_score"]].sum(axis=1)
    eda_q4_rfm["segment"] = eda_q4_rfm["rfm_score"].apply(segment_customer_eda)

    eda_q4_segment = (
        eda_q4_rfm
        .groupby("segment", as_index=False)
        .agg(
            total_customers=("customer_unique_id", "count"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
        )
    )
    eda_q4_segment["customer_share_pct"] = (
        eda_q4_segment["total_customers"] / eda_q4_segment["total_customers"].sum() * 100
    )
    eda_q4_segment["segment"] = pd.Categorical(eda_q4_segment["segment"], categories=SEGMENT_ORDER, ordered=True)
    eda_q4_segment = eda_q4_segment.sort_values("segment")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Order", f"{kpi_total_orders:,}")
col2.metric("Total Revenue", f"R$ {kpi_total_revenue:,.0f}")
col3.metric("State Aktif", f"{kpi_active_states:,}")
col4.metric("Pelanggan (Simulasi)", f"{kpi_unique_customers:,}")

st.caption(
    f"Periode data analisis: {start_date.strftime('%d %b %Y')} sampai {end_date.strftime('%d %b %Y')}"
)
st.divider()

eda_tab, q1, q2, q3, q4, q5, q6 = st.tabs(
    [
        "EDA (Agregasi & Plot)",
        "Pertanyaan 1: Tren Penjualan",
        "Pertanyaan 2: Kategori Produk",
        "Pertanyaan 3: Demografi Geografis",
        "Pertanyaan 4: Segmentasi RFM",
        "Geospatial Analysis",
        "Kesimpulan",
    ]
)

with eda_tab:
    st.subheader("Exploratory Data Analysis (EDA) - Agregasi & Plot")
    st.caption("Bagian ini menampilkan sinkronisasi hasil EDA agregasi dan EDA plot dari notebook ke dashboard interaktif.")

    st.markdown("### Pertanyaan 1 - Tren Penjualan & Revenue Bulanan")
    st.dataframe(eda_q1_agg, use_container_width=True)
    render_dist_box(eda_q1_agg, "total_orders", "Total Orders Bulanan")
    render_dist_box(eda_q1_agg, "total_revenue", "Total Revenue Bulanan")
    st.dataframe(build_plot_stats(eda_q1_agg, ["total_orders", "total_revenue"]), use_container_width=True)
    st.markdown(INTERPRETASI_EDA_Q1)
    st.divider()

    st.markdown("### Pertanyaan 2 - Performa Kategori Produk")
    st.dataframe(eda_q2_agg, use_container_width=True)
    render_dist_box(eda_q2_agg, "total_sold", "Total Item Terjual per Kategori")
    render_dist_box(eda_q2_agg, "total_item_revenue", "Revenue Item per Kategori")
    st.dataframe(build_plot_stats(eda_q2_agg, ["total_sold", "total_item_revenue"]), use_container_width=True)
    st.markdown(INTERPRETASI_EDA_Q2)
    st.divider()

    st.markdown("### Pertanyaan 3 - Kontribusi Order per State")
    st.dataframe(eda_q3_agg, use_container_width=True)
    render_dist_box(eda_q3_agg, "total_orders", "Total Orders per State")
    st.dataframe(build_plot_stats(eda_q3_agg, ["total_orders"]), use_container_width=True)
    st.markdown(INTERPRETASI_EDA_Q3)
    st.divider()

    st.markdown("### Pertanyaan 4 - Segmentasi Pelanggan Berbasis RFM")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Agregasi RFM Level Pelanggan")
        st.dataframe(eda_q4_rfm, use_container_width=True)
    with c2:
        st.markdown("#### Ringkasan Segmen RFM")
        st.dataframe(eda_q4_segment.round(2), use_container_width=True)

    render_dist_box(eda_q4_rfm, "recency", "Recency")
    render_dist_box(eda_q4_rfm, "frequency", "Frequency")
    render_dist_box(eda_q4_rfm, "monetary", "Monetary")
    st.dataframe(build_plot_stats(eda_q4_rfm, ["recency", "frequency", "monetary"]), use_container_width=True)
    st.markdown(INTERPRETASI_EDA_Q4)

with q1:
    st.subheader(
        "Pada periode terpilih, bagaimana tren performa penjualan (jumlah order) dan berapa revenue per bulannya?"
    )

    fig_q1 = go.Figure()
    fig_q1.add_trace(
        go.Bar(
            x=monthly_stats["order_month"],
            y=monthly_stats["total_revenue"],
            name="Total Revenue (R$)",
            marker_color=BRAZIL_THEME["green_soft"],
            opacity=0.8,
            yaxis="y1",
        )
    )
    fig_q1.add_trace(
        go.Scatter(
            x=monthly_stats["order_month"],
            y=monthly_stats["order_count"],
            name="Jumlah Order",
            mode="lines+markers",
            line=dict(color=BRAZIL_THEME["green_lime"], width=3),
            marker=dict(color=BRAZIL_THEME["yellow"], size=8),
            yaxis="y2",
        )
    )
    fig_q1.update_layout(
        height=500,
        xaxis=dict(title="Bulan", tickangle=-40),
        yaxis=dict(title="Total Revenue (R$)"),
        yaxis2=dict(title="Jumlah Order", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.08),
        margin=dict(l=20, r=20, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=BRAZIL_THEME["bg_plot"],
        font=dict(color=BRAZIL_THEME["text_light"]),
    )
    st.plotly_chart(fig_q1, use_container_width=True)

    idx_max_rev = monthly_stats["total_revenue"].idxmax()
    idx_max_ord = monthly_stats["order_count"].idxmax()

    c1, c2 = st.columns(2)
    c1.info(
        f"Revenue tertinggi: **{monthly_stats.loc[idx_max_rev, 'order_month']}** "
        f"(R$ {monthly_stats.loc[idx_max_rev, 'total_revenue']:,.0f})"
    )
    c2.info(
        f"Order terbanyak: **{monthly_stats.loc[idx_max_ord, 'order_month']}** "
        f"({monthly_stats.loc[idx_max_ord, 'order_count']:,.0f} order)"
    )

    st.markdown(
        """
<div class="insight-box">
<strong>Insight Pertanyaan 1:</strong>
<ul>
  <li>Pada periode terpilih, jumlah order dan revenue bulanan menunjukkan tren naik dari awal 2017 hingga puncak di akhir 2017/awal 2018.</li>
  <li>Lonjakan paling menonjol terjadi pada <strong>November 2017</strong> sebagai puncak performa bulanan.</li>
  <li>Pergerakan revenue searah dengan jumlah order, menandakan kenaikan transaksi menjadi pendorong utama pendapatan.</li>
  <li>Sepanjang 2018 performa cenderung stabil di level tinggi dibanding fase pertumbuhan awal.</li>
</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with q2:
    st.subheader(
        "Pada periode terpilih, kategori produk mana yang paling tinggi dan paling rendah penjualannya, serta kontribusi Top kategori?"
    )

    top_n = category_sales.head(top_n_categories)
    bot_n = category_sales.tail(top_n_categories)

    col_left, col_right = st.columns(2)

    with col_left:
        fig_top = px.bar(
            top_n.sort_values("total_sold"),
            x="total_sold",
            y="product_category_name_english",
            orientation="h",
            color="total_sold",
            color_continuous_scale=["#183A25", "#1F8A3A", "#7BC67B", "#B7E36C"],
            title=f"Top {top_n_categories} Kategori Terlaris",
        )
        fig_top.update_layout(
            height=500,
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=BRAZIL_THEME["bg_plot"],
            font=dict(color=BRAZIL_THEME["text_light"]),
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col_right:
        fig_bottom = px.bar(
            bot_n.sort_values("total_sold"),
            x="total_sold",
            y="product_category_name_english",
            orientation="h",
            color="total_sold",
            color_continuous_scale=["#102217", "#1A4E2C", "#2F7B42", "#74B66C"],
            title=f"Bottom {top_n_categories} Kategori Tersedikit",
        )
        fig_bottom.update_layout(
            height=500,
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=BRAZIL_THEME["bg_plot"],
            font=dict(color=BRAZIL_THEME["text_light"]),
        )
        st.plotly_chart(fig_bottom, use_container_width=True)

    total_items_sold = int(category_sales["total_sold"].sum()) if not category_sales.empty else 0
    top_n_share = (top_n["total_sold"].sum() / total_items_sold * 100) if total_items_sold else 0

    st.write(
        f"Total kategori: **{len(category_sales):,}** | "
        f"Terlaris: **{category_sales.iloc[0]['product_category_name_english']}** ({category_sales.iloc[0]['total_sold']:,} item) | "
        f"Tersedikit: **{category_sales.iloc[-1]['product_category_name_english']}** ({category_sales.iloc[-1]['total_sold']:,} item) | "
        f"Kontribusi Top {top_n_categories}: **{top_n_share:.2f}%**"
    )

    st.markdown(
        """
<div class="insight-box">
<strong>Insight Pertanyaan 2:</strong>
<ul>
  <li>Pada periode terpilih, kategori <strong>bed_bath_table</strong>, <strong>health_beauty</strong>, dan <strong>sports_leisure</strong> konsisten berada pada kontributor utama penjualan.</li>
  <li>Top kategori menyumbang porsi besar dari total item terjual sehingga layak diprioritaskan pada alokasi stok dan promosi.</li>
  <li>Kategori terbawah berkontribusi kecil dan dapat dievaluasi untuk strategi long-tail, efisiensi stok, atau kampanye niche.</li>
</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with q3:
    st.subheader(
        "Pada periode terpilih, state mana yang paling besar kontribusi order-nya dan berapa porsi Top 3 state?"
    )

    top10_states = geo_stats.head(10).copy()
    top5_states = geo_stats.head(5).copy()
    others_count = geo_stats.iloc[5:]["total_orders"].sum()

    left, right = st.columns(2)

    with left:
        fig_geo_bar = px.bar(
            top10_states.sort_values("total_orders"),
            x="total_orders",
            y="customer_state",
            orientation="h",
            color="total_orders",
            color_continuous_scale=["#183A25", "#1F8A3A", "#7BC67B", "#B7E36C"],
            title="Top 10 State Berdasarkan Jumlah Order",
        )
        fig_geo_bar.update_layout(
            height=500,
            coloraxis_showscale=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=BRAZIL_THEME["bg_plot"],
            font=dict(color=BRAZIL_THEME["text_light"]),
        )
        st.plotly_chart(fig_geo_bar, use_container_width=True)

    with right:
        pie_df = pd.DataFrame(
            {
                "state": list(top5_states["customer_state"]) + ["Others"],
                "orders": list(top5_states["total_orders"]) + [others_count],
            }
        )
        fig_geo_pie = px.pie(
            pie_df,
            names="state",
            values="orders",
            hole=0.4,
            title="Proporsi Order per State",
            color="state",
            color_discrete_sequence=["#0B5D1E", "#1F8A3A", "#57B36A", "#7BC67B", "#B7E36C", "#F4C430"],
        )
        fig_geo_pie.update_layout(
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=BRAZIL_THEME["text_light"]),
        )
        st.plotly_chart(fig_geo_pie, use_container_width=True)

    total_orders = geo_stats["total_orders"].sum()
    top3_pct = geo_stats.head(3)["total_orders"].sum() / total_orders * 100 if total_orders else 0
    st.info(
        f"State teratas: **{geo_stats.iloc[0]['customer_state']}** | "
        f"Share 3 state teratas: **{top3_pct:.1f}%** dari total order"
    )

    st.markdown(
        """
<div class="insight-box">
<strong>Insight Pertanyaan 3:</strong>
<ul>
  <li>Pada periode terpilih, distribusi order terkonsentrasi pada state besar seperti <strong>SP</strong>, lalu diikuti <strong>RJ</strong> dan <strong>MG</strong>.</li>
  <li>Metrik share Top 3 state menunjukkan tingkat konsentrasi pasar dan membantu menentukan prioritas wilayah operasional.</li>
  <li>State berkontribusi tertinggi cocok diprioritaskan untuk SLA pengiriman, kapasitas gudang, dan kampanye retention.</li>
</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with q4:
    st.subheader(
        "Pada periode terpilih, bagaimana komposisi segmen pelanggan RFM dan segmen prioritas retensi?"
    )

    left, right = st.columns(2)

    with left:
        fig_seg_bar = px.bar(
            seg_count,
            x="segment",
            y="count",
            color="segment",
            title="Jumlah Pelanggan per Segmen",
            color_discrete_map=SEGMENT_COLOR_MAP,
        )
        fig_seg_bar.update_layout(
            height=450,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=BRAZIL_THEME["bg_plot"],
            font=dict(color=BRAZIL_THEME["text_light"]),
        )
        st.plotly_chart(fig_seg_bar, use_container_width=True)

    with right:
        fig_seg_pie = px.pie(
            seg_count,
            names="segment",
            values="count",
            title="Komposisi Segmen Pelanggan (%)",
            hole=0.45,
            color="segment",
            color_discrete_map=SEGMENT_COLOR_MAP,
        )
        fig_seg_pie.update_layout(
            height=450,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=BRAZIL_THEME["text_light"]),
        )
        st.plotly_chart(fig_seg_pie, use_container_width=True)

    st.dataframe(rfm_stats, use_container_width=True)

    st.markdown(
        """
<div class="insight-box">
<strong>Insight Segmentasi RFM:</strong>
<ul>
  <li>Komposisi segmen pada periode terpilih menunjukkan porsi terbesar berada di <em>Potential Loyalists</em>.</li>
  <li>Gabungan segmen <em>At Risk</em> dan <em>Lost / Inactive</em> tetap signifikan sehingga butuh kampanye win-back yang terencana.</li>
  <li>Prioritas aksi retensi: dorong repeat purchase pada Potential Loyalists dan pertahankan Loyal/Champions dengan benefit eksklusif.</li>
</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with q5:
    st.subheader("Geospatial analysis sebaran pelanggan")

    fig_map = px.scatter_mapbox(
        geo_points,
        lat="geolocation_lat",
        lon="geolocation_lng",
        opacity=0.35,
        zoom=3.2,
        height=650,
        color_discrete_sequence=[BRAZIL_THEME["green_lime"]],
        hover_data={"customer_city": True, "customer_state": True},
    )
    fig_map.update_layout(
        mapbox_style="carto-darkmatter",
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BRAZIL_THEME["text_light"]),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown(
        """
<div class="insight-box">
<strong>Insight Geospatial Analysis:</strong>
<ul>
  <li>Visualisasi peta memperlihatkan titik-titik merah terkonsentrasi di wilayah pesisir tenggara Brazil, khususnya area metropolitan Sao Paulo, Rio de Janeiro, dan Belo Horizonte.</li>
  <li>Pola distribusi ini konsisten dengan data ekonomi Brazil bahwa wilayah tenggara adalah pusat perekonomian negara.</li>
  <li>Wilayah Sul (Parana, Rio Grande do Sul, Santa Catarina) menunjukkan aktivitas e-commerce aktif dan potensial untuk ekspansi.</li>
  <li>Kawasan utara (Amazon region) relatif minim pelanggan, sejalan dengan tantangan infrastruktur internet dan logistik e-commerce.</li>
  <li>Analisis ini menggunakan data koordinat geolocation yang dikaitkan dengan data customers melalui kode pos.</li>
</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with q6:
    st.subheader("Kesimpulan Akhir Analisis")

    st.markdown(
        """
Setelah dilakukan analisis eksplorasi dan visualisasi di atas, dapat diambil kesimpulan bahwa:

### 1. Tren Penjualan & Revenue *(Pertanyaan 1)*
Pada periode terpilih, performa penjualan bulanan menunjukkan tren meningkat dari awal 2017 lalu stabil di level tinggi pada 2018. Puncak performa terjadi sekitar November 2017, dan revenue bergerak searah dengan jumlah order.

### 2. Performa Kategori Produk *(Pertanyaan 2)*
Kategori bed_bath_table, health_beauty, dan sports_leisure menjadi kontributor utama volume penjualan. Metrik kontribusi Top kategori membantu penentuan prioritas stok dan anggaran promosi secara lebih terukur.

### 3. Demografi Geografis Pelanggan *(Pertanyaan 3)*
Order terkonsentrasi pada state besar seperti SP, RJ, dan MG. Share Top 3 state menjadi indikator praktis untuk strategi kapasitas logistik dan prioritas operasional regional.

### 4. Segmentasi Pelanggan RFM *(Pertanyaan 4)*
Mayoritas pelanggan berada pada segmen Potential Loyalists, sementara porsi At Risk dan Lost / Inactive tetap penting untuk strategi retensi. Fokus utama adalah meningkatkan repeat purchase dan menjalankan win-back campaign.

### 5. Analisis Geospasial *(Tambahan)*
Persebaran pelanggan terpadat berada di wilayah tenggara Brazil, konsisten dengan pusat ekonomi utama negara. Area selatan juga aktif, sedangkan wilayah utara relatif rendah, sehingga strategi ekspansi dan distribusi perlu dibedakan antar wilayah.

> Catatan: metrik non-bulanan pada dashboard disajikan menggunakan simulasi distribusi bulanan agar interaktif dan ringan untuk deployment satu file data.
        """
    )

st.divider()
st.caption(
    "Credit: Proyek Analisis Data: E-commerce Public Dataset | "
    "Nama: Zefanya Maureen Nathania | "
    "Email: CDCC293D6X1530@student.devacademy.id | "
    "ID Dicoding: CDCC293D6X1530"
)
