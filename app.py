import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math
from datetime import datetime

# ---------------------------------------------------------
# 🎨 Конфигурация на страницата & Персонализиран CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Дигитален Двойник ВХР & Турбоагрегат — Блок 5, АЕЦ Козлодуй",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔥 Уникален CSS за Glassmorphism интерфейс
st.markdown("""
<style>
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 18px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        margin-bottom: 15px;
    }
    .status-ok { border-left: 6px solid #2ecc71 !important; }
    .status-warn { border-left: 6px solid #f1c40f !important; }
    .status-alert { border-left: 6px solid #e74c3c !important; }
    
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚛️ Интерактивен Дигитален Двойник — Блок 5, АЕЦ Козлодуй")
st.caption("Пълен софтуерен комплекс: Първи контур (ВВЕР-1000) | Втори контур | Турбоагрегат К-1000-60/1500 | Химико-механичен анализ")

# ---------------------------------------------------------
# 🔄 Инициализация на сесийни променливи (Модул 1)
# ---------------------------------------------------------
default_state = {
    'temp_val': 301.0,
    'h3bo3_val': 3.5,
    'k_val': 12.0,
    'nh3_val': 18.0,
    'h2_val': 45.0,
    'o2_reactor': 0.0,
    'flow_gcp': 84000.0,
    'na_sg': 2.0,
    'cl_sg': 3.0,
    'o2_sg': 1.0,
    'eta_val': 1.8,
    'leak_val': 0.0,
    # Нови параметри за Турбината:
    'turbine_mw': 1000.0,
    'cond_vac_bar': 0.05,
    'rpm_val': 1500,
    'brot_val': 0.0
}

for key, val in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = val

def apply_auto_fix():
    for key, val in default_state.items():
        st.session_state[key] = val

# 🕹️ Главно меню
st.sidebar.title("🕹️ Модули на системата")
module = st.sidebar.radio(
    "Преминаване към:",
    [
        "1. Оперативен Мониторинг & Турбоагрегат (Блок 5)",
        "2. Лаборатория: Корозия, Питинг & Оразмеряване на съоръжения"
    ]
)

# ==========================================================
# МОДУЛ 1: ОПЕРАТИВЕН МОНИТОРИНГ, ВХР И ТУРБИНЕН ОСТРОВ
# ==========================================================
if module == "1. Оперативен Мониторинг & Турбоагрегат (Блок 5)":
    st.header("📊 Модул 1: Оперативен мониторинг на 1-ви, 2-ри контур и Турбоагрегат")
    st.caption("Мониторинг на ВХР, пароводния тракт и енергийния баланс в реално време")

    # 🎛️ НАСТРОЙКИ ПО СЪОРЪЖЕНИЯ В СТРАНИЧНОТО МЕНЮ
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Управление по съоръжения")
    
    selected_facility = st.sidebar.selectbox(
        "Избери съоръжение за контрол:",
        [
            "🔥 Реактор ВВЕР-1000 (Активна зона)",
            "🌀 Главни Циркулационни Помпи (ГЦП & ГЦТ)",
            "💨 Парогенератори ПГВ-1000 (Втори контур)",
            "⚡ Турбина К-1000-60/1500 & Турбогенератор",
            "💧 Кондензатор, БОУ & ЕТА дозиране"
        ]
    )

    if selected_facility == "🔥 Реактор ВВЕР-1000 (Активна зона)":
        st.sidebar.markdown("#### 🔥 Параметри на Реактора")
        st.sidebar.slider("Работна температура Т1 (°C)", 280.0, 325.0, key="temp_val", step=0.5)
        st.sidebar.slider("Борна киселина H3BO3 (g/kg)", 0.0, 10.0, key="h3bo3_val", step=0.1)
        st.sidebar.slider("Калиев йон K+ (mg/dm³)", 0.0, 20.0, key="k_val", step=0.5)
        st.sidebar.slider("Амоняк NH3 (mg/dm³)", 0.0, 30.0, key="nh3_val", step=1.0)
        st.sidebar.slider("Разтворен Водород H2 (Ncm³/kg)", 0.0, 150.0, key="h2_val", step=1.0)
        st.sidebar.slider("Кислород O2 в Реактора (ppb)", 0.0, 50.0, key="o2_reactor", step=1.0)

    elif selected_facility == "🌀 Главни Циркулационни Помпи (ГЦП & ГЦТ)":
        st.sidebar.markdown("#### 🌀 Параметри на ГЦП / ГЦТ")
        st.sidebar.slider("Общ дебит на ГЦП Q (m³/h)", 0.0, 90000.0, key="flow_gcp", step=1000.0)
        st.sidebar.info("Номинален дебит за 4 помпи ГЦН-195М: ~84,000 m³/h при P = 15.7 MPa.")

    elif selected_facility == "💨 Парогенератори ПГВ-1000 (Втори контур)":
        st.sidebar.markdown("#### 💨 Параметри на Парогенераторите")
        st.sidebar.slider("Натриеви йони Na+ (ppb)", 0.0, 50.0, key="na_sg", step=0.5)
        st.sidebar.slider("Хлориди Cl- (ppb)", 0.0, 50.0, key="cl_sg", step=0.5)
        st.sidebar.slider("Разтворен O2 в продухването (ppb)", 0.0, 20.0, key="o2_sg", step=0.5)

    elif selected_facility == "⚡ Турбина К-1000-60/1500 & Турбогенератор":
        st.sidebar.markdown("#### ⚡ Параметри на Турбината")
        st.sidebar.slider("Електрическа мощност N (MW)", 0.0, 1040.0, key="turbine_mw", step=10.0)
        st.sidebar.slider("Налягане в кондензатора (bar)", 0.03, 0.25, key="cond_vac_bar", step=0.01)
        st.sidebar.slider("Обороти на ротора (rpm)", 0, 1500, key="rpm_val", step=10)
        st.sidebar.slider("Паропрепускане към БРУ-К (t/h)", 0.0, 3000.0, key="brot_val", step=50.0)

    elif selected_facility == "💧 Кондензатор, БОУ & ЕТА дозиране":
        st.sidebar.markdown("#### 💧 Параметри на Кондензатора & БОУ")
        st.sidebar.slider("Дозиране на ЕТА (mg/dm³)", 0.0, 5.0, key="eta_val", step=0.1)
        st.sidebar.slider("Приток на охладителна вода (L/h)", 0.0, 10.0, key="leak_val", step=0.1)

    # 🧮 ТЕХНОЛОГИЧНИ ПРЕСМЯТАНИЯ
    ph_25_p1 = 7.0 + 0.12 * st.session_state.k_val - 0.08 * st.session_state.h3bo3_val
    ph_t_p1 = ph_25_p1 - (st.session_state.temp_val - 25.0) * 0.0072
    effective_o2 = max(0.0, st.session_state.o2_reactor - (st.session_state.h2_val / 10.0))
    conductivity = 0.8 + 0.45 * st.session_state.k_val + 0.15 * st.session_state.nh3_val

    is_emergency_scram = st.session_state.h2_val > 100.0 or st.session_state.flow_gcp < 40000.0
    has_condenser_leak = st.session_state.leak_val > 0.2
    has_sg_impurity = st.session_state.na_sg > 5.0 or st.session_state.cl_sg > 5.0 or st.session_state.o2_sg > 5.0
    has_ph_anomaly = ph_t_p1 < 7.00 or ph_t_p1 > 7.30
    has_vacuum_drop = st.session_state.cond_vac_bar > 0.12
    is_turbine_trip = st.session_state.rpm_val < 1450 or st.session_state.turbine_mw == 0.0

    # --- 1. ТЕХНОЛОГИЧЕН ДАШБОРД НА СЪОРЪЖЕНИЯТА (5 КАРТИ) ---
    st.subheader("🏭 Технологична схема: 1-ви контур ➔ Втори контур ➔ Турбоагрегат К-1000-60/1500")
    
    st1 = "🔴 АВАРИЯ / ААЗ" if is_emergency_scram else ("🟡 ВНИМАНИЕ" if effective_o2 > 5.0 or has_ph_anomaly else "🟢 НОРМА")
    st2 = "🔴 ИЗКЛЮЧЕНИ ПОМПИ" if st.session_state.flow_gcp < 40000.0 else "🟢 НОРМА (4/4 ГЦП)"
    st3 = "🔴 ЗАМЪРСЯВАНЕ В ПГ" if has_sg_impurity else "🟢 НОРМА"
    st4 = "🔴 СРИВ НА ВАКУУМА / ТРИП" if (has_vacuum_drop or is_turbine_trip) else "🟢 НОРМА (1500 rpm)"
    st5 = "🔴 ПРОБИВ В КОНДЕНЗАТОРА" if has_condenser_leak else "🟢 НОРМА"

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.info(f"**🔥 Реактор ВВЕР-1000**\n\nСтатус: **{st1}**\n\nТ: `{st.session_state.temp_val}°C` | $pH_T$: `{ph_t_p1:.2f}`\n\n$H_2$: `{st.session_state.h2_val} Ncm³/kg`")
    with c2:
        st.info(f"**🌀 ГЦП & ГЦТ**\n\nСтатус: **{st2}**\n\nДебит: `{st.session_state.flow_gcp:.0f} m³/h`\n\nНалягане: `15.7 MPa`")
    with c3:
        st.info(f"**💨 Парогенератори (4x)**\n\nСтатус: **{st3}**\n\nПара: `6.27 MPa / 278°C`\n\n$Na^+$: `{st.session_state.na_sg} ppb`")
    with c4:
        st.info(f"**⚡ Турбина К-1000**\n\nСтатус: **{st4}**\n\nМощност: `{st.session_state.turbine_mw:.0f} MW`\n\nОбороти: `{st.session_state.rpm_val} rpm`")
    with c5:
        st.info(f"**💧 Кондензатор & БОУ**\n\nСтатус: **{st5}**\n\nВакуум: `{st.session_state.cond_vac_bar:.2f} bar`\n\nПриток: `{st.session_state.leak_val} L/h`")

    st.markdown("---")

    # --- 2. ДИНАМИЧНО СЪОБЩЕНИЕ И ПРЕПОРЪКА КЪМ ОПЕРАТОРА (ALERT BOX) ---
    st.subheader("🚨 Оперативна диагностика & Препоръка към оператора")
    
    has_any_issue = is_emergency_scram or has_condenser_leak or has_sg_impurity or has_ph_anomaly or has_vacuum_drop or is_turbine_trip

    if has_any_issue:
        st.error("⚠️ РЕГИСТРИРАНО ОТКЛОНЕНИЕ ИЛИ АВАРИЕН РЕЖИМ В БЛОКА!")
        
        if is_emergency_scram:
            st.critical("💥 **КРИТИЧЕН АВАРИЕН РЕЖИМ — СРАБОТВАНЕ НА АВАРИЙНАТА ЗАЩИТА (ААЗ)!**")
            st.markdown("""
            * **Къде:** Първи контур / Активна зона и ГЦТ.
            * **Какво:** Повишаване на водорода ($H_2 > 100\\text{ Ncm}^3/\\text{kg}$) или срив в дебита ($Q < 40,000\\text{ m}^3/\\text{h}$).
            * **Препоръка:** Незабавно въвеждане на ААЗ, задействане на СВО-1 и продухване на капака на реактора!
            """)
        elif has_vacuum_drop:
            st.warning("⚠️ **ВЛОШАВАНЕ НА ВАКУУМА В ОХЛАДИТЕЛНИЯ КОНДЕНЗАТОР НА ТУРБИНАТА!**")
            st.markdown(f"""
            * **Къде:** Турбинен остров / Цилиндри Ниско Налягане (ЦНН) & Кондензатор.
            * **Какво:** Налягането в кондензатора скочи на `{st.session_state.cond_vac_bar:.2f} bar` (Норма: ~0.04 - 0.06 bar).
            * **Защо:** Риск от прегряване и вибрации в последните степенни лопатки на ЦНН.
            * **Препоръка:** Включете резервната ежекционна група, проверете притока на охладителна речна вода и подгответе сработване на БРУ-К!
            """)
        elif is_turbine_trip:
            st.warning("⚠️ **ИЗКЛЮЧВАНЕ НА ТУРБОГЕНЕРАТОРА (TURBINE TRIP)!**")
            st.markdown(f"""
            * **Къде:** Главна прекъсвателна арматура / Генератор.
            * **Какво:** Оборотите на турбината спаднаха под 1450 rpm или електрическият товар е 0 MW.
            * **Препоръка:** Пренасочете парата от Парогенераторите през БРУ-К към кондензатора или през БРУ-А към атмосферата. Разтоварване на реактора до 30% N_ном!
            """)
        elif has_condenser_leak:
            st.warning("⚠️ **ОТКРИТ ПРОБИВ В ОХЛАДИТЕЛНИЯ КОНДЕНЗАТОР!**")
            st.markdown(f"""
            * **Къде:** Втори контур / Кондензатор на турбината.
            * **Какво:** Постъпване на сурова охладителна вода ({st.session_state.leak_val} L/h).
            * **Препоръка:** Включване на блоковата обезсолителна инсталация (БОУ) на 100% и локализиране на пробития тръбен сноп.
            """)
        elif has_sg_impurity:
            st.warning("⚠️ **ВЛОШЕНО КАЧЕСТВО НА ВОДАТА В ПАРОГЕНЕРАТОРИТЕ!**")
            st.markdown(f"""
            * **Къде:** Втори контур / Парогенератори ПГВ-1000.
            * **Какво:** Повишена концентрация на примеси ($Na^+$, $Cl^-$ или $O_2 > 5\\text{ ppb}$).
            * **Препоръка:** Увеличаване на непрекъснатото продухване на Парогенераторите и оптимизиране на дозирането на ЕТА.
            """)
        elif has_ph_anomaly:
            st.warning("⚠️ **ОТКЛОНЕНИЕ В pH_T НА ПЪРВИ КОНТУР!**")
            st.markdown(f"""
            * **Къде:** Първи контур / Реактор.
            * **Какво:** $pH_T = {ph_t_p1:.2f}$ е извън оптималния прозорец (7.00 - 7.30).
            * **Препоръка:** Коригирайте дозирането на калиева основа ($K^+$) спрямо текущата концентрация на борна киселина.
            """)

        st.button("🤖 Автоматично възстановяване на оптимален ВХР & Турбинен режим (Auto-Fix)", on_click=apply_auto_fix)
    else:
        st.success("✅ Всички химически, хидродинамични и турбинни параметри са в **ОПТИМАЛЕН ЗЕЛЕН СТАТУС**. Блок 5 генерира 1000 MW чиста енергия!")

    st.markdown("---")

    # --- 3. РАЗШИРЕН ХИМИЧЕСКИ И ТУРБИНЕН КОНТРОЛ ---
    st.subheader("🔬 Разширен контрол по контури и Турбоагрегат")

    chem_data = [
        {"Контур / Съоръжение": "Първи контур (Реактор)", "Параметър": "pH_T (работна T)", "Измерена стойност": f"{ph_t_p1:.2f}", "Норма": "7.00 - 7.30", "Статус": "⚠️ Отклонение" if has_ph_anomaly else "✅ В норма"},
        {"Контур / Съоръжение": "Първи контур (Реактор)", "Параметър": "Разтворен H2", "Измерена стойност": f"{st.session_state.h2_val:.1f} Ncm³/kg", "Норма": "30 - 60 Ncm³/kg", "Статус": "🚨 Критично!" if st.session_state.h2_val > 100 else "✅ В норма"},
        {"Контур / Съоръжение": "Втори контур (Парогенератор)", "Параметър": "Пара на изхода (P / T)", "Измерена стойност": "6.27 MPa / 278°C", "Норма": "6.27 MPa / 278°C", "Статус": "✅ В норма"},
        {"Контур / Съоръжение": "Турбина К-1000-60/1500", "Параметър": "Електрическа мощност", "Измерена стойност": f"{st.session_state.turbine_mw:.0f} MW", "Норма": "1000 MW", "Статус": "⚠️ Изключена" if is_turbine_trip else "✅ В норма"},
        {"Контур / Съоръжение": "Турбина К-1000-60/1500", "Параметър": "Налягане в Кондензатора", "Измерена стойност": f"{st.session_state.cond_vac_bar:.2f} bar", "Норма": "0.04 - 0.06 bar", "Статус": "🚨 Срив на вакуума" if has_vacuum_drop else "✅ В норма"},
        {"Контур / Съоръжение": "Втори контур (Кондензатор)", "Параметър": "Дозиране ЕТА", "Измерена стойност": f"{st.session_state.eta_val:.1f} mg/dm³", "Норма": "1.0 - 3.0 mg/dm³", "Статус": "✅ В норма"}
    ]
    st.dataframe(pd.DataFrame(chem_data), use_container_width=True)

    st.markdown("---")

    # --- 4. ИНТЕРАКТИВНИ ГРАФИКИ: БОРНО-КАЛИЕВА КАРТА & ТУРБИНЕН ЕНЕРГИЕН ТРЕНД ---
    st.subheader("📈 Графичен анализ: Регламентна Борно-Калиева Карта & Мощност на Турбината")
    
    tab_graph1, tab_graph2 = st.tabs(["🗺️ Борно-Калиева Регламентна Карта (1-ви Контур)", "⚡ 24h Генерация & Вакуум в Турбината"])

    with tab_graph1:
        h3bo3_axis = np.linspace(0.1, 10.0, 50)
        k_opt_min = 2.0 + 1.2 * h3bo3_axis
        k_opt_max = 5.0 + 1.6 * h3bo3_axis

        fig_map = go.Figure()
        fig_map.add_trace(go.Scatter(x=h3bo3_axis, y=k_opt_max, mode='lines', name='Верхен праг K+', line=dict(color='#e67e22', width=1)))
        fig_map.add_trace(go.Scatter(x=h3bo3_axis, y=k_opt_min, mode='lines', name='Нижен праг K+', fill='tonexty', fillcolor='rgba(46, 204, 113, 0.2)', line=dict(color='#27ae60', width=1)))
        
        fig_map.add_trace(go.Scatter(
            x=[st.session_state.h3bo3_val], y=[st.session_state.k_val],
            mode='markers+text',
            name='Текущо състояние',
            text=['📍 Блок 5'],
            textposition="top center",
            marker=dict(size=16, color='#c0392b' if has_ph_anomaly else '#2980b9', symbol='diamond-open-dot', line=dict(width=3))
        ))
        
        fig_map.update_layout(
            title="Борно-Калиев График — Оптимална зона за пасивация на конструкционните стомани",
            xaxis_title="Концентрация на Борна киселина H3BO3 (g/kg)",
            yaxis_title="Концентрация на Калиев йон K+ (mg/dm³)",
            height=380,
            plot_bgcolor="#fdfdfd"
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with tab_graph2:
        hours = [f"{h:02d}:00" for h in range(24)]
        mw_trend = list(1000 + 10 * np.sin(np.linspace(0, 4, 23))) + [st.session_state.turbine_mw]

        fig_turb = go.Figure()
        fig_turb.add_trace(go.Scatter(x=hours, y=mw_trend, mode='lines+markers', name='Електрическа мощност (MW)', line=dict(color='#f39c12', width=3)))
        fig_turb.update_layout(
            title="Денонощна графика на бруто електрическата мощност на Турбоагрегата",
            xaxis_title="Време (Часове)",
            yaxis_title="Мощност (MW)",
            yaxis=dict(range=[0, 1100]),
            height=380,
            plot_bgcolor="#fdfdfd"
        )
        st.plotly_chart(fig_turb, use_container_width=True)

    # Оперативен дневник
    with st.expander("📜 Оперативен хронологичен журнал на системата (Log)"):
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        st.code(f"""
[{now_str}] INFO: Дигитален Двойник на Блок 5 функционира нормално.
[{now_str}] FACILITY: Избрано съоръжение -> {selected_facility}
[{now_str}] TURBINE: N = {st.session_state.turbine_mw:.0f} MW | RPM = {st.session_state.rpm_val} rpm | P_cond = {st.session_state.cond_vac_bar:.2f} bar
[{now_str}] PRIMARY: H3BO3 = {st.session_state.h3bo3_val:.2f} g/kg | K+ = {st.session_state.k_val:.1f} mg/dm3 | pH_T = {ph_t_p1:.2f}
[{now_str}] STATUS: {"ОТКЛОНЕНИЕ / АВАРИЕН РЕЖИМ!" if has_any_issue else "НОРМАЛНА ЕКСПЛОАТАЦИЯ (1000 MW)"}
        """, language="bash")


# ==========================================================
# МОДУЛ 2: ЛАБОРАТОРИЯ, НАЛЯГАНЕ & ОРАЗМЕРЯВАНЕ (НАПЪЛНО ЗАПАЗЕН)
# ==========================================================
elif module == "2. Лаборатория: Корозия, Питинг & Оразмеряване на съоръжения":
    st.header("🔬 Модул 2: Хидродинамика, Корозия, Питинг & Оразмеряване")
    st.caption("Комплексен химико-механичен симулатор за оборудване и тръбопроводи в АЕЦ ВВЕР-1000")

    metal_info_db = {
        "Конструкционна стомана 10ГН2МФА (Главни циркулационни тръбопроводи - ГЦТ)": {
            "type": "Перлитна нисколегирана стомана",
            "comp": "C: 0.08–0.12%, Mn: 0.8–1.1%, Ni: 1.8–2.3%, Mo: 0.4–0.6%, V: 0.08–0.12%",
            "sigma_dov": 185.0,
            "ph_range": "6.8 – 7.4 (при 300°C)",
            "temp_range": "290°C – 325°C",
            "p_range": "15.7 MPa (157 bar)",
            "vhr_type": "Борно-калиев амонячен ВХР с редуциращи условия (H2)",
            "desc": "Основен материал за Главния циркулационен тръбопровод (ГЦТ Du850) при ВВЕР-1000. Отличава се с висока якост и устойчивост на циклично натоварване. Задължително с вътрешен антикорозионен наплав."
        },
        "Корпусна стомана 15Х2МФА / 15Х2НМФА (Корпус на Реактора & Компенсатор)": {
            "type": "Високоякостна хромо-молибден-ванадиева корпусна стомана",
            "comp": "Cr: 2.0–2.5%, Mo: 0.6–0.8%, V: 0.25–0.35%, Ni: 0.6–0.8%",
            "sigma_dov": 195.0,
            "ph_range": "6.8 – 7.3 (при 300°C)",
            "temp_range": "280°C – 350°C",
            "p_range": "15.7 – 17.8 MPa (157–178 bar)",
            "vhr_type": "Борно-калиев амонячен ВХР (Първи контур)",
            "desc": "Използва се за изработване на корпуса на реактора ВВЕР-1000, компенсатора на налягането и съдовете под налягане. Има висока съпротивителна способност срещу радиационно охрупване."
        },
        "Аустенитна стомана 08Х18Н10Т (Първи контур / Тръби Парогенератор)": {
            "type": "Неръждаема аустенитна стомана, стабилизирана с Титан",
            "comp": "Cr: 17–19%, Ni: 9–11%, Ti: 5xС–0.8%, C ≤ 0.08%",
            "sigma_dov": 137.0,
            "ph_range": "6.8 – 7.4 (Първи контур) / 8.8 – 9.6 (Втори контур)",
            "temp_range": "280°C – 325°C",
            "p_range": "6.4 – 15.7 MPa (64–157 bar)",
            "vhr_type": "Универсален (Първи контур / Тръбен сноп на ПГВ-1000)",
            "desc": "Стандартен материал за топлообменните тръбички на парогенераторите (ПГВ-1000) и вътрешнокорпусните устройства (ВКУ). Притежава отлична обща корозионна устойчивост."
        },
        "Аустенитна стомана 12Х18Н10Т (Спомагателни системи & Колектори)": {
            "type": "Класическа неръждаема аустенитна стомана",
            "comp": "Cr: 17–19%, Ni: 9–11%, Ti: 0.4–0.8%, C ≤ 0.12%",
            "sigma_dov": 137.0,
            "ph_range": "6.0 – 9.5",
            "temp_range": "20°C – 300°C",
            "p_range": "1.0 – 16.0 MPa",
            "vhr_type": "Спомагателни системи (СВО-1, СВО-2, Борно регулиране)",
            "desc": "Материал за спомагателни тръбопроводи на първи контур, колектори на парогенератори и системи за пречистване на топлоносителя."
        },
        "Антикорозионен наплав 04Х20Н10Г2Б (Вътрешна защита на ГЦТ)": {
            "type": "Аустенитен двуслоен антикорозионен наплав",
            "comp": "Cr: 19–21%, Ni: 9–11%, Mn: 1.5–2.5%, Nb: 0.7–1.0%",
            "sigma_dov": 145.0,
            "ph_range": "7.0 – 7.3 (при 300°C)",
            "temp_range": "До 325°C",
            "p_range": "15.7 MPa (157 bar)",
            "vhr_type": "Защитен слой при борно-калиев ВХР",
            "desc": "Нанася се отвътре върху тръбопроводите от стомана 10ГН2МФА и корпуса на реактора за изолиране на въглеродната стомана от контакт с агресивната борна киселина."
        },
        "Въглеродна стомана 20К / 16ГС (Втори контур / Паропроводи)": {
            "type": "Котелна въглеродна / нисколегирана стомана",
            "comp": "C: 0.16–0.24%, Mn: 0.35–0.65%, Si: 0.15–0.30%",
            "sigma_dov": 115.0,
            "ph_range": "9.2 – 9.8 (при 25°C - Втори контур)",
            "temp_range": "180°C – 280°C",
            "p_range": "6.4 MPa (64 bar)",
            "vhr_type": "Амонячно-етаноламинов (ETA) / Аминов ВХР",
            "desc": "Прилага се във Втори контур за главните паропроводи, захранващите тръбопроводи и сепараторите-прегреватели. Чувствителна към ерозионно-корозионно износване (FAC)."
        },
        "Високоякостна стомана 25Х1МФ / 38ХН3МФА (Главни шпилки)": {
            "type": "Високоякостна конструкционна стомана за крепеж",
            "comp": "Cr: 1.3–1.7%, Mo: 0.25–0.35%, V: 0.15–0.25%",
            "sigma_dov": 210.0,
            "ph_range": "Суха атмосфера / Защитна среда",
            "temp_range": "20°C – 320°C",
            "p_range": "Високи механични опънни напрежения",
            "vhr_type": "Не е в пряк контакт с топлоносителя (Външен уплътнителен възел)",
            "desc": "Използва се за главния уплътнителен разрез (шпилки M140) на реакторния корпус. Изпитва екстремни опънни напрежения."
        },
        "Циркониева сплав Э110 / Э635 (Обвивки на ТВЕЛ)": {
            "type": "Циркониево-ниобиева сплав (Zr-1%Nb)",
            "comp": "Zr: ~99%, Nb: 0.9–1.1%, Fe ≤ 0.05%",
            "sigma_dov": 95.0,
            "ph_range": "7.0 – 7.3 (при 300°C)",
            "temp_range": "300°C – 350°C",
            "p_range": "15.7 MPa (157 bar)",
            "vhr_type": "Строго контролиран Борно-Калиев ВХР (Без O2!)",
            "desc": "Конструкционен материал за обвивките на горивните елементи (ТВЕЛ) и касетите в активната зона. Има изключително малко сечение на поглъщане на неутрони."
        }
    }

    st.subheader("🧪 1. Избор на материал и физикохимична среда")
    
    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        equipment_type = st.selectbox(
            "Тип съоръжение / конструктивен елемент:",
            [
                "🚀 Тръбопровод (напр. Главна циркулационна контура ГЦТ, Паропровод)",
                "🧪 Цилиндричен съд под налягане (напр. Компенсатор на налягането, Парогенератор)"
            ]
        )
    with col_eq2:
        metal = st.selectbox(
            "Избор на сплав / стомана:",
            list(metal_info_db.keys())
        )

    selected_info = metal_info_db[metal]
    with st.expander(f"ℹ️ Подробна техническа & оперативна характеристика за: {metal}", expanded=True):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"**Тип сплав:** `{selected_info['type']}`")
            st.markdown(f"**Химически състав:** `{selected_info['comp']}`")
            st.markdown(f"**Допустимо напрежение $[\sigma]$:** `{selected_info['sigma_dov']} MPa` (при 300°C)")
            st.markdown(f"**Препоръчителен ВХР:** `{selected_info['vhr_type']}`")
        with col_m2:
            st.markdown(f"**Оптимален pH диапазон:** `{selected_info['ph_range']}`")
            st.markdown(f"**Работна температура (T):** `{selected_info['temp_range']}`")
            st.markdown(f"**Работно налягане (P):** `{selected_info['p_range']}`")
        st.caption(f"**Предназначение и особености:** {selected_info['desc']}")

    st.markdown("##### 🧪 Задаване на химическите агресори и работната среда")
    hc1, hc2, hc3, hc4 = st.columns(4)
    ph_val = hc1.slider("pH (при 25°C)", 4.0, 11.5, 9.2, 0.1)
    o2_conc = hc2.number_input("Разтворен O2 (ppb)", 0, 500, 5)
    cl_conc = hc3.number_input("Хлориди Cl- (ppb)", 0, 1000, 2)
    velocity = hc4.slider("Скорост на флуида v (m/s)", 0.0, 10.0, 2.0, 0.1)

    allowable_stress_db = {k: v["sigma_dov"] for k, v in metal_info_db.items()}

    st.markdown("---")
    st.subheader("📐 2. Геометрични параметри, налягане и ресурсен анализ")
    
    gc1, gc2, gc3 = st.columns(3)
    pressure_bar = gc1.slider("Работно налягане P (bar)", 1.0, 180.0, 157.0, 1.0)
    work_temp = gc2.slider("Работна температура T (°C)", 25.0, 350.0, 300.0, 5.0)
    years_service = gc3.slider("Проектен ресурс (Години):", 1, 60, 40)

    pressure_mpa = pressure_bar / 10.0

    if "Тръбопровод" in equipment_type:
        g_col1, g_col2 = st.columns(2)
        diameter_mm = g_col1.number_input("Вътрешен диаметър D_вн (mm)", min_value=10, max_value=2000, value=850)
        pipe_length_m = g_col2.number_input("Дължина на тръбопровода L (m)", min_value=1, max_value=500, value=50)
        vessel_volume_m3 = (np.pi * ((diameter_mm / 1000.0) ** 2) / 4) * pipe_length_m
    else:
        g_col1, g_col2 = st.columns(2)
        vessel_volume_m3 = g_col1.number_input("Желан вътрешен обем V (m³)", min_value=1.0, max_value=200.0, value=79.0)
        vessel_height_m = g_col2.number_input("Височина / Дължина на цилиндъра H (m)", min_value=1.0, max_value=30.0, value=12.0)
        diameter_mm = math.sqrt((4 * vessel_volume_m3) / (math.pi * vessel_height_m)) * 1000.0
        st.info(f"💡 За желан обем **{vessel_volume_m3:.1f} m³** и височина **{vessel_height_m:.1f} m**, изчисленият вътрешен диаметър е **D = {diameter_mm:.0f} mm**.")

    if velocity < 0.2:
        flow_factor = 1.0
    elif velocity <= 2.5:
        flow_factor = 1.0 + (velocity / 5.0) ** 0.5
    else:
        flow_factor = 1.0 + (velocity / 2.5) ** 1.6

    if "Въглеродна" in metal or "10ГН2МФА" in metal:
        base_rate = 0.02 * np.exp((work_temp - 100) / 110) * flow_factor
        if ph_val < 9.2:
            base_rate *= (9.2 / ph_val) ** 3.0
        elif ph_val > 10.2:
            base_rate *= (ph_val / 9.5) ** 1.8
        if o2_conc > 20:
            base_rate *= (1.0 + o2_conc / 20.0)

    elif "15Х2МФА" in metal or "шпилки" in metal:
        base_rate = 0.015 * np.exp((work_temp - 100) / 130) * (flow_factor ** 0.8)
        if "шпилки" in metal and (cl_conc > 20 or o2_conc > 15):
            base_rate *= 3.0
    elif "Аустенитна" in metal or "наплав" in metal:
        base_rate = 0.0008 * np.exp((work_temp - 100) / 210) * (flow_factor ** 0.3)
        if cl_conc > 30 or o2_conc > 10:
            base_rate *= (1.0 + (cl_conc / 25.0) * (o2_conc / 10.0) * 0.3)
    else:
        base_rate = 0.0007 * np.exp((work_temp - 200) / 105)

    sigma_dov = allowable_stress_db[metal]
    phi_weld = 1.0

    s_mech_cyl = (pressure_mpa * diameter_mm) / (2 * sigma_dov * phi_weld - pressure_mpa)
    s_mech_cyl = max(0.5, s_mech_cyl)

    s_mech_head = (pressure_mpa * diameter_mm) / (2 * sigma_dov * phi_weld - 0.5 * pressure_mpa)
    s_mech_head = max(0.5, s_mech_head)

    c_corrosion = base_rate * years_service

    k_pit_base = 15.0 if ("Аустенитна" in metal or "наплав" in metal) else 40.0
    h_pit_um = k_pit_base * (max(1.0, cl_conc)**0.5) * (max(1.0, o2_conc)**0.3) * (years_service**0.5) / 10.0
    h_pit_mm = h_pit_um / 1000.0

    c_fab = 1.0

    s_total_cyl = s_mech_cyl + c_corrosion + h_pit_mm + c_fab
    s_total_head = s_mech_head + c_corrosion + h_pit_mm + c_fab

    st.markdown("---")
    st.subheader("🎯 3. Симулация на Локална Питингова Корозия ($h_{pit}$ с времето)")
    st.info(
        r"""
        **🔍 Физикохимичен механизъм:**  
        При наличие на халогениди ($Cl^-$) и окислител ($O_2$), локалната питингова корозия се развива по **дифузионно-контролиран степенен закон**:
        $$h_{pit}(t) = K_{pit} \cdot (C_{Cl^-})^{0.5} \cdot (C_{O_2})^{0.3} \cdot t^{0.5} \quad [\mu m]$$
        """
    )

    time_array = np.linspace(0.1, years_service, 100)
    pit_depth_curve_um = k_pit_base * (max(1.0, cl_conc)**0.5) * (max(1.0, o2_conc)**0.3) * (time_array**0.5) / 10.0

    fig_pit = go.Figure()
    fig_pit.add_trace(go.Scatter(x=time_array, y=pit_depth_curve_um, mode='lines', name='h_pit (µm)', line=dict(color='#d35400', width=3)))
    fig_pit.update_layout(
        title=f"Развитие на питингова дълбочина h_pit за {metal}",
        xaxis_title="Време (Години)",
        yaxis_title="Дълбочина на питинга (µm)",
        height=320,
        plot_bgcolor="#ffffff"
    )
    st.plotly_chart(fig_pit, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 4. Инженерна спецификация и предписание")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Якостна дебелина (P)", f"{s_mech_cyl:.2f} mm", f"P = {pressure_bar} bar")
    r2.metric("Загуба от корозия (C_corr)", f"{c_corrosion:.2f} mm", f"За {years_service} години")
    r3.metric("Питинг дълбочина (h_pit)", f"{h_pit_um:.1f} µm", f"({h_pit_mm:.3f} mm)")
    r4.metric("МИН. ПРОЕКТНА ДЕБЕЛИНА", f"{math.ceil(s_total_cyl)} mm", "Номинален размер", delta_color="normal")

    if "Цилиндричен съд" in equipment_type:
        st.success(
            f"""
            💡 **Инженерно предписание за ЦИЛИНДРИЧЕН СЪД ({metal}):**  
            * **Обем на съда ($V$):** **{vessel_volume_m3:.1f} m³** | **Изчислен диаметър ($D$):** **{diameter_mm:.0f} mm**
            * **Дебелина на цилиндричната обечайка:** $S_{{cyl}} \\ge$ **{math.ceil(s_total_cyl)} mm**
            * **Дебелина на елиптичните дъна:** $S_{{head}} \\ge$ **{math.ceil(s_total_head)} mm**
            * **Препоръка за изпитване:** Хидравлично изпитване на якост при налягане $P_{{test}} = 1.25 \\cdot {pressure_bar} = {1.25 * pressure_bar:.1f} \\text{{ bar}}$.
            """
        )
    else:
        mean_d_m = (diameter_mm + s_total_cyl) / 1000.0
        steel_density_kg_m3 = 7850.0
        metal_volume_loss_m3 = np.pi * mean_d_m * (c_corrosion / 1000.0) * pipe_length_m
        mass_loss_kg = metal_volume_loss_m3 * steel_density_kg_m3

        st.success(
            f"""
            💡 **Инженерно предписание за ТРЪБОПРОВОД ({metal}):**  
            * **Дължина на трасето ($L$):** **{pipe_length_m} m** | **Вътрешен диаметър ($D$):** **{diameter_mm:.0f} mm**
            * **Минимална проектна дебелина на стената:** $S_{{pipe}} \\ge$ **{math.ceil(s_total_cyl)} mm**
            * **Прогнозна загуба на метал от корозия ({years_service}г.):** **{mass_loss_kg:.1f} kg стомана**
            * **Препоръка за дефектоскопия:** Ултразвуков контрол на дебелината (UT) на колена и стеснения на всеки **5 години**.
            """
        )
