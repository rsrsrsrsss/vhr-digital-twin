import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="АЕЦ Козлодуй - ВХР Дигитален Двойник (Пълен Комплект)",
    page_icon="⚛️",
    layout="wide"
)

# --- ПРОФЕСИОНАЛНА ЗАГЛАВНА ЛЕНТА ---
st.markdown("""
    <div style='background-color:#0e1117; padding:15px; border-radius:10px; border:1px solid #30363d; margin-bottom:20px'>
        <h2 style='color:#58a6ff; margin:0;'>⚛️ АЕЦ Козлодуй — Дигитален Двойник на Водно-Химичния Режим</h2>
        <p style='color:#8b949e; margin:5px 0 0 0;'>Блок 5 / Блок 6 | Мониторинг на ВВЕР-1000, СВО, Симулатор на Сценарии & Прогнозен Анализ</p>
    </div>
""", unsafe_allow_html=True)

# --- СЕСИЙНИ ПРОМЕНЛИВИ ---
if 'dosed_nh3' not in st.session_state:
    st.session_state.dosed_nh3 = False
if 'dosed_n2h4' not in st.session_state:
    st.session_state.dosed_n2h4 = False
if 'scenario' not in st.session_state:
    st.session_state.scenario = "Нормален режим"

# --- ИЗЧИСЛИТЕЛНИ ФУНКЦИИ ---
def calc_ph_temp(ph_25, temp_c):
    kw_25 = 1e-14
    kw_t = 10**(-(14.0 - 0.03 * (temp_c - 25) + 0.0001 * (temp_c - 25)**2))
    delta_ph = (np.log10(kw_25) - np.log10(kw_t)) / 2.0
    return max(5.0, ph_25 - delta_ph)

def calc_orp(o2_ppb, temp_c):
    return -400.0 + (temp_c * 0.5) + 60.0 * np.log10(max(o2_ppb, 0.1) + 1.0)

def calc_conductivities(ph_val, cond_base, o2_ppb):
    chi_spec = cond_base + (10**(ph_val - 14) * 250.0)
    chi_cat = cond_base * 0.85 + (o2_ppb * 0.002)
    return chi_spec, chi_cat

# --- 🚨 СИМУЛАТОР НА СЦЕНАРИИ (SCENARIO LAB) ---
st.sidebar.header("🚨 Симулатор на Сценарии (Scenario Lab)")
st.sidebar.caption("Задействане на събития за тестване на ВХР:")

sc_col1, sc_col2 = st.sidebar.columns(2)
with sc_col1:
    if st.button("🌊 Солеви шок"): st.session_state.scenario = "Солеви шок"
    if st.button("📉 Срив на pH"): st.session_state.scenario = "Срив на pH"
with sc_col2:
    if st.button("💨 O2 Пик"): st.session_state.scenario = "O2 Пик"
    if st.button("⚛️ Теч в ПГ-2"): st.session_state.scenario = "Теч в ПГ-2"

if st.sidebar.button("🔄 Нулирай Сценариите"):
    st.session_state.scenario = "Нормален режим"
    st.session_state.dosed_nh3 = False
    st.session_state.dosed_n2h4 = False

st.sidebar.info(f"Режим: **{st.session_state.scenario}**")

# --- 🎛️ КОНТРОЛЕН ПАНЕЛ ---
st.sidebar.header("🎛️ Настройки на ВХР")

base_ph_25 = 8.60 if st.session_state.scenario == "Срив на pH" else 9.40
base_o2 = 35.0 if st.session_state.scenario == "O2 Пик" else 3.0
base_cond = 2.80 if st.session_state.scenario == "Солеви шок" else 0.10
base_n16_pg2 = 320.0 if st.session_state.scenario == "Теч в ПГ-2" else 5.0

st.sidebar.subheader("🔵 1-ви Контур & СВО")
temp_1st = st.sidebar.number_input("Температура 1-ви контур (°C)", 200.0, 350.0, 301.0, step=1.0)
ph_1st_25 = st.sidebar.slider("pH (25°C) 1-ви контур", 6.0, 8.5, 7.10, step=0.05)
boron = st.sidebar.slider("Борна киселина H3BO3 (g/kg)", 0.0, 12.0, 4.2)

st.sidebar.subheader("🌀 4-те Примки (ПГ-1..4)")
n16_pg1 = st.sidebar.slider("N-16 Активност ПГ-1 (Bq/l)", 0.0, 500.0, 5.0)
n16_pg2 = st.sidebar.slider("N-16 Активност ПГ-2 (Bq/l)", 0.0, 500.0, base_n16_pg2)
n16_pg3 = st.sidebar.slider("N-16 Активност ПГ-3 (Bq/l)", 0.0, 500.0, 5.0)
n16_pg4 = st.sidebar.slider("N-16 Активност ПГ-4 (Bq/l)", 0.0, 500.0, 5.0)

st.sidebar.subheader("🔴 2-ри Контур & Деаерация")
ph_feed_25 = st.sidebar.slider("pH (25°C) Питателна вода", 8.0, 10.2, base_ph_25, step=0.05)
o2_deaerator = st.sidebar.slider("Разтворен O2 след Деаератор (ppb)", 0.0, 50.0, base_o2)
cond_base_val = st.sidebar.slider("Соленост Кондензатор (µS/cm)", 0.05, 5.0, base_cond, step=0.05)
temp_pvd = st.sidebar.slider("Температура ПВД (°C)", 150.0, 260.0, 225.0)

time_horizon = st.sidebar.radio("Прогнозен хоризонт:", ["Сега (0h)", "+1 час", "+6 часа", "+24 часа"])

# --- ДИНАМИЧЕН ХИМИЧЕН БАЛАНС ---
calculated_ph_25 = ph_feed_25
if st.session_state.dosed_nh3 and time_horizon != "Сега (0h)":
    calculated_ph_25 += 0.80

calculated_o2 = o2_deaerator
if st.session_state.dosed_n2h4 and time_horizon != "Сега (0h)":
    calculated_o2 = max(0.5, calculated_o2 - 30.0)

ph_t_1st = calc_ph_temp(ph_1st_25, temp_1st)
ph_t_2nd = calc_ph_temp(calculated_ph_25, temp_pvd)
orp_2nd = calc_orp(calculated_o2, temp_pvd)
chi_spec, chi_cat = calc_conductivities(calculated_ph_25, cond_base_val, calculated_o2)

# --- ПРОВЕРКА ЗА АЗ-1 ---
reactor_trip = temp_1st > 335.0 or ph_1st_25 < 6.2 or ph_1st_25 > 7.8

if reactor_trip:
    st.error("🚨 **АВАРИЙНА ЗАЩИТА АЗ-1 СРАБОТИ!** Реакторът е изключен поради превишени физически граници.")
else:
    leak_pg1 = (n16_pg1 / 500.0) * 15.0
    leak_pg2 = (n16_pg2 / 500.0) * 15.0
    leak_pg3 = (n16_pg3 / 500.0) * 15.0
    leak_pg4 = (n16_pg4 / 500.0) * 15.0

    # --- 🗺️ ТЕХНОЛОГИЧНА КАРТА НА ВВЕР-1000 ---
    st.subheader("🗺️ Технологична карта: ВВЕР-1000 с Подробен Втори Контур")
    fig_map = go.Figure()
    fig_map.add_trace(go.Scatter(x=[2, 2], y=[2, 5], mode='lines', line=dict(color='blue', width=6), name='Реактор-ГЦТ'))
    fig_map.add_trace(go.Scatter(x=[2, 0.8, 0.8, 2], y=[3.5, 4.5, 5.2, 4.2], mode='lines', line=dict(color='blue', width=2), name='Примка 1'))
    fig_map.add_trace(go.Scatter(x=[2, 0.8, 0.8, 2], y=[3.5, 2.5, 1.8, 2.8], mode='lines', line=dict(color='blue', width=2), name='Примка 2'))
    fig_map.add_trace(go.Scatter(x=[2, 3.2, 3.2, 2], y=[3.5, 4.5, 5.2, 4.2], mode='lines', line=dict(color='blue', width=2), name='Примка 3'))
    fig_map.add_trace(go.Scatter(x=[2, 3.2, 3.2, 2], y=[3.5, 2.5, 1.8, 2.8], mode='lines', line=dict(color='blue', width=2), name='Примка 4'))

    fig_map.add_trace(go.Scatter(x=[3.2, 5.0, 6.5, 6.5, 5.5, 4.5, 4.0, 3.2], 
                                 y=[5.2, 5.2, 4.0, 1.0, 1.0, 1.0, 2.5, 2.8], 
                                 mode='lines', line=dict(color='red', width=3, dash='dash'), name='2-ри Контур'))

    fig_map.add_trace(go.Scatter(x=[2], y=[3.5], mode='markers+text', marker=dict(size=30, color='green'), text=["Реактор ВВЕР"], textposition="top center"))
    fig_map.add_trace(go.Scatter(x=[0.8], y=[5.2], mode='markers+text', marker=dict(size=18, color='red' if leak_pg1 > 2.0 else 'green'), text=["ПГ-1"], textposition="middle left"))
    fig_map.add_trace(go.Scatter(x=[0.8], y=[1.8], mode='markers+text', marker=dict(size=18, color='red' if leak_pg2 > 2.0 else 'green'), text=["ПГ-2"], textposition="middle left"))
    fig_map.add_trace(go.Scatter(x=[3.2], y=[5.2], mode='markers+text', marker=dict(size=18, color='red' if leak_pg3 > 2.0 else 'green'), text=["ПГ-3"], textposition="middle right"))
    fig_map.add_trace(go.Scatter(x=[3.2], y=[1.8], mode='markers+text', marker=dict(size=18, color='red' if leak_pg4 > 2.0 else 'green'), text=["ПГ-4"], textposition="middle right"))

    fig_map.add_trace(go.Scatter(x=[5.0], y=[5.2], mode='markers+text', marker=dict(size=20, color='gray'), text=["ЦВД / СПП / ЦНД"], textposition="top center"))
    fig_map.add_trace(go.Scatter(x=[6.5], y=[1.0], mode='markers+text', marker=dict(size=20, color='red' if cond_base_val > 0.5 else 'green'), text=["Кондензатор & БОВ"], textposition="bottom center"))
    fig_map.add_trace(go.Scatter(x=[5.5], y=[1.0], mode='markers+text', marker=dict(size=16, color='green'), text=["ПНД-1..4"], textposition="top center"))
    fig_map.add_trace(go.Scatter(x=[4.5], y=[1.0], mode='markers+text', marker=dict(size=22, color='red' if calculated_o2 > 10.0 else 'green'), text=["Деаератор (6 atm)"], textposition="top center"))
    fig_map.add_trace(go.Scatter(x=[4.0], y=[2.5], mode='markers+text', marker=dict(size=18, color='green'), text=["ПЕН / ПВД-5,6,7"], textposition="middle right"))

    fig_map.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), height=400, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_map, use_container_width=True)

    # --- 🧪 ТАБЛО ЗА ТЕРМОДИНАМИКА И ЕЛЕКТРОХИМИЯ ---
    st.markdown("### 🧪 Термодинамичен & Електрохимичен Баланс")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("pH_T (1-ви контур 300°C)", f"{ph_t_1st:.2f}")
    with m2: st.metric(f"pH_T (ПВД {temp_pvd}°C)", f"{ph_t_2nd:.2f}")
    with m3: st.metric("ORP / Редокс (mV)", f"{orp_2nd:.1f} mV")
    with m4: st.metric("Специфична χ (µS/cm)", f"{chi_spec:.3f}")
    with m5: st.metric("Катионирана χ_cat", f"{chi_cat:.3f} µS/cm")

    # --- 🔍 SUB-VIEW ПРЕГЛЕД ---
    st.markdown("---")
    st.subheader("🔍 Детайлен инспекционен преглед на съоръжение (Sub-view)")
    
    selected_comp = st.selectbox(
        "Изберете съоръжение за подробна вътрешна ВХР диагноза:",
        ["Парогенератор ПГ-2 (Вторична страна)", "Блок Външна Очистка (БОВ) & Йонитни филтри", "Деаератор (6 atm)", "Кондензатор на турбината"]
    )

    if selected_comp == "Парогенератор ПГ-2 (Вторична страна)":
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            st.markdown("#### 🏭 Парогенератор ПГ-2 (ПГВ-1000M)")
            st.write(f"* **Текуща N-16 активност:** {n16_pg2:.1f} Bq/l")
            st.write(f"* **Изчислена утечка 1-ви->2-ри контур:** {leak_pg2:.2f} l/h")
        with c_sub2:
            st.progress(min(1.0, leak_pg2 / 10.0))
            if leak_pg2 > 2.0:
                st.error("⚠️ **ВНИМАНИЕ:** Утечката надвишава регламента! Вземете проба за радиоактивен йод.")
            else:
                st.success("✅ Тръбният сноп на ПГ-2 е херметичен.")

    elif selected_comp == "Блок Външна Очистка (БОВ) & Йонитни филтри":
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            st.markdown("#### 🧪 БОВ - Йонообменни Филтри")
            st.write(f"* **Катионирана проводимост:** {chi_cat:.3f} µS/cm")
        with c_sub2:
            resin_exhaust = min(100, int(cond_base_val * 30))
            st.write(f"**Износване на йонитната смола:** {resin_exhaust}%")
            st.progress(resin_exhaust / 100.0)

    elif selected_comp == "Деаератор (6 atm)":
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            st.markdown("#### ♨️ Деаераторна Колона")
            st.write(f"* **Изходен кислород:** {calculated_o2:.1f} ppb")
        with c_sub2:
            deaer_eff = max(0.0, 100.0 - (calculated_o2 * 2.0))
            st.write(f"**Ефективност на дегазация:** {deaer_eff:.1f}%")
            st.progress(deaer_eff / 100.0)

    elif selected_comp == "Кондензатор на турбината":
        c_sub1, c_sub2 = st.columns(2)
        with c_sub1:
            st.markdown("#### 💧 Кондензатор")
            st.write(f"* **Базова проводимост:** {cond_base_val:.2f} µS/cm")
        with c_sub2:
            if cond_base_val > 0.5:
                st.error("🚨 **ПРОБИВ В КОНДЕНЗАТОРА:** Навлизане на речна вода!")
            else:
                st.success("✅ Кондензаторът е херметичен.")

    # --- 📈 ТОЧКА 4: ГРАФИКИ ЗА ТРЕНДОВЕ ВЪВ ВРЕМЕТО ---
    st.markdown("---")
    st.subheader("📈 Динамичен Анализ на Трендовете (24-часова Прогноза)")
    
    hours = np.linspace(0, 24, 50)
    
    if st.session_state.scenario == "Срив на pH":
        trend_ph = np.maximum(8.0, calculated_ph_25 - (hours * 0.05))
    else:
        trend_ph = np.full_like(hours, calculated_ph_25)

    if st.session_state.scenario == "O2 Пик":
        trend_o2 = calculated_o2 * np.exp(-hours * 0.1) if st.session_state.dosed_n2h4 else np.minimum(50.0, calculated_o2 + (hours * 0.5))
    else:
        trend_o2 = np.full_like(hours, calculated_o2)

    tr_col1, tr_col2 = st.columns(2)
    
    with tr_col1:
        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(x=hours, y=trend_ph, mode='lines', name='pH (25°C)', line=dict(color='green' if calculated_ph_25>=9.2 else 'red', width=3)))
        fig_ph.add_hline(y=9.2, line_dash="dash", line_color="orange", annotation_text="Минимум регламент (9.2)")
        fig_ph.update_layout(title="Динамика на pH във времето (ч)", xaxis_title="Време (часове)", yaxis_title="pH", height=300)
        st.plotly_chart(fig_ph, use_container_width=True)

    with tr_col2:
        fig_o2 = go.Figure()
        fig_o2.add_trace(go.Scatter(x=hours, y=trend_o2, mode='lines', name='O2 (ppb)', line=dict(color='blue' if calculated_o2<=10.0 else 'red', width=3)))
        fig_o2.add_hline(y=10.0, line_dash="dash", line_color="red", annotation_text="Максимум регламент (10 ppb)")
        fig_o2.update_layout(title="Тренд на Разтворен Кислород O2 (ppb)", xaxis_title="Време (часове)", yaxis_title="O2 (ppb)", height=300)
        st.plotly_chart(fig_o2, use_container_width=True)

    # --- 💡 ЕКСПЕРТЕН АНАЛИЗ И ДОЗИРАНЕ ---
    st.markdown("---")
    col_d, col_a = st.columns([1.2, 1])

    with col_d:
        st.subheader("💡 Системен Експертен Анализ")
        if leak_pg2 > 2.0:
            st.error("🚨 **АВАРИЯ [ТЕЧ В ПГ-2]:** Повишена радиоактивност във втори контур!")
        elif cond_base_val > 0.5:
            st.error("🚨 **АВАРИЯ [СОЛЕВИ ШОК]:** Пробив на охлаждаща вода в Кондензатора!")
        elif calculated_ph_25 < 9.2:
            st.warning("⚠️ **ОПАСНОСТ [СРИВ НА pH]:** Риск от ерозия-корозия (FAC).")
        elif calculated_o2 > 10.0:
            st.warning("⚠️ **ОПАСНОСТ [O2 ПИК]:** Кислородна питинг корозия.")
        else:
            st.success("✅ **НОРМАЛЕН РЕЖИМ:** Всички параметри са в регламент.")

    with col_a:
        st.subheader("🧪 Корeгиращи Действия")
        if calculated_ph_25 < 9.2 and not st.session_state.dosed_nh3:
            if st.button("💉 Дозирай Амоняк (Нормализирай pH)"):
                st.session_state.dosed_nh3 = True
                st.rerun()
        elif st.session_state.dosed_nh3:
            st.success("✅ **Амонякът е дозиран!** pH е възстановено.")

        if calculated_o2 > 10.0 and not st.session_state.dosed_n2h4:
            if st.button("💉 Дозирай Хидразин-хидрат (Свържи O2)"):
                st.session_state.dosed_n2h4 = True
                st.rerun()
        elif st.session_state.dosed_n2h4:
            st.success("✅ **Хидразинът е дозиран!** $O_2$ е неутрализиран.")
