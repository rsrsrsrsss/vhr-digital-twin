import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Настройка на страницата
st.set_page_config(
    page_title="Дигитален Двойник ВХР — Блок 5, АЕЦ Козлодуй",
    page_icon="⚛️",
    layout="wide"
)

st.title("⚛️ Интерактивен Дигитален Двойник на ВХР — Блок 5, АЕЦ Козлодуй")
st.caption("Симулатор за оперативен мониторинг, динамична диагностика и корозионни изпитания")

# ---------------------------------------------------------
# Инициализация на състоянието на слайдерите (Сесийни променливи)
# ---------------------------------------------------------
if 'temp_val' not in st.session_state:
    st.session_state.temp_val = 301.0
if 'h3bo3_val' not in st.session_state:
    st.session_state.h3bo3_val = 3.5
if 'k_val' not in st.session_state:
    st.session_state.k_val = 12.0
if 'nh3_val' not in st.session_state:
    st.session_state.nh3_val = 18.0
if 'h2_val' not in st.session_state:
    st.session_state.h2_val = 45.0
if 'o2_val' not in st.session_state:
    st.session_state.o2_val = 0.0
if 'eta_val' not in st.session_state:
    st.session_state.eta_val = 1.8
if 'leak_val' not in st.session_state:
    st.session_state.leak_val = 0.0

# Функция за пълно автоматично възстановяване на Модул 1
def apply_auto_fix():
    st.session_state.temp_val = 301.0
    st.session_state.h3bo3_val = 3.5
    st.session_state.k_val = 12.0
    st.session_state.nh3_val = 18.0
    st.session_state.h2_val = 45.0
    st.session_state.o2_val = 0.0
    st.session_state.eta_val = 1.8
    st.session_state.leak_val = 0.0

# Главно меню
st.sidebar.title("🕹️ Избор на модул")
module = st.sidebar.radio(
    "Преминаване към:",
    [
        "1. Оперативен Мониторинг & Диагностика на Блок 5",
        "2. Лаборатория за корозионни изпитания & Пасивация"
    ]
)

# ==========================================================
# МОДУЛ 1: ОПЕРАТИВЕН МОНИТОРИНГ И ДИАГНОСТИКА
# ==========================================================
if module == "1. Оперативен Мониторинг & Диагностика на Блок 5":
    st.header("📊 Мониторинг на параметрите на ВХР и контрол на отклоненията")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Симулиране на ситуации (Първи контур)")
    
    primary_temp = st.sidebar.slider("Работна температура Т1 (°C)", 280.0, 325.0, key="temp_val", step=0.5)
    h3bo3 = st.sidebar.slider("Борна киселина H3BO3 (g/kg)", 0.0, 10.0, key="h3bo3_val", step=0.1)
    k_mg = st.sidebar.slider("Калиева основа / K+ (mg/dm³)", 0.0, 20.0, key="k_val", step=0.5)
    nh3_mg = st.sidebar.slider("Дозиране на Амоняк NH3 (mg/dm³)", 0.0, 30.0, key="nh3_val", step=1.0)
    h2_input = st.sidebar.slider("Разтворен Водород H2 (Ncm³/kg)", 0.0, 150.0, key="h2_val", step=1.0)
    o2_input = st.sidebar.slider("Приток на Кислород O2 (ppb)", 0.0, 50.0, key="o2_val", step=1.0)
    
    st.sidebar.subheader("🎛️ Симулиране на ситуации (Втори контур)")
    eta_ppm = st.sidebar.slider("Дозиране на ЕТА (mg/dm³)", 0.0, 5.0, key="eta_val", step=0.1)
    cond_leak = st.sidebar.slider("Приток в кондензатора (L/h)", 0.0, 5.0, key="leak_val", step=0.1)

    # Физикохимични изчисления
    ph_25_p1 = 7.0 + 0.12 * k_mg - 0.08 * h3bo3
    ph_t_p1 = ph_25_p1 - (primary_temp - 25.0) * 0.0072
    effective_o2 = max(0.0, o2_input - (h2_input / 10.0))
    is_emergency_scram = h2_input > 100.0

    # Основни метрики
    power_mw = "0 MWth" if is_emergency_scram else "3000 MWth"
    power_delta = "🚨 СРАБОТИЛА ААЗ!" if is_emergency_scram else "100% Номинал"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Теплинна мощност", power_mw, power_delta)
    m2.metric("pH_T (Първи контур)", f"{ph_t_p1:.2f}", "В норма (7.0-7.3)" if 7.0 <= ph_t_p1 <= 7.3 else "Отклонение!")
    m3.metric("Разтворен H2", f"{h2_input:.1f} Ncm³/kg", "🚨 Газов мехур!" if is_emergency_scram else "Норма: 30-60 Ncm³/kg")
    m4.metric("Разтворен O2 (Първи контур)", f"{effective_o2:.1f} ppb", "Критично!" if effective_o2 > 5.0 else "✅ < 5 ppb")

    st.markdown("---")

    # Контролна графика за pH_T
    st.subheader("📈 Контролна графика за отклонения от Технологичния регламент")
    hours = [f"{h:02d}:00" for h in range(24)]
    ph_min_limit = [7.00] * 24
    ph_max_limit = [7.30] * 24
    ph_trend = list(7.15 + 0.05 * np.sin(np.linspace(0, 5, 23))) + [ph_t_p1]

    fig_reg = go.Figure()
    fig_reg.add_trace(go.Scatter(x=hours, y=ph_trend, mode='lines+markers', name='pH_T (Текущо)', line=dict(color='#2980b9', width=3)))
    fig_reg.add_trace(go.Scatter(x=hours, y=ph_min_limit, mode='lines', name='Мин. праг (7.00)', line=dict(color='#e74c3c', width=2, dash='dash')))
    fig_reg.add_trace(go.Scatter(x=hours, y=ph_max_limit, mode='lines', name='Макс. праг (7.30)', line=dict(color='#e74c3c', width=2, dash='dash')))
    fig_reg.update_layout(title="Динамика на pH_T за 24 часа", xaxis_title="Време", yaxis_title="pH_T", yaxis=dict(range=[6.5, 7.8]), height=380, plot_bgcolor="#ffffff")
    st.plotly_chart(fig_reg, use_container_width=True)

    st.markdown("---")

    # Диагностика и автоматични препоръки
    st.subheader("📋 Система за диагностика и препоръки в реално време")
    has_issue = is_emergency_scram or (cond_leak > 0.2) or (effective_o2 > 5.0) or (ph_t_p1 < 7.00 or ph_t_p1 > 7.30)

    if has_issue:
        st.error("⚠️ РЕГИСТРИРАНО ОТКЛОНЕНИЕ ОТ ВХР!")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.button("🤖 Автоматично възстановяване на оптимален ВХР", on_click=apply_auto_fix)
        with col_b2:
            st.info("💡 Можете да оставите параметрите така за анализ на отклонението.")

        st.markdown("---")

        if is_emergency_scram:
            st.error("🚨🚨🚨 АВАРИЕН СИНАЛ: ПРЕВИШЕНА ГРАНИЦА НА РАЗТВОРИМОСТ НА ВОДОРОДА (H2 > 100 Ncm³/kg)!")
            st.markdown(f"""
            * **🔍 Причина:** Неконтролирано повишаване на $H_2$ (`{h2_input:.1f} Ncm³/kg`).
            * **💥 Риск:** Образуване на свободна газова възглавница и риск от кавитация на ГЦП.
            * **🛠️ Препоръка към оператора:** Намалете дозирането на $H_2$ под $60\\text{{ Ncm}}^3/\\text{{kg}}$ и извършете продухване.
            """)

        if cond_leak > 0.2:
            st.error("🚨 ВНИМАНИЕ: Приток на сурова/охладителна вода в кондензатора!")
            st.markdown(f"""
            * **🔍 Причина:** Пробив в тръбната система на кондензатора (Дебит: `{cond_leak} L/h`).
            * **💥 Риск:** Внасяне на твърдост и хлориди $\\rightarrow$ питингова корозия по ПГ.
            * **🛠️ Препоръка към оператора:** Увеличете дозата на ЕТА, форсирайте продухването на ПГ и задействайте БОВ.
            """)

        if effective_o2 > 5.0 and not is_emergency_scram:
            st.warning("⚠️ ПРЕДУПРЕПРЕЖДЕНИЕ: Повишен разтворен Кислород (O2)!")
            st.markdown(f"""
            * **🔍 Причина:** Недостатъчен водороден покрив (`H2 = {h2_input:.1f} Ncm³/kg`).
            * **💥 Риск:** Корозионно напукване под напрежение (SCC) на аустенитната стомана.
            * **🛠️ Препоръка към оператора:** Увеличете дозирането на $NH_3$ или $H_2$.
            """)

        if (ph_t_p1 < 7.00 or ph_t_p1 > 7.30) and not is_emergency_scram:
            st.warning("⚠️ ПРЕДУПРЕЖДЕНИЕ: Отклонение от Борно-Калиевия график!")
            st.markdown(f"""
            * **🔍 Причина:** Несъответствие между Борна киселина (`{h3bo3} g/kg`) и Калий (`{k_mg} mg/dm³`).
            * **💥 Риск:** Образуване на CRUD отлагания по обвивките на ТВЕЛ-ите.
            * **🛠️ Препоръка към оператора:** Коригирайте $KOH$, за да поддържате $pH_T$ в границите $7.10 - 7.20$.
            """)
    else:
        st.success("✅ Всички параметри са в ЗЕЛЕН СТАТУС. Спазва се Технологичният регламент на Блок 5.")

# ==========================================================
# МОДУЛ 2: ЛАБОРАТОРИЯ ЗА КОРОЗИОННИ ИЗПИТАНИЯ & ПАСИВАЦИЯ (ПЪЛНИ ПОДОБРЕНИЯ)
# ==========================================================
elif module == "2. Лаборатория за корозионни изпитания & Пасивация":
    st.header("🔬 Модул 2: Разширена лаборатория за корозия, пасивация и ресурсен анализ")
    st.caption("Физикохимичен симулатор за устойчивост на конструкционни материали от ВВЕР-1000")

    # --- 1. Избор на материал и компонент ---
    st.subheader("⚙️ 1. Конструкционен материал и компонент")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        metal = st.selectbox(
            "Избор на сплав:",
            [
                "Аустенитна стомана 08Х18Н10Т (Първи контур / ПГ)",
                "Въглеродна стомана 20К / 16ГС (Втори контур / Тръбопроводи)",
                "Никелова сплав Инконел-690 (Тръбички ПГ - Модернизирани)",
                "Циркониева сплав Э110 / Э635 (Обвивки на ТВЕЛ)"
            ]
        )
    with col_m2:
        fluid = st.selectbox(
            "Хидродинамичен режим:",
            [
                "💧 Еднофазен воден поток (Ламинарен)",
                "🌊 Турбулентен воден поток (V > 3 m/s)",
                "🌫️ Прегрята / Суха пара",
                "🫧 Двуфазен поток (Влажна пара / FAC риск)"
            ]
        )
    with col_m3:
        work_temp = st.slider("Работна температура T (°C)", 25.0, 350.0, 280.0, 5.0)

    # --- 2. Физикохимичен състав на средата ---
    st.markdown("### 🧪 2. Химичен състав на водната среда")
    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
    ph_val = fc1.slider("pH (при 25°C)", 4.0, 11.5, 9.2, 0.1)
    o2_conc = fc2.number_input("Разтворен O2 (ppb)", 0, 500, 5)
    cl_conc = fc3.number_input("Хлориди Cl- (ppb)", 0, 1000, 2)
    so4_conc = fc4.number_input("Сулфати SO4(2-) (ppb)", 0, 1000, 5)
    h2_conc = fc5.number_input("Разтворен H2 (Ncm³/kg)", 0, 100, 45)

    # --- Алгоритъм за изчисление на корозионното поведение ---
    corrosion_mechanism = []
    initial_wall_thickness = 1.5 # mm (проектна дебелина)

    if "Въглеродна" in metal:
        initial_wall_thickness = 8.0 # mm за тръбопровод
        base_rate = 0.025 * np.exp((work_temp - 100) / 110)
        
        # pH ефект върху разтворимостта на магнетита
        if ph_val < 9.0:
            base_rate *= (9.2 / ph_val) ** 3.0
            corrosion_mechanism.append("Интензивно киселинно разтваряне на магнетита")
        elif ph_val > 10.0:
            base_rate *= 1.2
            corrosion_mechanism.append("Алкална корозия при високи концентрации")

        # FAC (Ерозийна корозия)
        if "Двуфазен" in fluid or "Турбулентен" in fluid:
            fac_factor = 4.2 if "Двуфазен" in fluid else 2.3
            base_rate *= fac_factor
            corrosion_mechanism.append("Ерозионно-корозионно износване (FAC / Flow-Accelerated Corrosion)")

        if o2_conc > 30:
            base_rate *= (1.0 + o2_conc / 40.0)
            corrosion_mechanism.append("Кислородна деполяризация и язвено износване")

        if ph_val >= 9.2 and ph_val <= 9.8 and o2_conc <= 20 and "Двуфазен" not in fluid:
            passivated = True
            film_type = "Стабилен магнетитен защитен филм (Fe₃O₄)"
            film_stability = max(10, min(100, int(98 - (9.5 - ph_val)**2 * 40 - (work_temp - 280)*0.1)))
        else:
            passivated = False
            film_type = "Ронлив / Порест / Нестабилен магнетит"
            film_stability = max(5, int(45 - abs(9.5 - ph_val)*20 - (o2_conc/10)))

    elif "Аустенитна" in metal:
        initial_wall_thickness = 1.5 # mm за тръбички на ПГ
        base_rate = 0.0012 * np.exp((work_temp - 100) / 200)
        
        # Питтинг и SCC (Напукване)
        if (cl_conc > 30 or so4_conc > 50) and o2_conc > 10 and work_temp > 140:
            pitting_factor = 1.0 + (cl_conc / 30.0) * (o2_conc / 10.0) * 0.5 + (so4_conc / 50.0) * 0.3
            base_rate *= pitting_factor
            corrosion_mechanism.append("Питингова корозия и висок риск от Корозионно напукване под напрежение (SCC)")

        if h2_conc >= 30:
            base_rate *= 0.65
            corrosion_mechanism.append("Водородно инхибиране на радиолитичната окислителна среда")

        passivated = True
        film_type = "Плътен хромов оксиден слой (Cr₂O₃ / Fe-Cr Шпинел)"
        film_stability = max(15, min(100, int(99 - (cl_conc / 15) - (so4_conc / 25) - (o2_conc / 5))))

    elif "Инконел-690" in metal:
        initial_wall_thickness = 1.5 # mm
        base_rate = 0.0003 * np.exp((work_temp - 100) / 250)
        if cl_conc > 200:
            base_rate *= 1.3
            corrosion_mechanism.append("Локално микро-износване при екстремни хлориди")

        passivated = True
        film_type = "Високостабилен Никел-Хромов шпинел (Ni-Cr Spinel)"
        film_stability = max(50, min(100, int(100 - (cl_conc / 40))))

    else: # Цирконий Э110
        initial_wall_thickness = 0.65 # mm (обвивка ТВЕЛ)
        base_rate = 0.0008 * np.exp((work_temp - 200) / 100)
        if work_temp > 330:
            base_rate *= 2.5
            corrosion_mechanism.append("Ускорена Нодуларна корозия при висока температура")
        if h2_conc > 60:
            corrosion_mechanism.append("Риск от Водородна трошливост (Образуване на хидриди)")

        passivated = True
        film_type = "Моноклинен циркониев диоксид (ZrO₂)"
        film_stability = max(20, min(100, int(95 - (work_temp - 300)*0.5)))

    if not corrosion_mechanism:
        corrosion_mechanism.append("Равномерна (пасивна) корозия в нормирани граници")

    # Ресурсен изчислетелен модул
    allowable_thinning = initial_wall_thickness * 0.20 # 20% марж на сигурност
    estimated_lifespan_years = allowable_thinning / max(base_rate, 1e-6)

    # --- 3. Резултати от симулацията ---
    st.markdown("---")
    st.subheader("📊 3. Резултати и оценка на състоянието")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Скорост на корозия", f"{base_rate:.4f} mm/година")
    
    if passivated and film_stability > 70:
        r2.success("🛡️ ПАСИВИРАН СТАТУС")
    elif passivated:
        r2.warning("⚠️ УЯЗВИМ ПАСИВЕН СЛОЙ")
    else:
        r2.error("💥 АКТИВНА КОРОЗИЯ / FAC")

    r3.metric("Стабилност на филма", f"{film_stability}%")
    r4.metric("Прогнозен остатъчен ресурс", f"{estimated_lifespan_years:.1f} години", f"При проектна дебелина {initial_wall_thickness} mm")

    st.markdown(f"**Характеристика на получения повърхностен слой:** `{film_type}`")

    # Диагностичен панел
    st.markdown("#### 🔍 Регистрирани физикохимични механизми:")
    for mech in corrosion_mechanism:
        if "FAC" in mech or "SCC" in mech or "киселинно" in mech or "Нодуларна" in mech:
            st.error(f"🚨 **Критичен риск:** {mech}")
        elif "инхибиране" in mech or "Стабилен" in mech:
            st.success(f"✅ **Защитен фактор:** {mech}")
        else:
            st.info(f"ℹ️ **Режим:** {mech}")

    # --- 4. Интерактивни графики (Температура & pH) ---
    st.markdown("---")
    st.subheader("📈 4. Графичен лабораторен анализ")

    graph_tab1, graph_tab2 = st.tabs(["Температурна зависимост", "pH зависимост (Разтворимост)"])

    with graph_tab1:
        temp_range = np.linspace(25, 350, 60)
        if "Въглеродна" in metal:
            rates_t = [0.025 * np.exp((t - 100) / 110) * (4.2 if "Двуфазен" in fluid else 1.0) * ((9.2/ph_val)**3.0 if ph_val<9.0 else 1.0) for t in temp_range]
        elif "Аустенитна" in metal:
            rates_t = [0.0012 * np.exp((t - 100) / 200) * (1.0 + (cl_conc/30)*(o2_conc/10)*0.5 if cl_conc>30 and o2_conc>10 and t>140 else 1.0) for t in temp_range]
        elif "Инконел-690" in metal:
            rates_t = [0.0003 * np.exp((t - 100) / 250) for t in temp_range]
        else:
            rates_t = [0.0008 * np.exp((t - 200) / 100) * (2.5 if t > 330 else 1.0) for t in temp_range]

        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=temp_range, y=rates_t, mode='lines', name='Скорост на корозия (mm/година)', line=dict(color='#e74c3c', width=3)))
        fig_temp.add_trace(go.Scatter(x=[work_temp], y=[base_rate], mode='markers', name='Текуща работна точка', marker=dict(size=14, color='#2ecc71', symbol='diamond')))
        fig_temp.update_layout(title="Скорост на корозия спрямо Работната температура (°C)", xaxis_title="Температура T (°C)", yaxis_title="Скорост (mm/година)", height=380, plot_bgcolor="#ffffff")
        st.plotly_chart(fig_temp, use_container_width=True)

    with graph_tab2:
        ph_range = np.linspace(4.0, 11.5, 60)
        if "Въглеродна" in metal:
            rates_ph = [base_rate * ((9.2/p)**3.0 if p < 9.0 else (1.0 + (p-9.5)**2 * 0.15)) for p in ph_range]
        else:
            rates_ph = [base_rate * (1.0 + abs(7.0 - p)*0.1) for p in ph_range]

        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(x=ph_range, y=rates_ph, mode='lines', name='Скорост на корозия (mm/година)', line=dict(color='#8e44ad', width=3)))
        fig_ph.add_trace(go.Scatter(x=[ph_val], y=[base_rate], mode='markers', name='Текущо pH', marker=dict(size=14, color='#f1c40f', symbol='star')))
        fig_ph.update_layout(title="Крива на разтворимост и скорост на корозия спрямо pH (при 25°C)", xaxis_title="pH", yaxis_title="Скорост (mm/година)", height=380, plot_bgcolor="#ffffff")
        st.plotly_chart(fig_ph, use_container_width=True)
