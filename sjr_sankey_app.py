import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Изменение квартилей SJR (2022–2024)")

@st.cache_data
def load_data():
    df_2022 = pd.read_csv('2022.csv', sep=';', usecols=['Sourceid', 'SJR Best Quartile']).assign(Year=2022)
    df_2023 = pd.read_csv('2023.csv', sep=';', usecols=['Sourceid', 'SJR Best Quartile']).assign(Year=2023)
    df_2024 = pd.read_csv('2024.csv', sep=';', usecols=['Sourceid', 'SJR Best Quartile']).assign(Year=2024)
    for df in [df_2022, df_2023, df_2024]:
        df.rename(columns={'Sourceid': 'Journal ID', 'SJR Best Quartile': 'Quartile'}, inplace=True)
    return pd.concat([df_2022, df_2023, df_2024], ignore_index=True)

df = load_data()
df = df.drop_duplicates(['Journal ID', 'Year'])
df['Quartile'] = df['Quartile'].str.upper().str.replace(' ', '')

years = [2022, 2023, 2024]
quartiles = ['Q1', 'Q2', 'Q3', 'Q4']
colors = {
    'Q1': 'rgba(100, 180, 80, 0.8)',
    'Q2': 'rgba(230, 200, 0, 0.8)',
    'Q3': 'rgba(250, 140, 0, 0.8)',
    'Q4': 'rgba(220, 60, 50, 0.8)',
    'Без квартиля': 'rgba(80, 130, 200, 0.8)'
}

nodes = [f"{year} {q}" for year in years for q in quartiles + ['Без квартиля']]
node_indices = {name: i for i, name in enumerate(nodes)}
node_colors = [colors[name.split(' ', 1)[1]] for name in nodes]

node_x = []
node_y = []
for node in nodes:
    year = int(node.split()[0])
    if year == 2022:
        node_x.append(0.1)
    elif year == 2023:
        node_x.append(0.5)
    elif year == 2024:
        node_x.append(0.9)

    if "Без квартиля" in node:
        node_y.append(1.0)
    elif "Q1" in node:
        node_y.append(0.1)
    elif "Q2" in node:
        node_y.append(0.3)
    elif "Q3" in node:
        node_y.append(0.6)
    elif "Q4" in node:
        node_y.append(0.8)

links = {'source': [], 'target': [], 'value': [], 'color': []}
all_ids = df['Journal ID'].unique()
year_dfs = {year: df[df['Year'] == year].set_index('Journal ID') for year in years}

for jid in all_ids:
    for i in range(len(years) - 1):
        y1, y2 = years[i], years[i + 1]
        q1 = year_dfs[y1].loc[jid]['Quartile'] if jid in year_dfs[y1].index else None
        q2 = year_dfs[y2].loc[jid]['Quartile'] if jid in year_dfs[y2].index else None

        if not q1:
            continue
        if not q2 or q2 not in quartiles:
            q2 = 'Без квартиля'
        if q1 not in quartiles:
            q1 = 'Без квартиля'

        source = f"{y1} {q1}"
        target = f"{y2} {q2}"

        links['source'].append(node_indices[source])
        links['target'].append(node_indices[target])
        links['value'].append(1)
        links['color'].append(colors[q1])

link_df = pd.DataFrame(links)
link_df = link_df.groupby(['source', 'target', 'color']).agg({'value': 'sum'}).reset_index()

fig = go.Figure(go.Sankey(
    arrangement="fixed",
    node=dict(
        pad=10,
        thickness=15,
        line=dict(color="black", width=0.5),
        label=nodes,
        color=node_colors,
        x=node_x,
        y=node_y
    ),
    link=dict(
        source=link_df['source'],
        target=link_df['target'],
        value=link_df['value'],
        color=link_df['color'],
        hovertemplate='%{source.label} → %{target.label}<br>Журналов: %{value:.0f}<extra></extra>',
        hoverinfo="skip"
    )
))

fig.update_layout(
    height=1000,
    plot_bgcolor='rgba(255,255,255,1)'
)

st.plotly_chart(fig, use_container_width=True)
