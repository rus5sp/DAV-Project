import streamlit as st
import pandas as pd
import plotly.express as px


timeseries_eco_plot_configs = {
    'birth_count': {'title': 'Birth Count Over Time', 'ylabel': 'Birth Count'},
    'employed_population': {'title': 'Employed Population Over Time', 'ylabel': 'Employed Population'},
    'gdp_per_capita': {'title': 'GDP Per Capita Over Time', 'ylabel': 'GDP Per Capita'},
    'monthly_salary': {'title': 'Monthly Salary Over Time', 'ylabel': 'Monthly Salary'},
    'unemployment_rate': {'title': 'Unemployment Rate Over Time', 'ylabel': 'Unemployment Rate'},
    'industrial_production': {'title': 'Industrial Production Over Time', 'ylabel': 'Industrial Production'}
}

timeseries_edu_plot_configs = {
    'inst_total': {'title': 'Total Institutions Over Time', 'ylabel': 'Total Institutions'},
    'teachers_total': {'title': 'Total Teachers Over Time', 'ylabel': 'Total Teachers'},
    'grad_total': {'title': 'Total Graduates Over Time', 'ylabel': 'Total Graduates'},
    'edu_exp_total': {'title': 'Total Education Expenditure Over Time', 'ylabel': 'Total Education Expenditure'}
}


df = pd.read_csv('data/final_dataset.csv', index_col='year')
data_dictionary = pd.read_csv('data/data_dictionary.csv')


st.set_page_config(layout="wide")
st.title("Kyrgyzstan Education and Economy Dashboard")


def plot_timeseries(df, config_dict, key_prefix):
    selected = st.selectbox(
        "Select metric:",
        list(config_dict.keys()),
        key=key_prefix
    )
    config = config_dict[selected]
    fig = px.line(
        df, x=df.index, y=selected,
        title=config['title'],
        labels={'year': 'Year', selected: config['ylabel']}
    )
    st.plotly_chart(fig, use_container_width=True)

    return selected, config['title']


def show_statistics(data, column_name, display_name):
    st.subheader(f"📊 Descriptive Statistics: {display_name}")
    
    stats = {
        'Mean': round(data[column_name].mean(), 2),
        'Median': round(data[column_name].median(), 2),
        'Std Dev': round(data[column_name].std(), 2),
        'Min': round(data[column_name].min(), 2),
        'Max': round(data[column_name].max(), 2),
        'Range': round(data[column_name].max() - data[column_name].min(), 2),
    }
    
    stats_df = pd.DataFrame(stats.items(), columns=['Statistic', 'Value'])
    st.dataframe(stats_df, use_container_width=True, hide_index=True)


st.header("Dataset Description")
st.dataframe(df)
st.dataframe(data_dictionary)

st.header("Time Series Plots")

st.subheader("Economy Metrics")
selected_eco, title_eco = plot_timeseries(df, timeseries_eco_plot_configs, "eco")
show_statistics(df, selected_eco, title_eco)

st.subheader("Education Metrics")
selected_edu, title_edu = plot_timeseries(df, timeseries_edu_plot_configs, "edu")
show_statistics(df, selected_edu, title_edu)


st.header('Composition of Education Expenditure by Level')

fig = px.bar(
    (df[['edu_exp_preschool', 'edu_exp_secondary', 'edu_exp_higher']] / 1_000_000_000)
        .reset_index()
        .melt(id_vars='year', var_name='Level', value_name='Expenditure')
        .assign(Level=lambda x: x['Level'].map({
            'edu_exp_preschool': 'Preschool Expenditure',
            'edu_exp_secondary': 'Secondary School Expenditure',
            'edu_exp_higher': 'Higher Education Expenditure',
        })),
    x='year',
    y='Expenditure',
    color='Level',
    barmode='stack',
    labels={
        'Expenditure': 'Expenditure (in Billions of Som)',
        'year': 'Year',
        'Level': 'Education Level',
    },
    height=600,
)
fig.update_layout(yaxis_tickformat=',')
st.plotly_chart(fig, use_container_width=True)


st.header('Education Expenditure vs. GDP per Capita (Indexed)')

edu_base = df['edu_exp_total'].iloc[0]
gdp_base = df['gdp_per_capita'].iloc[0]

fig = px.line(
    pd.DataFrame({
        'Education Expenditure': df['edu_exp_total'] / edu_base * 100,
        'GDP per Capita': df['gdp_per_capita'] / gdp_base * 100,
    }, index=df.index)
        .reset_index()
        .melt(id_vars='year', var_name='Indicator', value_name='Index'),
    x='year',
    y='Index',
    color='Indicator',
    labels={'year': 'Year', 'Index': 'Index (2011 = 100)', 'Indicator': ''},
    height=600,
)
st.plotly_chart(fig, use_container_width=True)


st.header('Education Expenditure vs. Graduates with Cost per Graduate as Bubble Size')

cost_per_grad = df['edu_exp_total'] / df['grad_total']

fig = px.scatter(
    df.assign(
        cost_per_grad=cost_per_grad,
        edu_exp_billions=df['edu_exp_total'] / 1_000_000_000,
    ),
    x='grad_total',
    y='edu_exp_billions',
    size='cost_per_grad',
    size_max=40,
    opacity=0.7,
    labels={
        'grad_total': 'Graduates',
        'edu_exp_billions': 'Expenditure (in Billions of Som)',
        'cost_per_grad': 'Cost per Graduate',
    },
    height=600,
)
st.plotly_chart(fig, use_container_width=True)


st.header('Correlation Between Graduates and Employment/Unemployment')

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(px.scatter(
        df.reset_index(),
        x='grad_total', y='unemployment_rate',
        trendline='ols',
        labels={'grad_total': 'Graduates', 'unemployment_rate': 'Unemployment Rate'},
    ), use_container_width=True)

with col2:
    st.plotly_chart(px.scatter(
        df.assign(employed_millions=df['employed_population'] / 1_000_000).reset_index(),
        x='grad_total', y='employed_millions',
        trendline='ols',
        labels={'grad_total': 'Graduates', 'employed_millions': 'Employed Population (in Millions of People)'},
    ), use_container_width=True)


st.header('Conclusion')
st.markdown("""
Education and economy indicators show strong correlations, but claiming causation would be overconfident given the external factors influencing both sets of variables.

In some cases, such as GDP per Capita and education expenditure, one indicator may appear to lead the other — however, the observed time gap never exceeded three years, which is too short to establish a causal relationship.

The most reasonable explanation is that education and the economy act as mutual accelerators, each needing to keep pace with the other in order to fulfill its role.
""")