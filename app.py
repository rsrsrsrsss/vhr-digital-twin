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
# Инициализация на сесийни променливи (Модул 1)
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

    power_mw = "0 MWth" if is_emergency_scram else "3000 MWth"
    power_delta = "🚨 СРАБОТИЛА ААЗ!" if is_emergency_scram else "100% Номинал"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Теплинна мощност", power_mw, power_delta)
    m2.metric("pH_T (Първи контур)", f"{ph_t_p1:.2f}", "В норма (7.0-7.3)" if 7.0 <= ph_t_p1 <= 7.3 else "Отклонение!")
    m3.metric("Разтворен H2", f"{h2_input:.1f} Ncm³/kg", "🚨 Газов мехур!" if is_emergency_scram else "Норма: 30-60 Ncm³/kg")
    m4.metric("Разтворен O2 (Първи контур)", f"{effective_o2:.1f} ppb", "Критично!" if effective_o2 > 5.0 else "✅ < 5 ppb")

    st.markdown("---")

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
# МОДУЛ 2: РАЗШИРЕНА ЛАБОРАТОРИЯ С ДЕТАЙЛЕН НАУЧЕН ПАСПОРТ
# ==========================================================
elif module == "2. Лаборатория за корозионни изпитания & Пасивация":
    st.header("🔬 Модул 2: Разширена лаборатория за корозия, хидродинамика и пасивация")
    st.caption("Физикохимичен симулатор за устойчивост на конструкционни стомани от ВВЕР-1000")

    # --- 1. Избор на материал ---
    st.subheader("⚙️ 1. Избор на конструкционен материал / стомана")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        metal = st.selectbox(
            "Избор на сплав / стомана:",
            [
                "Аустенитна стомана 08Х18Н10Т (Първи контур / ПГ)",
                "Аустенитна стомана 12Х18Н10Т (Спомагателни системи)",
                "Аустенитна стомана AISI 316L / 03Х17Н14М3 (Модернизирани възели)",
                "Перлитна стомана 15Х2МФА / 15Х2НМФА (Корпус на Реактора)",
                "Въглеродна стомана 20К / 16ГС (Втори контур / Тръбопроводи)",
                "Никелова сплав Инконел-690 (Тръбички ПГ)",
                "Циркониева сплав Э110 / Э635 (Обвивки на ТВЕЛ)"
            ]
        )
    with col_m2:
        fluid = st.selectbox(
            "Тип на средата:",
            [
                "💧 Еднофазен воден поток",
                "🌫️ Прегрята / Суха пара",
                "🫧 Двуфазен поток (Влажна пара)"
            ]
        )
    with col_m3:
        velocity = st.slider("Скорост на флуида v (m/s)", 0.0, 10.0, 2.0, 0.1)

    # --- НАУЧНО-ФИЗИКОХИМИЧЕН ПАСПОРТ И АРГУМЕНТАЦИЯ ---
    scientific_passport = {
        "Аустенитна стомана 08Х18Н10Т (Първи контур / ПГ)": {
            "composition": "Fe-Cr18-Ni10-Ti0.5",
            "film": "Хромов оксид (Cr₂O₃) / Fe-Cr шпинел",
            "ph_optimum": "pH 6.8 - 7.4 (при работна температура) / pH 9.0-10.5 при 25°C",
            "temp_limit": "До 350°C (Отлична устойчивост в 1-ви контур)",
            "hydrodynamics": "Подходяща за високоскоростен воден поток. Не е чувствителна към FAC.",
            "keller_fac": "НЕ Е ПРИЛОЖИМ (Високо съдържание на Chromium Cr > 13% напълно блокира FAC).",
            "pitting_scc_risk": "Висок риск от SCC при комбинация от Cl- > 50 ppb, O2 > 10 ppb и T > 150°C."
        },
        "Аустенитна стомана 12Х18Н10Т (Спомагателни системи)": {
            "composition": "Fe-Cr18-Ni10-Ti0.7",
            "film": "Хромов оксид (Cr₂O₃)",
            "ph_optimum": "pH 7.0 - 10.5",
            "temp_limit": "До 350°C",
            "hydrodynamics": "Стабилна при бърз и бавен поток. По-високо съдържание на въглерод/титан спрямо 08Х18Н10Т.",
            "keller_fac": "НЕ Е ПРИЛОЖИМ (Cr > 13%).",
            "pitting_scc_risk": "Уязвима към междукристална корозия (МКК) при заварени съединения без подходящо пасивиране."
        },
        "Аустенитна стомана AISI 316L / 03Х17Н14М3 (Модернизирани възели)": {
            "composition": "Fe-Cr17-Ni12-Mo2.5",
            "film": "Пасивационен филм (Cr₂O₃ + MoO₃)",
            "ph_optimum": "Широк спектър: pH 5.0 - 11.0",
            "temp_limit": "До 400°C",
            "hydrodynamics": "Отлична за агресивни среда и висока скорост.",
            "keller_fac": "НЕ Е ПРИЛОЖИМ (Cr > 13%).",
            "pitting_scc_risk": "Много нисък! Молибденът (Mo 2.5%) драстично повишава устойчивостта срещу питинг от хлориди."
        },
        "Перлитна стомана 15Х2МФА / 15Х2НМФА (Корпус на Реактора)": {
            "composition": "Fe-Cr2.5-Mo0.6-V0.3",
            "film": "Магнетитен оксиден слой (Fe₃O₄)",
            "ph_optimum": "pH 9.2 - 10.0 (при 25°C) за минимална разтворимост на магнетита",
            "temp_limit": "До 320°C (Работи под защитен вътрешен аустенитен наплав)",
            "hydrodynamics": "Изисква ниска скорост или защита от наплав. Уязвима при ниско pH.",
            "keller_fac": "ЧАСТИЧНО ПРИЛОЖИМ. Нисък Cr (2.5%) намалява FAC, но не го елиминира напълно без наплав.",
            "pitting_scc_risk": "Нисък питинг риск, но висок риск от обща корозия и флуенсно/радиационно стареене."
        },
        "Въглеродна стомана 20К / 16ГС (Втори контур / Тръбопроводи)": {
            "composition": "Fe-C0.2 (Без Cr и Ni)",
            "film": "Магнетит (Fe₃O₄) — податлив на разтваряне при pH < 9.0",
            "ph_optimum": "pH 9.2 - 9.8 (Строго задължително алкално pH за втория контур!)",
            "temp_limit": "Оптимум до 250°C. При T=150-180°C е максимумът на FAC!",
            "hydrodynamics": "Силно чувствителна към скорост и турбулентност! Риск от отмиване на магнетита.",
            "keller_fac": "СИЛНО ПРИЛОЖИМ МОДЕЛ НА КЕЛЕР! Скоростта на FAC зависи от $v^{0.8}$, T, pH и влажността на парата.",
            "pitting_scc_risk": "Уязвима към бърза обща корозия и ерозионно износване при влажна пара (Двуфазен поток)."
        },
        "Никелова сплав Инконел-690 (Тръбички ПГ)": {
            "composition": "Ni58-Cr30-Fe9",
            "film": "Високоплътен Ni-Cr шпинел",
            "ph_optimum": "Изключително широк диапазон (pH 4.0 - 11.5)",
            "temp_limit": "Над 350°C (Еталон за парогенераторни тръби)",
            "hydrodynamics": "Перфектна за високоскоростна топла вода и пара.",
            "keller_fac": "НЕ Е ПРИЛОЖИМ (Напълно имунна към FAC).",
            "pitting_scc_risk": "Изключително нисък (Модернизация спрямо по-стария Инконел-600)."
        },
        "Циркониева сплав Э110 / Э635 (Обвивки на ТВЕЛ)": {
            "composition": "Zr-Nb1.0%",
            "film": "Циркониев диоксид (ZrO₂)",
            "ph_optimum": "pH 6.8 - 7.3 (при работна T) с контролиран Lithium/Potassium",
            "temp_limit": "До 350°C при нормална експлоатация (При T > 900°C започва пароциркониева реакция!)",
            "hydrodynamics": "Оптимизирана за протичане на топлоносителя в активната зона.",
            "keller_fac": "НЕ Е ПРИЛОЖИМ.",
            "pitting_scc_risk": "Уязвима към водородна трошливост (образуване на Zr-хидриди) при H2 > 60 Ncm³/kg."
        }
    }

    pass_data = scientific_passport[metal]

    with st.expander("📖 Научно-инженерна справка и характеристики на избраната стомана", expanded=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"* **Химичен състав / Химия:** `{pass_data['composition']}`")
            st.markdown(f"* **Защитен филм / Пасивация:** `{pass_data['film']}`")
            st.markdown(f"* **Оптимално pH (Поурбе):** {pass_data['ph_optimum']}")
            st.markdown(f"* **Температурни граници:** {pass_data['temp_limit']}")
        with col_p2:
            st.markdown(f"* **Хидродинамичен профил:** {pass_data['hydrodynamics']}")
            st.markdown(f"* **Модел на Келер за FAC:** {pass_data['keller_fac']}")
            st.markdown(f"* **Уязвимост към Питинг / SCC:** {pass_data['pitting_scc_risk']}")

    # --- 2. Работни параметри ---
    st.markdown("### 🧪 2. Задаване на работни параметри на средата")
    fc1, fc2, fc3, fc4, fc5 = st.columns(5)
    work_temp = fc1.slider("Температура T (°C)", 25.0, 350.0, 280.0, 5.0)
    ph_val = fc2.slider("pH (при 25°C)", 4.0, 11.5, 9.2, 0.1)
    o2_conc = fc3.number_input("Разтворен O2 (ppb)", 0, 500, 5)
    cl_conc = fc4.number_input("Хлориди Cl- (ppb)", 0, 1000, 2)
    h2_conc = fc5.number_input("Разтворен H2 (Ncm³/kg)", 0, 100, 45)

    # --- Изчисления и физикохимична диагностика ---
    corrosion_mechanism = []
    initial_wall_thickness = 1.5 if "ПГ" in metal or "ТВЕЛ" in metal else 8.0

    # Фактор от скорост
    if velocity < 0.2:
        flow_factor = 1.0
        corrosion_mechanism.append("Утайки/Застой: Риск от подшламова корозия")
    elif velocity <= 2.5:
        flow_factor = 1.0 + (velocity / 5.0) ** 0.5
    else:
        flow_factor = 1.0 + (velocity / 2.5) ** 1.6
        if "Въглеродна" in metal or "Перлитна" in metal:
            corrosion_mechanism.append(f"Висока скорост ({velocity} m/s) $\\rightarrow$ Модел на Келер: Интензивен FAC!")

    # Изчисляване на база сплав
    if "Въглеродна" in metal or "Перлитна" in metal:
        base_rate = 0.02 * np.exp((work_temp - 100) / 110) * flow_factor
        
        if ph_val < 9.0:
            base_rate *= (9.2 / ph_val) ** 2.8
            corrosion_mechanism.append("Киселинно разтваряне на магнетитния филм (Отклонение от Поурбе)")
        elif ph_val > 10.2:
            base_rate *= (ph_val / 9.5) ** 1.8
            corrosion_mechanism.append("Алкална корозия (Образуване на разтворими ферати)")

        if o2_conc > 30:
            base_rate *= (1.0 + o2_conc / 35.0)
            corrosion_mechanism.append("Кислородна деполяризация")

        if ph_val >= 9.2 and ph_val <= 9.8 and o2_conc <= 20 and velocity <= 2.5 and "Двуфазен" not in fluid:
            passivated = True
            film_type = "Стабилен магнетитен защитен филм (Fe₃O₄)"
            film_stability = max(10, min(100, int(98 - abs(9.5 - ph_val)*30 - velocity*5)))
        else:
            passivated = False
            film_type = "Ронлив / Частично отмит магнетитен филм"
            film_stability = max(5, int(45 - abs(9.5 - ph_val)*15 - velocity*8))

    elif "Аустенитна" in metal:
        base_rate = 0.001 * np.exp((work_temp - 100) / 210) * (flow_factor ** 0.3)
        pitting_sens = 0.2 if "316L" in metal else 0.5

        if cl_conc > 30 and o2_conc > 10 and work_temp > 140:
            pitting_factor = 1.0 + (cl_conc / 30.0) * (o2_conc / 10.0) * pitting_sens
            base_rate *= pitting_factor
            corrosion_mechanism.append("Питингова корозия и риск от Кор. Напукване под Напрежение (SCC)")

        if h2_conc >= 30:
            base_rate *= 0.65
            corrosion_mechanism.append("Водородно инхибиране на радиолизата")

        passivated = True
        film_type = "Плътен Хромов Оксиден слой (Cr₂O₃ / Fe-Cr Шпинел)"
        film_stability = max(15, min(100, int(99 - (cl_conc / 20) - (o2_conc / 8))))

    elif "Инконел-690" in metal:
        base_rate = 0.00025 * np.exp((work_temp - 100) / 260)
        passivated = True
        film_type = "Ултра-стабилен Ni-Cr шпинелен оксид"
        film_stability = max(60, min(100, int(100 - (cl_conc / 50))))

    else: # Цирконий Э110
        base_rate = 0.0007 * np.exp((work_temp - 200) / 105)
        if work_temp > 330:
            base_rate *= 2.2
            corrosion_mechanism.append("Ускорена Нодуларна корозия")
        if h2_conc > 60:
            corrosion_mechanism.append("Водородна трошливост (Образуване на Zr-хидриди)")

        passivated = True
        film_type = "Пасивационен филм ZrO₂"
        film_stability = max(20, min(100, int(95 - (work_temp - 300)*0.5)))

    if not corrosion_mechanism:
        corrosion_mechanism.append("Нормален пасивен режим с незначително оксидиране")

    allowable_thinning = initial_wall_thickness * 0.20
    estimated_lifespan_years = allowable_thinning / max(base_rate, 1e-6)

    # --- 3. Резултати ---
    st.markdown("---")
    st.subheader("📊 3. Резултати и Инженерни Аргументи")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Скорост на корозия", f"{base_rate:.4f} mm/година")
    
    if passivated and film_stability > 70:
        r2.success("🛡️ ПАСИВИРАН СТАТУС")
    elif passivated:
        r2.warning("⚠️ УЯЗВИМ ПАСИВЕН СЛОЙ")
    else:
        r2.error("💥 АКТИВНА КОРОЗИЯ / FAC")

    r3.metric("Стабилност на филма", f"{film_stability}%")
    r4.metric("Прогнозен остатъчен ресурс", f"{estimated_lifespan_years:.1f} години", f"За марж {allowable_thinning:.2f} mm")

    # Текстова аргументация на състоянието
    st.markdown("#### 💡 Аргументи за получения статус:")
    if passivated and film_stability > 70:
        st.success(f"**Научна подкрепа:** Условията (pH={ph_val}, T={work_temp}°C, v={velocity}m/s) съответстват на термодинамичната стабилност на `{film_type}`. Пасивният слой е плътен и предпазва основния метал.")
    elif passivated:
        st.warning(f"**Научна подкрепа:** Слой `{film_type}` е налице, но е уязвим заради високи хлориди ({cl_conc} ppb), кислород ({o2_conc} ppb) или температура. Налице е риск от локален питинг.")
    else:
        st.error(f"**Научна подкрепа:** Термодинамичните условия излизат извън пасивната зона на Поурбе или скоростта ({velocity} m/s) надвишава якостта на оксида (Модел на Келер). Налице е активно разтваряне!")

    st.markdown("#### 🔍 Регистрирани физикохимични механизми:")
    for mech in corrosion_mechanism:
        if "FAC" in mech or "SCC" in mech or "Киселинно" in mech or "Нодуларна" in mech or "трошливост" in mech:
            st.error(f"🚨 **Активен риск:** {mech}")
        elif "инхибиране" in mech or "Стабилен" in mech:
            st.success(f"✅ **Защитен фактор:** {mech}")
        else:
            st.info(f"ℹ️ **Режим:** {mech}")

    # --- 4. Интерактивни графики ---
    st.markdown("---")
    st.subheader("📈 4. Зависимости на скоростта на корозия")

    graph_tab1, graph_tab2, graph_tab3 = st.tabs(["Температурна зависимост", "pH зависимост (Разтворимост)", "Зависимост от Скоростта (v)"])

    with graph_tab1:
        temp_range = np.linspace(25, 350, 60)
        rates_t = [base_rate * np.exp((t - work_temp) / 120) for t in temp_range]

        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=temp_range, y=rates_t, mode='lines', name='Скорост (mm/год)', line=dict(color='#e74c3c', width=3)))
        fig_temp.add_trace(go.Scatter(x=[work_temp], y=[base_rate], mode='markers', name='Текуща точка', marker=dict(size=14, color='#2ecc71', symbol='diamond')))
        fig_temp.update_layout(title="Скорост на корозия спрямо Работната температура (°C)", xaxis_title="Температура T (°C)", yaxis_title="Скорост (mm/година)", height=380, plot_bgcolor="#ffffff")
        st.plotly_chart(fig_temp, use_container_width=True)

    with graph_tab2:
        ph_range = np.linspace(4.0, 11.5, 60)
        if "Въглеродна" in metal or "Перлитна" in metal:
            rates_ph = [base_rate * ((9.2/p)**2.8 if p < 9.0 else (1.0 + (p-9.5)**2 * 0.2)) for p in ph_range]
        else:
            rates_ph = [base_rate * (1.0 + abs(7.0 - p)*0.08) for p in ph_range]

        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(x=ph_range, y=rates_ph, mode='lines', name='Скорост (mm/год)', line=dict(color='#8e44ad', width=3)))
        fig_ph.add_trace(go.Scatter(x=[ph_val], y=[base_rate], mode='markers', name='Текущо pH', marker=dict(size=14, color='#f1c40f', symbol='star')))
        fig_ph.update_layout(title="Крива на разтворимост и скорост на корозия спрямо pH (при 25°C)", xaxis_title="pH", yaxis_title="Скорост (mm/година)", height=380, plot_bgcolor="#ffffff")
        st.plotly_chart(fig_ph, use_container_width=True)

    with graph_tab3:
        v_range = np.linspace(0.0, 10.0, 50)
        rates_v = [base_rate * ((1.0 + (v/2.5)**1.6) / flow_factor) for v in v_range]

        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(x=v_range, y=rates_v, mode='lines', name='Скорост (mm/год)', line=dict(color='#27ae60', width=3)))
        fig_v.add_trace(go.Scatter(x=[velocity], y=[base_rate], mode='markers', name='Текуща скорост', marker=dict(size=14, color='#3498db', symbol='circle')))
        fig_v.update_layout(title="Зависимост на корозията/FAC от Скоростта на флуида (m/s)", xaxis_title="Скорост v (m/s)", yaxis_title="Скорост (mm/година)", height=380, plot_bgcolor="#ffffff")
        st.plotly_chart(fig_v, use_container_width=True)
