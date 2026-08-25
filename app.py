import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import math

# ---------------------------------------------------------
# Настройка на страницата
# ---------------------------------------------------------
st.set_page_config(
    page_title="Дигитален Двойник ВХР — Блок 5, АЕЦ Козлодуй",
    page_icon="⚛️",
    layout="wide"
)

st.title("⚛️ Интерактивен Дигитален Двойник на ВХР — Блок 5, АЕЦ Козлодуй")
st.caption("Симулатор за оперативен мониторинг, хидродинамика, корозия и механично оразмеряване (ВВЕР-1000)")

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
        "2. Лаборатория: Корозия, Питинг & Оразмеряване на съоръжения"
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
# МОДУЛ 2: ЛАБОРАТОРИЯ, НАЛЯГАНЕ & ОРАЗМЕРЯВАНЕ
# ==========================================================
elif module == "2. Лаборатория: Корозия, Питинг & Оразмеряване на съоръжения":
    st.header("🔬 Разширена лаборатория: Хидродинамика, Налягане и Проектна Дебелина")
    st.caption("Комплексен химико-механичен симулатор за оборудване и тръбопроводи в АЕЦ ВВЕР-1000")

    # Богата база данни с пълните физико-химични, оперативни и механични характеристики
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

    # --- 1. Избор на съоръжение и материал ---
    st.subheader("⚙️ 1. Избор на съоръжение и конструкционен материал")
    
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

    # 📌 ХАРАКТЕРИСТИКА НА ИЗБРАНИЯ МЕТАЛ (ИНФО-КАРЕ / EXPANDER)
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

    allowable_stress_db = {k: v["sigma_dov"] for k, v in metal_info_db.items()}

    # --- 2. Геометрия & Работни условия ---
    st.markdown("---")
    st.subheader("📐 2. Геометрични параметри и работни условия")
    
    gc1, gc2, gc3, gc4 = st.columns(4)
    pressure_bar = gc1.slider("Работно налягане P (bar)", 1.0, 180.0, 157.0, 1.0)
    work_temp = gc2.slider("Температура T (°C)", 25.0, 350.0, 300.0, 5.0)
    velocity = gc3.slider("Скорост на флуида v (m/s)", 0.0, 10.0, 2.0, 0.1)
    years_service = gc4.slider("Ресурс (Години):", 1, 60, 40)

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

    # Химически агресори
    st.markdown("##### 🧪 Химични агресори във флуида")
    hc1, hc2, hc3 = st.columns(3)
    ph_val = hc1.slider("pH (при 25°C)", 4.0, 11.5, 9.2, 0.1)
    o2_conc = hc2.number_input("Разтворен O2 (ppb)", 0, 500, 5)
    cl_conc = hc3.number_input("Хлориди Cl- (ppb)", 0, 1000, 2)

    # --- 3. ДИНАМИЧНО ПРЕИЗЧИСЛЯВАНЕ НА КОРОЗИЯТА ---
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

    # --- 4. МЕХАНИЧНИ И КОРРОЗИОННИ ИЗЧИСЛЕНИЯ ---
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

    # --- 5. РЕЗУЛТАТИ И ИНЖЕНЕРНИ ПРЕПОРЪКИ ---
    st.markdown("---")
    st.subheader("📋 3. Инженерна спецификация и предписание")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Якостна дебелина (P)", f"{s_mech_cyl:.2f} mm", f"P = {pressure_bar} bar")
    r2.metric("Загуба от корозия (C_corr)", f"{c_corrosion:.2f} mm", f"За {years_service} години")
    r3.metric("Питинг дълбочина (h_pit)", f"{h_pit_um:.1f} µm", f"({h_pit_mm:.3f} mm)")
    r4.metric("МИН. ПРОЕКТНА ДЕБЕЛИНА", f"{math.ceil(s_total_cyl)} mm", f"Номинален размер", delta_color="normal")

    if "Цилиндричен съд" in equipment_type:
        st.success(
            f"""
            💡 **Инженерно предписание за ЦИЛИНДРИЧЕН СЪД ({metal}):**  
            * **Обем на съда ($V$):** **{vessel_volume_m3:.1f} m³** | **Изчислен диаметър ($D$):** **{diameter_mm:.0f} mm**
            * **Дебелина на цилиндричната обечайка:** $S_{{cyl}} \\ge$ **{math.ceil(s_total_cyl)} mm** (Якост: {s_mech_cyl:.1f} mm + Корозиен толеранс: {(c_corrosion + h_pit_mm):.2f} mm)
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
            * **Прогнозна загуба на метал от корозия за трасето ({years_service}г.):** **{mass_loss_kg:.1f} kg стомана**
            * **Препоръка за дефектоскопия:** Ултразвуков контрол на дебелината (UT) на колена и стеснения на всеки **5 години**.
            """
        )

    # --- 6. ГРАФИКА ЗА РАЗВИТИЕТО НА ПИТИНГА ---
    st.markdown("---")
    st.subheader("🎯 4. Симулация на Локална Питингова Корозия ($h_{pit}$ с времето)")
    st.info(
        r"""
        **🔍 Физикохимичен механизъм:**  
        При наличие на халогениди ($Cl^-$) и окислител ($O_2$), локалната питингова корозия се развива по **дифузионно-контролиран степенен закон** (съгласно Втория закон на Фик за масопренос):
        $$h_{pit}(t) = K_{pit} \cdot (C_{Cl^-})^{0.5} \cdot (C_{O_2})^{0.3} \cdot t^{0.5} \quad [\mu m]$$
        *Забележка: Параболичният софтуерен профил ($t^{0.5}$) отразява забавянето на корозията във времето поради затруднена дифузия на йони в дълбочината на питинга.*
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
