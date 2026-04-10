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
    data_file = Path(__file__).resolve().parents[1] / "dashboard" / "main_data.csv"
    df = pd.read_csv(data_file, keep_default_na=False)
    return {row["section"]: json.loads(row["payload"]) for _, row in df.iterrows()}

DATA = load_static_data()

monthly_stats = pd.DataFrame(DATA["monthly_stats"])
category_sales = pd.DataFrame(DATA["category_sales"])
geo_stats = pd.DataFrame(DATA["geo_stats"])
seg_count = pd.DataFrame(DATA["segment_counts"])
rfm_stats = pd.DataFrame(DATA["rfm_stats"])
geo_points_all = pd.DataFrame(DATA["geo_points"])

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
        Dashboard ini menjelaskan tren penjualan dan revenue dari data e-commerce salah satu perusahaan di Brazil selama periode 2017-2018. Dashboard ini juga menampilkan performa produk, distribusi pelanggan, serta segmentasi pelanggan untuk mendukung analisis bisnis.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filter Interaktif")
    top_n_categories = st.slider("Jumlah kategori teratas", 5, 20, 10)
    map_sample_size = st.slider("Jumlah titik pada peta", 500, len(geo_points_all), 2000, step=500)

geo_points = geo_points_all.head(map_sample_size)

meta = DATA["metadata"]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Order", f"{meta['kpi_total_orders']:,}")
col2.metric("Total Revenue", f"R$ {meta['kpi_total_revenue']:,.0f}")
col3.metric("State Aktif", f"{meta['kpi_active_states']:,}")
col4.metric("Pelanggan Unik", f"{meta['kpi_unique_customers']:,}")

st.caption(f"Periode data analisis: {meta['period_start']} sampai {meta['period_end']}")
st.divider()

q1, q2, q3, q4, q5, q6 = st.tabs(
    [
        "Pertanyaan 1: Tren Penjualan",
        "Pertanyaan 2: Kategori Produk",
        "Pertanyaan 3: Demografi Geografis",
        "Pertanyaan 4: Segmentasi RFM",
        "Geospatial Analysis",
        "Kesimpulan",
    ]
)

with q1:
    st.subheader("Tren performa penjualan dan revenue bulanan (2017-2018)")

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
  <li>Tren penjualan menunjukkan <strong>pertumbuhan yang konsisten dan signifikan</strong> sepanjang 2017 hingga awal 2018</li>
  <li>Terdapat <strong>lonjakan tajam pada November 2017</strong>, kemungkinan besar dipicu oleh event promosi besar seperti <em>Black Friday</em>; ini menjadi puncak penjualan tertinggi dalam dataset</li>
  <li><strong>Revenue dan jumlah order bergerak searah</strong> (berkorelasi positif), mengindikasikan nilai transaksi rata-rata yang relatif stabil</li>
  <li>Sepanjang pertengahan 2018, angka penjualan stabil di level tinggi, menandakan bisnis yang kian matang dan basis pelanggan yang sudah bertumbuh</li>
</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with q2:
    st.subheader("Kategori produk paling banyak dan paling sedikit terjual")

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

    st.write(
        f"Total kategori: **{len(category_sales):,}** | "
        f"Terlaris: **{category_sales.iloc[0]['product_category_name_english']}** ({category_sales.iloc[0]['total_sold']:,} item) | "
        f"Tersedikit: **{category_sales.iloc[-1]['product_category_name_english']}** ({category_sales.iloc[-1]['total_sold']:,} item)"
    )

    st.markdown(
        """
<div class="insight-box">
<strong>Insight Pertanyaan 2:</strong>
<ul>
  <li>Kategori <strong>bed_bath_table</strong>, <strong>health_beauty</strong>, dan <strong>sports_leisure</strong> adalah tiga kategori terlaris, mencerminkan kebutuhan sehari-hari pelanggan belanja online</li>
  <li>Dominasi kategori kebutuhan rumah tangga dan kesehatan menunjukkan karakteristik belanja online masyarakat Brazil</li>
  <li>Kategori dengan penjualan terendah adalah produk niche dan spesifik seperti <strong>security_and_services</strong> serta <strong>fashion_childrens_clothes</strong></li>
  <li><strong>Rekomendasi:</strong> untuk bisnis yaitu lebih difokuskan untuk meningkatkan stok dan promosi pada kategori terlaris, lalu evaluasi apakah kategori tersedikit layak dipertahankan atau perlu strategi khusus</li>
</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with q3:
    st.subheader("Distribusi pelanggan berdasarkan state di Brazil")

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
    top3_pct = geo_stats.head(3)["total_orders"].sum() / total_orders * 100
    st.info(
        f"State teratas: **{geo_stats.iloc[0]['customer_state']}** | "
        f"Share 3 state teratas: **{top3_pct:.1f}%** dari total order"
    )

    st.markdown(
        """
<div class="insight-box">
<strong>Insight Pertanyaan 3:</strong>
<ul>
  <li><strong>Sao Paulo (SP)</strong> mendominasi distribusi belanja online dengan nilai sebesar 40,494 (42,9%), sangat jauh daripada negara bagian lain, yang mencerminkan konsentrasi ekonomi digital di kota Sao Paulo Brazil</li>
  <li><strong>Rio de Janeiro (RJ)</strong> dan <strong>Minas Gerais (MG)</strong> berada di posisi 2 dan 3, sejalan  dengan status kota metropolitan</li>
  <li>Ketiga state teratas (SP, RJ, MG) menyumbang sekitar <strong>66% total order</strong> yang menunjukkan ketimpangan geografis antar state di Brazil</li>
  <li><strong>Rekomendasi:</strong> Optimalkan infrastruktur logistik dan warehouse di wilayah SP sebagai hub distribusi utama</li>
</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with q4:
    st.subheader("Segmentasi pelanggan berdasarkan RFM")

    left, right = st.columns(2)

    with left:
        fig_seg_bar = px.bar(
            seg_count,
            x="segment",
            y="count",
            color="segment",
            title="Jumlah Pelanggan per Segmen",
            color_discrete_map={
                "Champions": "#0B5D1E",
                "Loyal Customers": "#1F8A3A",
                "Potential Loyalists": "#57B36A",
                "At Risk": "#7BC67B",
                "Lost / Inactive": "#B7E36C",
            },
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
            color_discrete_map={
                "Champions": "#0B5D1E",
                "Loyal Customers": "#1F8A3A",
                "Potential Loyalists": "#57B36A",
                "At Risk": "#7BC67B",
                "Lost / Inactive": "#B7E36C",
            },
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
  <li><em>Calon Pelanggan loyal (47.4%)</em> cukup besar sehingga perusahaan perlu fokus pada peningkatan frekuensi belanja untuk mengubah mereka menjadi pelanggan loyal</li>
  <li><em>Risiko Churn (39.1%)</em>, gabungan segmen At Risk dan Lost cukup besar sehingga diperlukan strategi agar pelanggan tidak benar-benar pergi</li>
  <li><em>Kelangkaan pelanggan Champions (0.1%)</em> sehingga perlu strategi eskalasi dari segmen Loyal Customers</li>
  <li><strong>Rekomendasi Aksi:</strong></li>
  <li>Champions: Berikan apresiasi dan perlakuan VIP.</li>
  <li>Loyal &amp; Potential: Dorong pembelian berulang dengan promo personal atau membership.</li>
  <li>At Risk &amp; Lost: Kirim kampanye win-back (diskon besar) atau survei untuk reaktivasi.</li>
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
  <li>Visualisasi peta memperlihatkan <strong>titik-titik merah terkonsentrasi di wilayah pesisir tenggara Brazil</strong>, khususnya area metropolitan Sao Paulo, Rio de Janeiro, dan Belo Horizonte</li>
  <li>Pola distribusi ini konsisten dengan data ekonomi Brazil di wilayah <strong>tenggara adalah pusat perekonomian</strong> negara</li>
  <li>Wilayah <strong>Sul (Selatan)</strong> seperti Parana (PR), Rio Grande do Sul (RS), dan Santa Catarina (SC) menunjukkan pertumbuhan e-commerce yang aktif dan dapat menjadi target ekspansi berikutnya</li>
  <li><strong>Kawasan utara (Amazon region)</strong> hampir tidak memiliki pelanggan, alasannya karena keterbatasan infrastruktur internet dan akses logistik e-commerce</li>
  <li>Analisis ini menggunakan data koordinat nyata dari <code>geolocation</code> yang dikaitkan langsung dengan <code>customers</code> melalui kode pos</li>
</ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with q6:
    st.subheader("Kesimpulan Akhir Analisis")

    st.markdown(
        """
Setelah dilakukan analisis eksplorasi dan visualisasi di atas,dapat diambil kesimpulan bahwa

### 1. Tren Penjualan & Revenue *(Pertanyaan 1)*
Bisnis menunjukkan **pertumbuhan yang konsisten dan signifikan** dari Januari 2017 hingga pertengahan 2018. Puncak penjualan terjadi pada **November 2017**, yang terjadi karena adanya event promosi besar seperti *Black Friday*. Revenue dan jumlah order bergerak searah (korelasi positif), menandakan nilai rata-rata transaksi yang stabil. Tren ini mengindikasikan bisnis yang sehat dan sedang dalam fase pertumbuhan.

### 2. Performa Kategori Produk *(Pertanyaan 2)*
Kategori **bed_bath_table**, **health_beauty**, dan **sports_leisure** mendominasi penjualan. Sebaliknya, kategori niche seperti **security_and_services** dan **fashion_childrens_clothes** memiliki volume sangat rendah. Perusahaan belanja online perlu untuk *fokus pada investasi stok dan promosi pada kategori terlaris*, serta evaluasi kelayakan ekonomi kategori yang underperforming.

### 3. Demografi Geografis Pelanggan *(Pertanyaan 3)*
Pelanggan sangat terkonsentrasi di wilayah tenggara Brazil, terutama **São Paulo (SP)**, **Rio de Janeiro (RJ)**, dan **Minas Gerais (MG)**, dimana ketiganya menyumbang sebesar 66% dari total order. . Perusahaan belanja online perlu untuk *mengoptimalkan infrastruktur di SP sebagai hub utama* dan memperluas jangkauan logistik ke wilayah yang potensial seperti wilayah Sul (Selatan) dan wilayah Barat.

### 4. Segmentasi Pelanggan RFM *(Pertanyaan 4)*
Analisis RFM menunjukkan bahwa segmen terbesar adalah **calon pelanggan loyal (47.4%)**, sehingga perusahaan perlu fokus mendorong peningkatan frekuensi belanja agar mereka naik menjadi pelanggan loyal. Di sisi lain, **risiko churn (39.1%)** dari segmen **At Risk** dan **Lost** juga cukup tinggi, sehingga diperlukan strategi retensi dan reaktivasi. Sementara itu, pelanggan **Champions** masih sangat sedikit (0.1%), sehingga perlu strategi untuk mendorong pelanggan loyal naik ke segmen ini.

**Rekomendasi aksi:**
- **Champions:** berikan apresiasi dan perlakuan VIP.
- **Loyal & Potential:** dorong pembelian berulang melalui promo personal atau membership.
- **At Risk & Lost:** lakukan kampanye *win-back* seperti diskon besar atau survei reaktivasi.

### 5. Analisis Geospasial *(Tambahan)*
Analisis geospasial menunjukkan bahwa pelanggan terkonsentrasi di **wilayah tenggara Brazil**, terutama di sekitar **Sao Paulo, Rio de Janeiro, dan Belo Horizonte**, yang memang merupakan pusat ekonomi utama negara. Wilayah **selatan** seperti **Parana, Rio Grande do Sul, dan Santa Catarina** juga terlihat memiliki aktivitas e-commerce yang cukup kuat dan berpotensi menjadi area ekspansi berikutnya. Sebaliknya, **wilayah utara** masih memiliki jumlah pelanggan yang sangat rendah, kemungkinan dipengaruhi oleh keterbatasan infrastruktur internet dan logistik. Secara keseluruhan, persebaran pelanggan mencerminkan bahwa aktivitas e-commerce sangat dipengaruhi oleh kekuatan ekonomi dan ketersediaan infrastruktur di setiap wilayah.
        """
    )

st.divider()
st.caption(
    "Credit: Proyek Analisis Data: E-commerce Public Dataset | "
    "Nama: Zefanya Maureen Nathania | "
    "Email: CDCC293D6X1530@student.devacademy.id | "
    "ID Dicoding: CDCC293D6X1530"
)