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
st.caption("Симулатор за оперативен мониторинг, динамична диагностика и корозионни изпитания (ВВЕР-1000)")

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
        if cond_leak > 0.2:
            st.error("🚨 ВНИМАНИЕ: Приток на сурова/охладителна вода в кондензатора!")
        if effective_o2 > 5.0 and not is_emergency_scram:
            st.warning("⚠️ ПРЕДУПРЕПРЕЖДЕНИЕ: Повишен разтворен Кислород (O2)!")
        if (ph_t_p1 < 7.00 or ph_t_p1 > 7.30) and not is_emergency_scram:
            st.warning("⚠️ ПРЕДУПРЕЖДЕНИЕ: Отклонение от Борно-Калиевия график!")
    else:
        st.success("✅ Всички параметри са в ЗЕЛЕН СТАТУС. Спазва се Технологичният регламент на Блок 5.")

# ==========================================================
# МОДУЛ 2: ЛАБОРАТОРИЯ (ВВЕР-1000 СПЕЦИФИЧНИ СТОМАНИ)
# ==========================================================
elif module == "2. Лаборатория за корозионни изпитания & Пасивация":
    st.header("🔬 Модул 2: Разширена лаборатория за корозия, хидродинамика и пасивация")
    st.caption("Динамичен физикохимичен симулатор за материалите на реактор тип ВВЕР-1000")

    # --- 1. Избор на материал ---
    st.subheader("⚙️ 1. Избор на конструкционен материал / стомана за ВВЕР-1000")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        metal = st.selectbox(
            "Избор на сплав / стомана (Официален списък ВВЕР-1000):",
            [
                "Аустенитна стомана 08Х18Н10Т (Първи контур / Тръби Парогенератор)",
                "Аустенитна стомана 12Х18Н10Т (Спомагателни системи & Колектори)",
                "Антикорозионен наплав 04Х20Н10Г2Б (Вътрешна защита на ГЦТ)",
                "Конструкционна стомана 10ГН2МФА (Главни циркулационни тръбопроводи - ГЦТ)",
                "Корпусна стомана 15Х2МФА / 15Х2НМФА (Корпус на Реактора)",
                "Високоякостна стомана 25Х1МФ / 38ХН3МФА (Главни шпилки на Реактора)",
                "Въглеродна стомана 20К / 16ГС (Втори контур / Паропроводи)",
                "Циркониева сплав Э110 / Э635 (Обвивки на ТВЕЛ / Гориво)"
            ]
        )
    with col_m2:
        fluid = st.selectbox(
            "Тип на средата:",
            [
                "💧 Еднофазен воден поток (Вода под налягане)",
                "🌫️ Прегрята / Суха пара",
                "🫧 Двуфазен поток (Влажна пара)"
            ]
        )
    with col_m3:
        velocity = st.slider("Скорост на флуида v (m/s)", 0.0, 10.0, 2.0, 0.1)

    # --- БАЗА ДАННИ С ПАСПОРТИ НА СТОМАНИТЕ В ВВЕР-1000 ---
    scientific_passport = {
        "Аустенитна стомана 08Х18Н10Т (Първи контур / Тръби Парогенератор)": {
            "composition": "Fe-Cr18-Ni10-Ti0.5",
            "film": "Хромов оксид (Cr₂O₃) / Fe-Cr шпинел",
            "ph_optimum": "pH 6.8 - 7.4 (работна Т) / pH 9.0-10.5 (25°C)",
            "temp_limit": "До 350°C",
            "hydrodynamics": "Устойчива при високи скорости. Имунна срещу FAC.",
            "keller_fac": "НЕ Е ПРИЛОЖИМ (Cr > 13%).",
            "pitting_scc_risk": "Чувствителна към Cl- > 30 ppb и O2 > 10 ppb."
        },
        "Аустенитна стомана 12Х18Н10Т (Спомагателни системи & Колектори)": {
            "composition": "Fe-Cr18-Ni10-Ti0.7",
            "film": "Хромов оксид (Cr₂O₃)",
            "ph_optimum": "pH 7.0 - 10.5",
            "temp_limit": "До 350°C",
            "hydrodynamics": "Стабилна при бърз и бавен поток.",
            "keller_fac": "НЕ Е ПРИЛОЖИМ (Cr > 13%).",
            "pitting_scc_risk": "Риск от междукристална корозия при заварки."
        },
        "Антикорозионен наплав 04Х20Н10Г2Б (Вътрешна защита на ГЦТ)": {
            "composition": "Fe-Cr20-Ni10-Mn2-Nb (Нисък C)",
            "film": "Високохромов пасивационен оксид (Cr₂O₃ + NbC)",
            "ph_optimum": "pH 6.5 - 11.0",
            "temp_limit": "До 360°C",
            "hydrodynamics": "Изключително устойчив на ерозия.",
            "keller_fac": "НЕ Е ПРИЛОЖИМ (Cr 20%).",
            "pitting_scc_risk": "Много нисък риск поради ниското съдържание на въглерод и стабилизацията с ниобий (Nb)."
        },
        "Конструкционна стомана 10ГН2МФА (Главни циркулационни тръбопроводи - ГЦТ)": {
            "composition": "Fe-Mn1.0-Ni2.0-Mo0.5-V0.1",
            "film": "Магнетит (Fe₃O₄) — разчита на вътрешния наплав 04Х20Н10Г2Б",
            "ph_optimum": "pH 9.2 - 9.8",
            "temp_limit": "До 340°C",
            "hydrodynamics": "Изисква защита от антикорозионен наплав.",
            "keller_fac": "ПРИЛОЖИМ (без наплав).",
            "pitting_scc_risk": "Риск от обща корозия при увреждане на защитния слой."
        },
        "Корпусна стомана 15Х2МФА / 15Х2НМФА (Корпус на Реактора)": {
            "composition": "Fe-Cr2.5-Ni0.8-Mo0.6-V0.3",
            "film": "Магнетит (Fe₃O₄)",
            "ph_optimum": "pH 9.2 - 10.0 (при 25°C)",
            "temp_limit": "До 320°C (Защитена с вътрешен наплав)",
            "hydrodynamics": "Изисква защита от наплава при високи скорости.",
            "keller_fac": "ЧАСТИЧНО ПРИЛОЖИМ (Нисък Cr = 2.5%).",
            "pitting_scc_risk": "Нисък питинг, риск от радиационно оакрохляване."
        },
        "Високоякостна стомана 25Х1МФ / 38ХН3МФА (Главни шпилки на Реактора)": {
            "composition": "Fe-Cr1.5-Ni3.0-Mo0.4-V0.2",
            "film": "Тънък оксиден слой",
            "ph_optimum": "pH 8.5 - 9.5",
            "temp_limit": "До 300°C",
            "hydrodynamics": "Разположени извън прекия бърз поток.",
            "keller_fac": "СЛАБО ПРИЛОЖИМ.",
            "pitting_scc_risk": "ИЗКЛЮЧИТЕЛНО ВИСОК РИСК от Напукване под Напрежение (SCC) при овлажняване и Cl-!"
        },
        "Въглеродна стомана 20К / 16ГС (Втори контур / Паропроводи)": {
            "composition": "Fe-C0.2 (Без Cr и Ni)",
            "film": "Магнетит (Fe₃O₄) — бързо се разтваря при pH < 9.0",
            "ph_optimum": "pH 9.2 - 9.8 (Алкален режим)",
            "temp_limit": "До 250°C (Максимум на FAC при T=150-180°C)",
            "hydrodynamics": "Изключително уязвима при v > 2.5 m/s!",
            "keller_fac": "СИЛНО ПРИЛОЖИМ МОДЕЛ НА КЕЛЕР!",
            "pitting_scc_risk": "Бърза обща корозия и FAC при ниско pH."
        },
        "Циркониева сплав Э110 / Э635 (Обвивки на ТВЕЛ / Гориво)": {
            "composition": "Zr-Nb1.0%",
            "film": "Циркониев диоксид (ZrO₂)",
            "ph_optimum": "pH 6.8 - 7.3 (при работна Т)",
            "temp_limit": "До 350°C (При T > 900°C — пароциркониева реакция)",
            "hydrodynamics": "Оптимизирана за протичане в активната зона.",
            "keller_fac": "НЕ Е ПРИЛОЖИМ.",
            "pitting_scc_risk": "Водородна трошливост при H2 > 60 Ncm³/kg."
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

    # --- ДИНАМИЧНО ПРЕИЗЧИСЛЯВАНЕ ЗА ВСЯКА СТОМАНА В РЕАЛНО ВРЕМЕ ---
    corrosion_mechanism = []
    initial_wall_thickness = 1.5 if ("ПГ" in metal or "ТВЕЛ" in metal) else (12.0 if "шпилки" in metal else 8.0)

    # Фактор на скоростта (Модел на Келер)
    if velocity < 0.2:
        flow_factor = 1.0
        corrosion_mechanism.append("Утайки/Застой: Риск от подшламова корозия")
    elif velocity <= 2.5:
        flow_factor = 1.0 + (velocity / 5.0) ** 0.5
    else:
        flow_factor = 1.0 + (velocity / 2.5) ** 1.6
        if "Въглеродна" in metal or "10ГН2МФА" in metal:
            corrosion_mechanism.append(f"Висока скорост ({velocity} m/s) ➔ Келер FAC: Интензивно отмиване на магнетита!")

    # ИЗЧИСЛЕНИЯ ПО СПЕЦИФИЧНИТЕ СТОМАНИ
    if "Въглеродна" in metal or "10ГН2МФА" in metal:
        base_rate = 0.02 * np.exp((work_temp - 100) / 110) * flow_factor
        if ph_val < 9.2:
            base_rate *= (9.2 / ph_val) ** 3.0
            corrosion_mechanism.append("Киселинно разтваряне на магнетитния слой (pH < 9.2)")
        elif ph_val > 10.2:
            base_rate *= (ph_val / 9.5) ** 1.8
            corrosion_mechanism.append("Алкална корозия (Образуване на разтворими ферати)")
        if o2_conc > 20:
            base_rate *= (1.0 + o2_conc / 20.0)
            corrosion_mechanism.append("Кислородна деполяризация")

        if ph_val >= 9.2 and ph_val <= 9.8 and o2_conc <= 20 and velocity <= 2.5 and "Двуфазен" not in fluid:
            status = "GREEN"
            film_type = "Стабилен магнетитен защитен филм (Fe₃O₄)"
            film_stability = max(10, min(100, int(98 - abs(9.5 - ph_val)*30 - velocity*5)))
        elif ph_val < 8.5 or velocity > 3.5 or o2_conc > 50:
            status = "RED"
            film_type = "Разрушен / Разтворен магнетитен филм"
            film_stability = max(5, int(35 - abs(9.5 - ph_val)*15 - velocity*8))
        else:
            status = "YELLOW"
            film_type = "Уязвим / Частично нестабилен магнетит"
            film_stability = max(20, int(65 - abs(9.5 - ph_val)*20 - velocity*6))

    elif "15Х2МФА" in metal or "шпилки" in metal:
        base_rate = 0.015 * np.exp((work_temp - 100) / 130) * (flow_factor ** 0.8)
        if "шпилки" in metal and (cl_conc > 20 or o2_conc > 15):
            base_rate *= 3.0
            corrosion_mechanism.append("КРИТИЧЕН РИСК: Корпорационно Напукване под Напрежение (SCC) на шпилките!")

        if ph_val < 9.0:
            base_rate *= (9.0 / ph_val) ** 2.2
            corrosion_mechanism.append("Повишена разтворимост на магнетита при ниско pH")
        
        if ph_val >= 9.0 and ph_val <= 10.0 and velocity <= 3.0 and cl_conc <= 20:
            status = "GREEN"
            film_type = "Защитен магнетитен слой (Fe₃O₄)"
            film_stability = max(10, min(100, int(95 - velocity*4)))
        elif ph_val < 8.0 or velocity > 4.5 or (cl_conc > 50 and "шпилки" in metal):
            status = "RED"
            film_type = "Отмит магнетит / Риск от SCC скъсване"
            film_stability = max(10, int(40 - velocity*6))
        else:
            status = "YELLOW"
            film_type = "Отслабен пасивационен слой"
            film_stability = max(20, int(70 - velocity*5))

    elif "Аустенитна" in metal or "наплав" in metal:
        base_rate = 0.0008 * np.exp((work_temp - 100) / 210) * (flow_factor ** 0.3)
        pitting_sens = 0.10 if "наплав" in metal else 0.40

        if cl_conc > 30 or o2_conc > 10:
            pitting_factor = 1.0 + (cl_conc / 25.0) * (o2_conc / 10.0) * pitting_sens
            base_rate *= pitting_factor
            corrosion_mechanism.append("Риск от Питингова корозия и Корпорозионно напукване (SCC)")

        if cl_conc <= 30 and o2_conc <= 10 and ph_val >= 6.5:
            status = "GREEN"
            film_type = "Плътен Хромов Оксиден слой (Cr₂O₃ / Nb- Cr Шпинел)"
            film_stability = max(20, min(100, int(99 - (cl_conc / 15) - (o2_conc / 5))))
        elif cl_conc > 100 or (cl_conc > 50 and o2_conc > 20):
            status = "RED"
            film_type = "Пробит пасивационен филм (Питинги)"
            film_stability = max(5, int(40 - (cl_conc / 10)))
        else:
            status = "YELLOW"
            film_type = "Уязвим за питинг пасивационен филм"
            film_stability = max(15, int(70 - (cl_conc / 12)))

    else: # Циркониева сплав Э110
        base_rate = 0.0007 * np.exp((work_temp - 200) / 105)
        if work_temp > 330:
            base_rate *= 2.0
            corrosion_mechanism.append("Ускорена Нодуларна корозия (Т > 330°C)")
        if h2_conc > 60:
            corrosion_mechanism.append("Водородна трошливост (Образуване на Zr-хидриди)")

        if work_temp <= 330 and h2_conc <= 60:
            status = "GREEN"
            film_type = "Пасивационен филм ZrO₂"
            film_stability = max(20, min(100, int(96 - (work_temp - 300)*0.5)))
        elif work_temp > 345 or h2_conc > 80:
            status = "RED"
            film_type = "Деградирал ZrO₂ филм / Хидриране"
            film_stability = 35
        else:
            status = "YELLOW"
            film_type = "Уязвим ZrO₂ филм"
            film_stability = 65

    if not corrosion_mechanism:
        corrosion_mechanism.append("Оптимален пасивен режим с минимално оксидиране")

    allowable_thinning = initial_wall_thickness * 0.20
    estimated_lifespan_years = allowable_thinning / max(base_rate, 1e-6)

    # --- 3. РЕЗУЛТАТИ И ДИНАМИЧЕН ИНДИКАТОР ---
    st.markdown("---")
    st.subheader("📊 3. Динамични резултати и Инженерни Аргументи")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Скорост на корозия", f"{base_rate:.4f} mm/година")
    
    if status == "GREEN":
        r2.success("🟢 ПАСИВИРАН / БЕЗОПАСЕН")
    elif status == "YELLOW":
        r2.warning("🟡 УЯЗВИМ / ВНИМАНИЕ")
    else:
        r2.error("🔴 АКТИВНА КОРОЗИЯ / ОПАСНОСТ")

    r3.metric("Стабилност на филма", f"{film_stability}%")
    r4.metric("Прогнозен остатъчен ресурс", f"{estimated_lifespan_years:.1f} години", f"Марж: {allowable_thinning:.2f} mm")

    st.markdown("#### 💡 Научно-физикохимична аргументация за текущия статус:")
    if status == "GREEN":
        st.success(f"**Научна подкрепа (ЗЕЛЕН СТАТУС):** Параметрите (pH={ph_val}, T={work_temp}°C, v={velocity}m/s, Cl-={cl_conc}ppb) попадат в зоната на стабилност на `{film_type}`. Пасивният оксиден слой е плътен и предпазва стоманата.")
    elif status == "YELLOW":
        st.warning(f"**Научна подкрепа (ЖЪЛТ СТАТУС):** Налице е гранично отклонение! Слой `{film_type}` губи стабилност поради повишени хлориди/кислород или скорост. Препоръчва се корекция на ВХР.")
    else:
        st.error(f"**Научна подкрепа (ЧЕРВЕН СТАТУС):** Условията излизат от пасивацията! Налице е разтваряне на оксида или отмиване по Модела на Келер при v={velocity}m/s. Скоростта на корозия е критична!")

    st.markdown("#### 🔍 Регистрирани физикохимични механизми в реално време:")
    for mech in corrosion_mechanism:
        if "FAC" in mech or "SCC" in mech or "Киселинно" in mech or "Нодуларна" in mech or "трошливост" in mech:
            st.error(f"🚨 **Активен риск:** {mech}")
        elif "инхибиране" in mech or "Оптимален" in mech:
            st.success(f"✅ **Защитен фактор:** {mech}")
        else:
            st.info(f"ℹ️ **Режим:** {mech}")

    # ==========================================================
    # 🎯 ТОЧКА 4: СИМУЛАЦИЯ НА ПИТИНГОВА ДЪЛБОЧИНА (h_pit)
    # ==========================================================
    st.markdown("---")
    st.subheader("🎯 4. Симулация на Локална Питингова Корозия (Дълбочина $h_{pit}$ с времето)")
    
    st.markdown("""
    *Забележка:* При наличие на халогениди ($Cl^-$) и окислител ($O_2$), локалната питингова корозия се развива по захранван от дифзия степенеен закон: 
    $$h_{pit}(t) = K_{pit} \cdot (C_{Cl^-})^{0.5} \cdot (C_{O_2})^{0.3} \cdot t^{0.5} \quad [\mu m]$$
    """)

    years_sim = st.slider("Прогнозен период за развитие на питинга (Години):", 1, 30, 10)
    time_array = np.linspace(0.1, years_sim, 100)

    # Питингов коефициент K_pit за съответната стомана
    if "Аустенитна" in metal or "наплав" in metal:
        k_pit_base = 15.0
    elif "шпилки" in metal:
        k_pit_base = 35.0
    elif "Въглеродна" in metal or "10ГН2МФА" in metal:
        k_pit_base = 45.0
    else:
        k_pit_base = 5.0

    # Дълбочина на питинга в микрони (µm)
    pit_depth_um = k_pit_base * (max(1.0, cl_conc)**0.5) * (max(1.0, o2_conc)**0.3) * (time_array**0.5) / 10.0
    max_pit_final = pit_depth_um[-1]
    
    col_pit1, col_pit2 = st.columns([1, 2])
    
    with col_pit1:
        st.metric("Макс. дълбочина на питинг ($h_{pit}$)", f"{max_pit_final:.1f} µm", f"За {years_sim} години")
        if max_pit_final > 500:
            st.error("🚨 КРИТИЧЕН ПИТИНГ! Опасност от сквозен пробив на тръбопровода!")
        elif max_pit_final > 150:
            st.warning("⚠️ Повишен питинг. Необходим е ултразвуков дефектоскопски контрол.")
        else:
            st.success("✅ Дълбочината на питингите е в допустими граници.")

    with col_pit2:
        fig_pit = go.Figure()
        fig_pit.add_trace(go.Scatter(x=time_array, y=pit_depth_um, mode='lines', name='Дълбочина h_pit (µm)', line=dict(color='#d35400', width=3)))
        fig_pit.update_layout(
            title=f"Развитие на питингова дълбочина $h_{{pit}}$ за {metal}",
            xaxis_title="Време (Години)",
            yaxis_title="Дълбочина на питинга (µm)",
            height=300,
            plot_bgcolor="#ffffff"
        )
        st.plotly_chart(fig_pit, use_container_width=True)

    # --- 5. Традиционни Графики ---
    st.markdown("---")
    st.subheader("📈 5. Зависимости на скоростта на корозия")

    graph_tab1, graph_tab2, graph_tab3 = st.tabs(["Температурна зависимост", "pH зависимост (Разтворимост)", "Зависимост от Скоростта (v)"])

    with graph_tab1:
        temp_range = np.linspace(25, 350, 60)
        rates_t = [base_rate * np.exp((t - work_temp) / 120) for t in temp_range]

        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=temp_range, y=rates_t, mode='lines', name='Скорост (mm/год)', line=dict(color='#e74c3c', width=3)))
        fig_temp.add_trace(go.Scatter(x=[work_temp], y=[base_rate], mode='markers', name='Текуща точка', marker=dict(size=14, color='#2ecc71', symbol='diamond')))
        fig_temp.update_layout(title=f"Скорост на корозия спрямо T (°C) — {metal}", xaxis_title="Температура T (°C)", yaxis_title="Скорост (mm/година)", height=380, plot_bgcolor="#ffffff")
        st.plotly_chart(fig_temp, use_container_width=True)

    with graph_tab2:
        ph_range = np.linspace(4.0, 11.5, 60)
        if "Въглеродна" in metal or "10ГН2МФА" in metal:
            rates_ph = [base_rate * ((9.2/p)**2.8 if p < 9.0 else (1.0 + (p-9.5)**2 * 0.2)) for p in ph_range]
        else:
            rates_ph = [base_rate * (1.0 + abs(7.0 - p)*0.08) for p in ph_range]

        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(x=ph_range, y=rates_ph, mode='lines', name='Скорост (mm/год)', line=dict(color='#8e44ad', width=3)))
        fig_ph.add_trace(go.Scatter(x=[ph_val], y=[base_rate], mode='markers', name='Текущо pH', marker=dict(size=14, color='#f1c40f', symbol='star')))
        fig_ph.update_layout(title=f"Зависимост от pH — {metal}", xaxis_title="pH", yaxis_title="Скорост (mm/година)", height=380, plot_bgcolor="#ffffff")
        st.plotly_chart(fig_ph, use_container_width=True)

    with graph_tab3:
        v_range = np.linspace(0.0, 10.0, 50)
        rates_v = [base_rate * ((1.0 + (v/2.5)**1.6) / flow_factor) for v in v_range]

        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(x=v_range, y=rates_v, mode='lines', name='Скорост (mm/год)', line=dict(color='#27ae60', width=3)))
        fig_v.add_trace(go.Scatter(x=[velocity], y=[base_rate], mode='markers', name='Текуща скорост', marker=dict(size=14, color='#3498db', symbol='circle')))
        fig_v.update_layout(title=f"Зависимост от скоростта v (m/s) — {metal}", xaxis_title="Скорост v (m/s)", yaxis_title="Скорост (mm/година)", height=380, plot_bgcolor="#ffffff")
        st.plotly_chart(fig_v, use_container_width=True)
