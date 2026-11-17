import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="Farg‘ona Travel Planner",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Ma'lumotlar bazasi
# -----------------------------
tourist_spots = [
    {"name": "Xudoyorxon o‘rdasi", "city": "Qo‘qon", "tags": ["tarixiy", "madaniy"], "time": 2.0, "cost": 30000, "cluster": "G‘arb"},
    {"name": "Jome masjidi va amaliy san’at muzeyi", "city": "Qo‘qon", "tags": ["tarixiy", "me’moriy"], "time": 1.5, "cost": 20000, "cluster": "G‘arb"},
    {"name": "Norbo‘tabiy madrasasi", "city": "Qo‘qon", "tags": ["ziyorat", "tarixiy"], "time": 1.0, "cost": 0, "cluster": "G‘arb"},
    {"name": "Daxmai Shohon maqbarasi", "city": "Qo‘qon", "tags": ["tarixiy", "ziyorat"], "time": 1.0, "cost": 15000, "cluster": "G‘arb"},
    {"name": "Yodgorlik ipak fabrikasi", "city": "Marg‘ilon", "tags": ["hunarmandchilik", "madaniy"], "time": 2.0, "cost": 40000, "cluster": "Markaz"},
    {"name": "Hunarmandlar markazi (Said Ahmad Xo‘ja)", "city": "Marg‘ilon", "tags": ["hunarmandchilik", "madaniy"], "time": 1.5, "cost": 15000, "cluster": "Markaz"},
    {"name": "Pir Siddiq majmuasi (Kaptarlik)", "city": "Marg‘ilon", "tags": ["ziyorat", "tarixiy"], "time": 1.0, "cost": 0, "cluster": "Markaz"},
    {"name": "Al-Farg‘oniy nomidagi markaziy bog‘", "city": "Farg‘ona", "tags": ["ekoturizm", "dam olish"], "time": 2.0, "cost": 30000, "cluster": "Markaz"},
    {"name": "Farg‘ona o‘lkashunoslik muzeyi", "city": "Farg‘ona", "tags": ["tarixiy", "madaniy"], "time": 1.5, "cost": 15000, "cluster": "Markaz"},
    {"name": "Rishton kulolchilik markazi", "city": "Rishton", "tags": ["hunarmandchilik", "madaniy"], "time": 2.5, "cost": 50000, "cluster": "G‘arb"},
    {"name": "Shohimardon (Ko‘kko‘l va Qurbanko‘l)", "city": "Farg‘ona tumani", "tags": ["ekoturizm", "dam olish"], "time": 6.0, "cost": 200000, "cluster": "Janub"},
    {"name": "Vodil chinorlari va ziyoratgohi", "city": "Farg‘ona tumani", "tags": ["ekoturizm", "ziyorat", "gastronomiya"], "time": 2.5, "cost": 80000, "cluster": "Janub"},
    {"name": "Oltiariq uzumzorlari (Agroturizm)", "city": "Oltiariq", "tags": ["agroturizm", "ekoturizm", "gastronomiya"], "time": 2.5, "cost": 60000, "cluster": "G‘arb"},
    {"name": "Quva qadimiy shahristoni va Al-Farg‘oniy majmuasi", "city": "Quva", "tags": ["tarixiy", "ziyorat"], "time": 2.0, "cost": 15000, "cluster": "Sharq"},
    {"name": "Chimen sanatoriysi va buloqlari", "city": "Farg‘ona tumani", "tags": ["sog‘lomlashtirish", "dam olish"], "time": 3.5, "cost": 120000, "cluster": "Janub"},
]

df = pd.DataFrame(tourist_spots)
ALL_INTERESTS = sorted({tag for tags in df["tags"] for tag in tags})
CLUSTER_ORDER = {"G‘arb": 0, "Markaz": 1, "Sharq": 2, "Janub": 3}

# -----------------------------
# Tavsiya algoritmi
# -----------------------------
def recommend_itinerary(user_interests, max_budget, max_hours, travel_time=0.5, travel_cost=15000, preferred_cities=None):
    scored = []
    for _, row in df.iterrows():
        if preferred_cities and row["city"] not in preferred_cities:
            continue
        match_score = len(set(user_interests).intersection(row["tags"]))
        if match_score:
            item = row.to_dict()
            item["tags_text"] = ", ".join(row["tags"])
            item["score"] = match_score
            scored.append(item)

    # Avval qiziqishga moslik, keyin arzonlik va tashrif vaqtiga ko‘ra
    scored.sort(key=lambda x: (-x["score"], x["cost"], x["time"]))
    selected, total_time, total_cost = [], 0.0, 0

    for spot in scored:
        extra_time = travel_time if selected else 0
        extra_cost = travel_cost if selected else 0
        if total_time + spot["time"] + extra_time <= max_hours and total_cost + spot["cost"] + extra_cost <= max_budget:
            selected.append(spot)
            total_time += spot["time"] + extra_time
            total_cost += spot["cost"] + extra_cost

    selected.sort(key=lambda x: (CLUSTER_ORDER.get(x["cluster"], 99), -x["score"], x["name"]))
    return selected, total_time, total_cost

# -----------------------------
# Uslub
# -----------------------------
st.markdown("""
<style>
    .stApp { background: #f7f9fc; }
    [data-testid="stSidebar"] { background: #102a43; }
    [data-testid="stSidebar"] * { color: #f4f7fb !important; }
    .hero { padding: 28px 32px; border-radius: 20px; background: linear-gradient(135deg, #0f766e, #155e75); color: white; margin-bottom: 24px; }
    .hero h1 { margin: 0 0 8px 0; font-size: 2.3rem; }
    .hero p { margin: 0; opacity: .9; font-size: 1.05rem; }
    .route-card { background: white; border: 1px solid #e5eaf0; border-radius: 14px; padding: 16px 18px; margin: 9px 0; box-shadow: 0 2px 8px rgba(15, 42, 67, .04); }
    .route-number { background: #0f766e; color: white; border-radius: 50%; display: inline-flex; width: 30px; height: 30px; justify-content: center; align-items: center; font-weight: 700; margin-right: 10px; }
    .muted { color: #64748b; font-size: .9rem; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #e5eaf0; border-radius: 12px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.markdown("## 🧭 Farg‘ona Travel Planner")
st.sidebar.caption("Qiziqishlaringiz va imkoniyatlaringizga mos marshrut yarating.")
st.sidebar.divider()

interests = st.sidebar.multiselect(
    "Sizni nimalar qiziqtiradi?",
    ALL_INTERESTS,
    default=["tarixiy", "madaniy"],
    format_func=lambda x: x.capitalize(),
)
max_budget = st.sidebar.number_input(
    "Maksimal byudjet (so‘m)", min_value=0, max_value=10_000_000,
    value=150_000, step=10_000, format="%d",
)
max_hours = st.sidebar.slider("Safar davomiyligi (soat)", 1.0, 24.0, 8.0, 0.5)
travel_time = st.sidebar.number_input("Manzillar orasidagi yo‘l (soat)", 0.0, 5.0, 0.5, 0.5)
travel_cost = st.sidebar.number_input("Har bir yo‘l uchun kira (so‘m)", 0, 1_000_000, 15_000, 5_000, format="%d")

all_cities = sorted(df["city"].unique())
selected_cities = st.sidebar.multiselect("Hudud bo‘yicha ixtiyoriy filtr", all_cities)

if st.sidebar.button("♻️ Standart sozlamalarni tiklash", use_container_width=True):
    st.rerun()

# -----------------------------
# Asosiy sahifa
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>Farg‘ona bo‘ylab sayohatingizni rejalashtiring</h1>
    <p>Qiziqishlaringiz, vaqtingiz va byudjetingiz asosida mos turistik yo‘nalishni bir necha soniyada toping.</p>
</div>
""", unsafe_allow_html=True)

if not interests:
    st.warning("Boshlash uchun chap paneldan kamida bitta qiziqish turini tanlang.")
    st.stop()

route, total_time, total_cost = recommend_itinerary(
    interests, max_budget, max_hours, travel_time, travel_cost, selected_cities or None
)

available_count = sum(1 for _, row in df.iterrows() if set(interests).intersection(row["tags"]))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tavsiya etilgan obyektlar", len(route))
c2.metric("Jami vaqt", f"{total_time:.1f} soat")
c3.metric("Taxminiy xarajat", f"{total_cost:,} so‘m")
c4.metric("Mos obyektlar", available_count)

st.markdown("### Siz uchun tavsiya etilgan marshrut")
if not route:
    st.error("Tanlangan cheklovlar bo‘yicha mos marshrut topilmadi. Byudjet yoki vaqtni oshirib ko‘ring.")
else:
    st.caption(f"Tanlangan qiziqishlar: {', '.join(i.capitalize() for i in interests)}")
    for i, item in enumerate(route, 1):
        st.markdown(f"""
        <div class="route-card">
            <div><span class="route-number">{i}</span><strong>{item['name']}</strong></div>
            <div class="muted" style="margin: 8px 0 0 40px;">📍 {item['city']} · 🧭 {item['cluster']} yo‘nalishi · 🏷️ {item['tags_text']}</div>
            <div style="margin: 6px 0 0 40px;">⏱️ {item['time']:.1f} soat &nbsp;&nbsp; 💰 {item['cost']:,} so‘m &nbsp;&nbsp; ⭐ Moslik: {item['score']}</div>
        </div>
        """, unsafe_allow_html=True)

    result_df = pd.DataFrame([
        {"№": i, "Obyekt": item["name"], "Shahar/tuman": item["city"], "Yo‘nalish": item["cluster"], "Teglar": item["tags_text"], "Tashrif vaqti (soat)": item["time"], "Kirish (so‘m)": item["cost"], "Moslik bali": item["score"]}
        for i, item in enumerate(route, 1)
    ])

    tab1, tab2 = st.tabs(["📋 Jadval ko‘rinishi", "📊 Tahlil"])
    with tab1:
        st.dataframe(result_df, use_container_width=True, hide_index=True)
    with tab2:
        chart_df = result_df[["Obyekt", "Tashrif vaqti (soat)"]].set_index("Obyekt")
        st.bar_chart(chart_df)

    csv = result_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Marshrutni CSV sifatida yuklab olish", csv, "fargona_marshrut.csv", "text/csv")

with st.expander("ℹ️ Hisoblash qanday ishlaydi?"):
    st.write("Har bir obyekt siz tanlagan qiziqishlar bilan kesishadigan teglar soni bo‘yicha baholanadi. Keyin obyektlar moslik bali, narxi va tashrif vaqtiga ko‘ra saralanadi. Har bir keyingi manzil uchun standart yo‘l vaqti hamda yo‘l kira qiymati qo‘shiladi.")
    st.caption("Eslatma: narxlar va vaqtlar taxminiy bo‘lib, safardan oldin aniqlashtirilishi tavsiya etiladi.")

st.divider()
st.caption("Farg‘ona Travel Planner · Streamlit prototipi")
