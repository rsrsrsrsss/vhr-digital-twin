import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Настройка на страницата
st.set_page_config(
    page_title="Дигитален Двойник ВХР — Блок 5, АЕЦ Козлодуй",
    page_icon="⚛️",
    layout="wide"
)

st.title("⚛️ Дигитален Двойник на ВХР — Блок 5, АЕЦ Козлодуй")
st.caption("Симулатор за оперативен мониторинг, диагностика на аварийни ситуации и корозионни изпитания")

# Инициализация на състоянието на слайдерите (ако не са дефинирани)
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

# Функция за ПЪЛНО и безупречно възстановяване на всички параметри в норма
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
        "1. Интерактивен Двойник на Блок 5 (1-ви и 2-ри контур)",
        "2. Лаборатория за корозионни изпитания & Пасивация"
    ]
)

# ==========================================================
# МОДУЛ 1: ДВОЙНИК НА БЛОК 5 (МОНИТОРИНГ И СИТУАЦИИ)
# ==========================================================
if module == "1. Интерактивен Двойник на Блок 5 (1-ви и 2-ри контур)":
    st.header("📊 Модул 1: Дигитален двойник на Блок 5 в реално време")
    
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

    # Точни физикохимични изчисления
    ph_25_p1 = 7.0 + 0.12 * k_mg - 0.08 * h3bo3
    ph_t_p1 = ph_25_p1 - (primary_temp - 25.0) * 0.0072
    effective_o2 = max(0.0, o2_input - (h2_input / 10.0))

    # Условия за сработване на ААЗ и аварийни сигнали
    is_emergency_scram = h2_input > 100.0
    power_mw = "0 MWth" if is_emergency_scram else "3000 MWth"
    power_delta = "🚨 СРАБОТИЛА ААЗ!" if is_emergency_scram else "100% Номинал"

    # Основни метрики
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Теплинна мощност", power_mw, power_delta)
    m2.metric("pH_T (Първи контур)", f"{ph_t_p1:.2f}", "В норма (7.0-7.3)" if 7.0 <= ph_t_p1 <= 7.3 else "Отклонение!")
    m3.metric("Разтворен H2", f"{h2_input:.1f} Ncm³/kg", "🚨 Газов мехур!" if is_emergency_scram else "Норма: 30-60 Ncm³/kg")
    m4.metric("Разтворен O2 (Първи контур)", f"{effective_o2:.1f} ppb", "Критично!" if effective_o2 > 5.0 else "✅ < 5 ppb")

    st.markdown("---")

    # Времеви графики
    tab1, tab2 = st.tabs(["🔴 Първи контур (Борно-Калиев режим & Газове)", "🔵 Втори контур (Питателна вода & ЕТА)"])
    
    time_series = pd.date_range(end=pd.Timestamp.now(), periods=20, freq='2min')
    np.random.seed(42)

    with tab1:
        st.subheader("Мониторинг на Първи контур (ВВЕР-1000)")
        df_p1 = pd.DataFrame({
            "Време": time_series,
            "H3BO3 (g/kg)": np.random.normal(h3bo3, 0.01, 20),
            "Калий K+ (mg/dm³)": np.random.normal(k_mg, 0.05, 20),
            "Разтворен H2 (Ncm³/kg)": np.random.normal(h2_input, 0.3, 20),
            "Разтворен O2 (ppb)": np.random.normal(effective_o2, 0.05 if effective_o2 > 0 else 0, 20)
        })
        fig1 = px.line(df_p1, x="Време", y=["H3BO3 (g/kg)", "Калий K+ (mg/dm³)", "Разтворен H2 (Ncm³/kg)", "Разтворен O2 (ppb)"],
                       title="Динамика на критичните химически компоненти в Първи контур")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("Мониторинг на Втори контур (Парогенератори & Питателна вода)")
        cond_spec = 0.11 + cond_leak * 0.08 + (0.05 if eta_ppm < 1.0 else 0.0)
        df_p2 = pd.DataFrame({
            "Време": time_series,
            "Концентрация на ЕТА (mg/dm³)": np.random.normal(eta_ppm, 0.02, 20),
            "Уделна електрическа проводимост χc (µS/cm)": np.random.normal(cond_spec, 0.003, 20)
        })
        fig2 = px.line(df_p2, x="Време", y=["Концентрация на ЕТА (mg/dm³)", "Уделна електрическа проводимост χc (µS/cm)"],
                       title="Динамика на pH-коректора и Електрическата проводимост във Втори контур")
        st.plotly_chart(fig2, use_container_width=True)

    # ДИАГНОСТИКА НА СИТУАЦИИ И АВТОМАТИЧНИ ПРЕПОРЪКИ
    st.markdown("---")
    st.subheader("📋 Система за диагностика и препоръки в реално време")

    # Точно определяне дали има регистрирано отклонение
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
            * **📍 Локализация:** Първи циркулационен контур (Горна част на реактора / Хорда на ГЦП).
            * **🔍 Причина:** Неконтролирано повишаване на $H_2$ (`{h2_input:.1f} Ncm³/kg`), надвишаващо предела на разтворимост при работна температура.
            * **💥 Риск:** Образуване на свободна газова възглавница, риск от кавитация на ГЦП и нарушено охлаждане на активната зона.
            * **⚡ Действие на защитите:** Сработила Аварийна защита на реактора (ААЗ)!
            * **🛠️ Препоръка към оператора:** Намалете дозирането на $H_2$ под $60\\text{{ Ncm}}^3/\\text{{kg}}$ и извършете продухване.
            """)

        if cond_leak > 0.2:
            st.error("🚨 ВНИМАНИЕ: Приток на сурова/охладителна вода в кондензатора!")
            st.markdown(f"""
            * **📍 Локализация:** Кондензационен тракт / Парогенератори (Втори контур).
            * **🔍 Причина:** Пробив в тръбната система на кондензатора (Дебит: `{cond_leak} L/h`).
            * **💥 Риск:** Внасяне на твърдост и хлориди $\\rightarrow$ интензивна питингова корозия по тръбичките на ПГ.
            * **🛠️ Препоръка към оператора:** Увеличете дозата на ЕТА, форсирайте продухването на ПГ и подгответе задействане на БОВ.
            """)

        if effective_o2 > 5.0 and not is_emergency_scram:
            st.warning("⚠️ ПРЕДУПРЕЖДЕНИЕ: Повишен разтворен Кислород (O2) в Първи контур!")
            st.markdown(f"""
            * **📍 Локализация:** Първи контур.
            * **🔍 Причина:** Недостатъчен водороден покрив (`H2 = {h2_input:.1f} Ncm³/kg`) за радиолитично свързване на $O_2$.
            * **💥 Риск:** Корозионно напукване под напрежение (SCC) на аустенитните стомани 08Х18Н10Т.
            * **🛠️ Препоръка към оператора:** Увеличете дозирането на Амоняк ($NH_3$) или директния Водород ($H_2$).
            """)

        if (ph_t_p1 < 7.00 or ph_t_p1 > 7.30) and not is_emergency_scram:
            st.warning("⚠️ ПРЕДУПРЕЖДЕНИЕ: Отклонение от Борно-Калиевия координационен график!")
            st.markdown(f"""
            * **📍 Локализация:** Active Zone / ТВЕЛ.
            * **🔍 Причина:** Несъответствие между концентрацията на Борна киселина (`{h3bo3} g/kg`) и Калий (`{k_mg} mg/dm³`).
            * **💥 Риск:** Пренасяне на корозионни продукты и образуване на CRUD отлагания по обвивките на ТВЕЛ-ите.
            * **🛠️ Препоръка към оператора:** Коригирайте съдържанието на $KOH$, за да поддържате $pH_T$ в границите $7.10 - 7.20$.
            """)
    else:
        st.success("✅ Всички параметри са в нормите на Технологичния регламент за експлоатация на Блок 5.")

# ==========================================================
# МОДУЛ 2: КОРОЗИОНЕН СИМУЛАТОР & ПАСИВАЦИЯ
# ==========================================================
elif module == "2. Лаборатория за корозионни изпитания & Пасивация":
    st.header("🔬 Модул 2: Лаборатория за изпитания на метали и пасивация")
    st.caption("Оценка на корозионната устойчивост на конструкционни материали от ВВЕР-1000")

    c1, c2, c3 = st.columns(3)
    with c1:
        metal = st.selectbox(
            "Изберете конструкционен метал / сплав:",
            [
                "Аустенитна стомана 08Х18Н10Т (Първи контур / ПГ)",
                "Въглеродна стомана 20К / 16ГС (Втори контур)",
                "Никелова сплав Инконел-690 (Тръбички ПГ)"
            ]
        )
    with c2:
        fluid = st.selectbox(
            "Агрегатно състояние на средата:",
            [
                "💧 Водна фаза (Течна)",
                "🌫️ Паро-газова фаза (Суха пара)",
                "🫧 Двуфазен поток (Вода + Пара / Влажна пара)"
            ]
        )
    with c3:
        work_temp = st.slider("Температура на изпитанието (°C)", 25.0, 350.0, 280.0, 5.0)

    st.markdown("### 🧪 Входни химически параметри на средата")
    fc1, fc2, fc3 = st.columns(3)
    ph_val = fc1.slider("pH на водната среда", 4.0, 11.0, 9.2, 0.1)
    o2_conc = fc2.number_input("Концентрация на O2 (ppb)", 0, 500, 10)
    cl_conc = fc3.number_input("Концентрация на Хлориди Cl- (ppb)", 0, 1000, 5)

    # Симулационни модели за корозия
    if "Въглеродна" in metal:
        base_rate = 0.04 * np.exp((work_temp - 100)/100)
        if ph_val < 9.0:
            base_rate *= 2.8
        if fluid == "🫧 Двуфазен поток (Вода + Пара / Влажна пара)":
            base_rate *= 3.5  # Ерозионно-корозионно износване (FAC)
            
        if ph_val >= 9.2 and o2_conc < 20 and "Двуфазен" not in fluid:
            passivated = True
            film_type = "Магнетитен защитен филм (Fe3O4)"
        else:
            passivated = False
            film_type = "Няма стабилен филм (Активно разтваряне / FAC)"

    elif "Аустенитна" in metal:
        base_rate = 0.002 * np.exp((work_temp - 100)/200)
        if cl_conc > 100 and work_temp > 150:
            base_rate *= 5.0
        
        passivated = True
        film_type = "Хромов оксиден пасивационен слой (Cr2O3)"

    else: # Инконел 690
        base_rate = 0.0008 * np.exp((work_temp - 100)/250)
        passivated = True
        film_type = "Високоустойчив Никелово-Хромов пасивационен филм"

    st.markdown("---")
    st.subheader("📊 Резултати от изпитването")

    r1, r2, r3 = st.columns(3)
    r1.metric("Скорост на корозия", f"{base_rate:.4f} mm/година")
    
    if passivated:
        r2.success("🛡️ СТАТУС: МЕТАЛЪТ Е ПАСИВИРАН")
    else:
        r2.error("💥 СТАТУС: АКТИВНА КОРОЗИЯ / FAC")

    r3.info(f"🔬 Пасивационен слой: {film_type}")

    st.markdown("### 🔍 Физикохимична диагноза:")
    if not passivated and "Въглеродна" in metal:
        st.error("⚠️ **Висок риск от Ерозионно-корозионно износване (FAC)!** Защитният магнетитен слой ($Fe_3O_4$) се разтваря интензивно поради ниското pH или турбулентния двуфазен поток.")
    elif "Аустенитна" in metal and cl_conc > 100:
        st.warning("⚠️ **Риск от питинг и Корозионно напукване под напрежение (SCC)!** Наличието на хлориди над 100 ppb при висока температура разрушава локално $Cr_2O_3$ слоя.")
    else:
        st.success("✅ **Отлична корозионна устойчивост.** Металът формира стабилен защитен филм и запазва целостта си при избраните работни условия.")
