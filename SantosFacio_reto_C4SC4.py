# =====================================================================
# The Learning Gate.
# Diplomado en Ciencia de Datos.
# Competencia: Diseño de Interfaces Visuales de Datos.
# Subcompetencia: Aplicación web de ciencia de datos.
# Reto: Conociendo el desempeño de los colaboradores del Área de Marketing de Socialize your knowledge
# =====================================================================
# Autor: Santos Guadalupe Facio Barraza
# Descripción: Aplicación web para mostrar el análisis de desempeño de los colaboradores de Socialize your knowledge.
# =====================================================================

# -------------------------------
# 1) Importar las librerías necesarias
# -------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from pathlib import Path

# -------------------------------
# 2) Configuración de la página
# -------------------------------
st.set_page_config(
    page_title="Desempeño de Colaboradores | Socialize your knowledge",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# 3) Despliegue del título y descripción de la aplicación web
# -------------------------------
st.title("📊 Análisis de Desempeño de Colaboradores")
st.header("Aplicación para mostrar el análisis de desempeño de los colaboradores de la empresa")
st.markdown("---")
st.subheader("Instrucciones:")
st.markdown("""
⬅️ Ajusta los filtros para analizar indicadores, identificar **fortalezas** y **áreas de oportunidad**, y con ello mejorar la calidad de los servicios.
""")
st.markdown("---")

# -------------------------------
# 4) Despliegue del logotipo de la empresa en un contenedor lateral
# -------------------------------
with st.sidebar:
    st.header("🌟Socialize your knowledge")
    logo_path = Path("logo.png")
    if logo_path.exists():
        st.image(str(logo_path))
    st.markdown("---")

# -------------------------------
# 5) Carga y preparación de datos, utilizando el archivo .csv proporcionado
# -------------------------------
@st.cache_data(show_spinner=False)
def load_data(default_path: str = "Employee_data.csv") -> pd.DataFrame:
    p = Path(default_path)
    if p.exists():
        df = pd.read_csv(p)
    else:
        # Opción para cargar manualmente si no está el CSV local
        uploaded = st.sidebar.file_uploader("Sube el archivo employee_data.csv", type=["csv"])
        if uploaded is None:
            st.warning("No se encontró **Employee_data.csv**. Sube el archivo para continuar.")
            st.stop()
        df = pd.read_csv(uploaded)

    # Normalización de tipos
    date_cols = ["birth_date", "hiring_date", "last_performance_date"]
    for c in date_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    # Asegurar tipos numéricos
    num_cols = ["age", "salary", "performance_score", "average_work_hours", "satisfaction_level", "absences"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

df = load_data()

# Validación mínima de columnas requeridas
required_cols = [
    "name_employee","birth_date","age","gender","marital_status","hiring_date",
    "position","salary","performance_score","last_performance_date",
    "average_work_hours","satisfaction_level","absences"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Faltan columnas requeridas en el CSV: {missing}")
    st.stop()

# -------------------------------
# 6) Aplicación de controles para selección de filros (Género, Puntaje, Estado civil)
# -------------------------------
with st.sidebar:
    st.header("⚡Filtros")

    # Selección de género
    genders = ["Todos"] + sorted([g for g in df["gender"].dropna().unique()])
    gender_sel = st.selectbox("Género", options=genders, index=0)

    # Rango de puntaje de desempeño del empleado
    min_ps = int(np.nanmin(df["performance_score"]))
    max_ps = int(np.nanmax(df["performance_score"]))
    perf_range = st.slider("Rango de puntaje de desempeño", min_ps, max_ps, (min_ps, max_ps), step=1)

    # Estado civil del empleado
    marital = ["Todos"] + sorted([m for m in df["marital_status"].dropna().unique()])
    marital_sel = st.selectbox("Estado civil", options=marital, index=0)

# Aplicación de filtros
mask = (
    (df["performance_score"].between(perf_range[0], perf_range[1])) &
    ((df["gender"] == gender_sel) if gender_sel != "Todos" else True) &
    ((df["marital_status"] == marital_sel) if marital_sel != "Todos" else True)
)
df_f = df.loc[mask].copy()

st.markdown(f"**Registros filtrados:** {len(df_f):,} de {len(df):,}")

# -------------------------------
# 7) Indicadores principales (KPI)
# -------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Salario promedio", f"${df_f['salary'].mean():,.0f}")
with col2:
    st.metric("Puntaje promedio", f"{df_f['performance_score'].mean():.2f}")
with col3:
    st.metric("Horas promedio/mes", f"{df_f['average_work_hours'].mean():.1f}")
with col4:
    st.metric("Satisfacción promedio", f"{df_f['satisfaction_level'].mean():.2f}")

st.markdown("---")

# -------------------------------
# 8) GRÁFICO: Distribución de puntajes de desempeño
# -------------------------------
st.subheader("Distribución de puntajes de desempeño")
hist = (
    alt.Chart(df_f)
    .mark_bar()
    .encode(
        x=alt.X("performance_score:Q", bin=alt.Bin(step=1), title="Puntaje de desempeño"),
        y=alt.Y("count()", title="Número de empleados"),
        tooltip=[alt.Tooltip("count()", title="Empleados")]
    )
    .properties(height=300)
)
st.altair_chart(hist, use_container_width=True)

# -------------------------------
# 9) GRÁFICO: Promedio de horas trabajadas por género
# -------------------------------
st.subheader("Promedio de horas trabajadas por género")
hours_by_gender = (
    df_f.groupby("gender", dropna=False)["average_work_hours"]
    .mean()
    .reset_index()
    .rename(columns={"average_work_hours": "avg_hours"})
)

bar = (
    alt.Chart(hours_by_gender)
    .mark_bar()
    .encode(
        x=alt.X("gender:N", title="Género", sort=alt.SortField("gender")),
        y=alt.Y("avg_hours:Q", title="Horas promedio/mes"),
        tooltip=[alt.Tooltip("avg_hours:Q", title="Horas promedio", format=".1f")]
    )
    .properties(height=300)
)
st.altair_chart(bar, use_container_width=True)

# -------------------------------
# 10) GRÁFICO: Edad vs Salario
# -------------------------------
st.subheader("Edad de los empleados vs salario")
scatter_age_salary = (
    alt.Chart(df_f.dropna(subset=["age", "salary"]))
    .mark_circle(size=60, opacity=0.6)
    .encode(
        x=alt.X("age:Q", title="Edad"),
        y=alt.Y("salary:Q", title="Salario"),
        tooltip=[
            alt.Tooltip("name_employee:N", title="Empleado"),
            alt.Tooltip("position:N", title="Puesto"),
            alt.Tooltip("age:Q", title="Edad"),
            alt.Tooltip("salary:Q", title="Salario", format=",.0f"),
        ]
    )
    .properties(height=350)
)
st.altair_chart(scatter_age_salary, use_container_width=True)

# -------------------------------
# 11) GRÁFICO: Horas trabajadas vs Puntaje
# -------------------------------
st.subheader("Relación entre promedio de horas trabajadas y puntaje de desempeño")
scatter_hours_perf = (
    alt.Chart(df_f.dropna(subset=["average_work_hours", "performance_score"]))
    .mark_circle(size=60, opacity=0.6)
    .encode(
        x=alt.X("average_work_hours:Q", title="Horas promedio/mes"),
        y=alt.Y("performance_score:Q", title="Puntaje de desempeño"),
        tooltip=[
            alt.Tooltip("name_employee:N", title="Empleado"),
            alt.Tooltip("position:N", title="Puesto"),
            alt.Tooltip("average_work_hours:Q", title="Horas/mes", format=".1f"),
            alt.Tooltip("performance_score:Q", title="Puntaje"),
        ]
    )
    .properties(height=350)
)
st.altair_chart(scatter_hours_perf, use_container_width=True)

st.markdown("---")

# -------------------------------
# 12) Desplegar conclusiones sobre el análisis mostrado en la aplicación web.
# -------------------------------
st.subheader("Conclusiones sobre el análisis mostrado en la aplicación web.")
def safe_corr(a, b):
    if a.dropna().empty or b.dropna().empty:
        return np.nan
    return a.corr(b)

corr_age_salary = safe_corr(df_f["age"], df_f["salary"])
corr_hours_perf = safe_corr(df_f["average_work_hours"], df_f["performance_score"])
avg_by_perf = df_f.groupby("performance_score")["satisfaction_level"].mean().round(2)

st.markdown(f"""
- Correlación **edad–salario**: `{corr_age_salary:.2f}` (valores cercanos a ±1 indican relación fuerte).
- Correlación **horas–puntaje**: `{corr_hours_perf:.2f}`.
- **Satisfacción promedio por puntaje**:
""")
st.dataframe(avg_by_perf.reset_index().rename(columns={"performance_score":"Puntaje","satisfaction_level":"Satisfacción promedio"}))

st.info("❗Estas métricas se ofrecen como guía. Utiliza los filtros para revelar patrones por género y estado civil.")

# -------------------------------
# 13) PIE DE PÁGINA
# -------------------------------
st.caption("📈 © 2025 Socialize your knowledge · Dashboard de analítica de desempeño - Desarrollado por Santos Guadalupe Facio Barraza💡")
