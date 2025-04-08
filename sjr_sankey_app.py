import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Настройка страницы
st.set_page_config(
    page_title="Диаграмма изменения квартилей SJR",
    layout="wide",
    initial_sidebar_state="collapsed"
)
#st.title("Изменение квартилей SJR (2022–2024)")
st.markdown("<h1 style='text-align: center;'>Изменение квартилей SJR (2022–2024)</h1>", unsafe_allow_html=True)


# Убираем Streamlit-заголовок (если не нужен, можно закомментировать)
# st.title("Изменение квартилей SJR (2022–2024)")

# Загрузка данных
df_2022 = pd.read_csv('2022.csv', sep=';', usecols=['Sourceid', 'SJR Best Quartile']).assign(Year=2022)
df_2023 = pd.read_csv('2023.csv', sep=';', usecols=['Sourceid', 'SJR Best Quartile']).assign(Year=2023)
df_2024 = pd.read_csv('2024.csv', sep=';', usecols=['Sourceid', 'SJR Best Quartile']).assign(Year=2024)

# Переименование и объединение
for df in [df_2022, df_2023, df_2024]:
    df.rename(columns={'Sourceid': 'Journal ID', 'SJR Best Quartile': 'Quartile'}, inplace=True)

df = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)
df = df.drop_duplicates(['Journal ID', 'Year'])
df['Quartile'] = df['Quartile'].str.upper().str.replace(' ', '')

# Параметры
years = [2022, 2023, 2024]
quartiles = ['Q1', 'Q2', 'Q3', 'Q4']

quartile_colors = {
    'Q1': 'rgba(100, 180, 80, 0.8)',
    'Q2': 'rgba(230, 200, 0, 0.8)',
    'Q3': 'rgba(250, 140, 0, 0.8)',
    'Q4': 'rgba(220, 60, 50, 0.8)',
    'Без квартиля': 'rgba(80, 130, 200, 0.8)'
}

# Узлы
quartile_nodes = [f"{year} {q}" for year in years for q in quartiles]
no_quartile_nodes = [f"{year} Без квартиля" for year in years]
all_nodes = quartile_nodes + no_quartile_nodes
node_indices = {node: idx for idx, node in enumerate(all_nodes)}

# Цвета узлов
node_colors = []
for node in all_nodes:
    q = node.split(' ', 1)[1]
    node_colors.append(quartile_colors.get(q, "rgba(150, 150, 150, 0.6)"))

# Координаты узлов (не трогаем!)
node_y = []
node_x = []
for node in all_nodes:
    year_str = node.split()[0]
    if year_str == "2022":
        node_x.append(0.15)
    elif year_str == "2023":
        node_x.append(0.5)
    elif year_str == "2024":
        node_x.append(0.85)

    if "Без квартиля" in node:
        node_y.append(1.08)
    elif "Q1" in node:
        node_y.append(0.15)
    elif "Q2" in node:
        node_y.append(0.3)
    elif "Q3" in node:
        node_y.append(0.5)
    elif "Q4" in node:
        node_y.append(0.83)

# Подготовка связей
sankey_links = {'source': [], 'target': [], 'value': [], 'color': []}
journals_2022 = set(df_2022['Journal ID'])
journals_2023 = set(df_2023['Journal ID'])
journals_2024 = set(df_2024['Journal ID'])
all_journal_ids = journals_2022.union(journals_2023).union(journals_2024)

for journal_id in all_journal_ids:
    journal_by_year = {}
    for year, year_df in zip(years, [df_2022, df_2023, df_2024]):
        journal_data = year_df[year_df['Journal ID'] == journal_id]
        if not journal_data.empty:
            quartile = journal_data['Quartile'].iloc[0]
            journal_by_year[year] = quartile if quartile in quartiles else 'Без квартиля'

    for i in range(len(years) - 1):
        y1 = years[i]
        y2 = years[i + 1]

        q1 = journal_by_year.get(y1)
        q2 = journal_by_year.get(y2)

        if not q1:
            continue

        source = f"{y1} {q1}"
        target = f"{y2} {q2 if q2 else 'Без квартиля'}"
        color = quartile_colors.get(q1, quartile_colors['Без квартиля'])

        sankey_links['source'].append(node_indices[source])
        sankey_links['target'].append(node_indices[target])
        sankey_links['value'].append(1)
        sankey_links['color'].append(color)

# Группировка и сортировка
links_df = pd.DataFrame(sankey_links)
links_df = links_df.groupby(['source', 'target', 'color']).agg({'value': 'sum'}).reset_index()
links_df = links_df.sort_values('value', ascending=False)

# Построение интерактивной Sankey-диаграммы
fig = go.Figure(go.Sankey(
    arrangement="fixed",
    node=dict(
        pad=25,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=all_nodes,
        color=node_colors,
        x=node_x,
        y=node_y
    ),
    link=dict(
        source=links_df['source'],
        target=links_df['target'],
        value=links_df['value'],
        color=links_df['color'],
        hovertemplate='%{source.label} → %{target.label}<br>Журналов: %{value:.0f}<extra></extra>'
    )
))

fig.update_layout(
    height=900,
      width=1800,
    plot_bgcolor='rgba(250, 250, 250, 0.9)',
    margin=dict(l=20, r=20, t=10, b=180),
    autosize=True
)

# Отображение в Streamlit
st.plotly_chart(fig, use_container_width=True, config={
    "displayModeBar": False,
    "responsive": True
})

# Легенда
with st.expander("ℹ️ О диаграмме"):
    st.markdown("""
    Эта диаграмма Sankey показывает изменение квартилей журналов в базе **SJR** с **2022 по 2024 год**.

    **Цветовая кодировка:**
    - 🟩 **Зеленый** — Q1 (верхний квартиль)
    - 🟨 **Желтый** — Q2
    - 🟧 **Оранжевый** — Q3
    - 🟥 **Красный** — Q4
    - 🟦 **Синий** — Без квартиля

    Ширина потоков между блоками отражает количество журналов, перешедших между квартилями.
    """)
