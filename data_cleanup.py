import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date

def dataset_downlaod_df():
    print("Downloading data from JHU")
# Dataset
    df_confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    df_deaths = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
    df_recovered = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
    #df_covid19 = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv")
    #df_table = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_time.csv",parse_dates=['Last_Update'])
    ## Rename Coloum Name 
    df_confirmed = df_confirmed.rename(columns={"Province/State":"State","Country/Region": "Country"})
    df_deaths = df_deaths.rename(columns={"Province/State":"State","Country/Region": "Country"})
    df_recovered = df_recovered.rename(columns={"Province/State":"State","Country/Region": "Country"})
    print("Extracing Dates and melt dataframes in longer formating")
    dates = df_confirmed.columns[4:]
    # melt dataframes in longer format
    df_confirmed_long = df_confirmed.melt(id_vars=['State', 'Country', 'Lat', 'Long'], 
                            value_vars=dates, var_name='Date', value_name='Confirmed')

    df_deaths_long = df_deaths.melt(id_vars=['State', 'Country', 'Lat', 'Long'], 
                            value_vars=dates, var_name='Date', value_name='Deaths')

    df_recovered_long = df_recovered.melt(id_vars=['State', 'Country', 'Lat', 'Long'], 
                            value_vars=dates, var_name='Date', value_name='Recovered')
    
    #print("Coivd 19 Confirmed Date frame Size" + df_confirmed_long.shape)
    #print("Coivd 19 Deaths Date frame Size" + df_deaths_long.shape)
    #print("Coivd 19 Recovery Date frame Size" + df_recovered_long.shape)
    
    print("Merging Confirmed, Deaths and Recovery to one dataframe")
    
    covid19_table = pd.merge(left=df_confirmed_long, right=df_deaths_long, how='left',
                      on=['State', 'Country', 'Date', 'Lat', 'Long'])
    covid19_table = pd.merge(left=covid19_table, right=df_recovered_long, how='left',
                      on=['State', 'Country', 'Date', 'Lat', 'Long'])
    
    print("Data Cleanup")
    covid19_table['Recovered'] = covid19_table['Recovered'].fillna(0)
    covid19_table['Recovered'] = covid19_table['Recovered'].astype('int')
    print("Change Country Name to formal Name ")
    my_dict_pycountry = {
    'US': 'United States', 
    'Bolivia': 'Bolivia, Plurinational State of',
    'Brunei': 'Brunei Darussalam',
    'Burma': 'Myanmar',
    'Iran': 'Iran, Islamic Republic of',
    'Laos':"Lao People's Democratic Republic",
    'Russia':'Russian Federation',
    'Korea, South': 'South Korea', 
    'Taiwan*': 'Taiwan',
    'Congo (Kinshasa)': 'Congo, the Democratic Republic of the',
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Reun:ion": "Réunion",
    "Congo (Brazzaville)": "Republic of the Congo",
    'Bahamas, The': 'Bahamas',
    'Gambia, The': 'Gambia'
     }
    for key, value in my_dict_pycountry.items():
        covid19_table.loc[covid19_table['Country'] == key, "Country"] = value
    print("Data Cleaning Level 2")
    # removing canada's recovered values
    covid19_table = covid19_table[covid19_table['State'].str.contains('Recovered')!=True]

    # removing county wise data to avoid double counting
    covid19_table = covid19_table[covid19_table['State'].str.contains(',')!=True]
    # Cleaning data
    # =============

    # fixing Country values
    covid19_table.loc[covid19_table['State']=='Greenland', 'Country'] = 'Greenland'

    # Active Case = confirmed - deaths - recovered
    covid19_table['Active'] = (covid19_table['Confirmed'] - covid19_table['Deaths'] - covid19_table['Recovered'])

    # filling missing values 
    covid19_table[['State']] = covid19_table[['State']].fillna('')
    covid19_table[['Confirmed', 'Deaths', 'Recovered', 'Active']] = covid19_table[['Confirmed', 'Deaths', 'Recovered', 'Active']].fillna(0)

    # fixing datatypes
    covid19_table['Recovered'] = covid19_table['Recovered'].astype(int)

    covid19_table['Date'] = pd.to_datetime(covid19_table['Date'])
    print("Data Framed Created " + str(max(covid19_table['Date'])))
    return covid19_table

def groupby_day_country(covid19_table):
    # Grouped by day, country
    # =======================
    print ( "Group  Data Frame by Day and country and insert new Colomuns like New Cases , New Death and New Recovery")
    covid19_country = covid19_table.groupby(['Date', 'Country'])['Confirmed', 'Deaths', 'Recovered', 'Active'].sum().reset_index()

    # new cases ======================================================
    temp = covid19_country.groupby(['Country', 'Date', ])['Confirmed', 'Deaths', 'Recovered']
    temp = temp.sum().diff().reset_index()

    mask = temp['Country'] != temp['Country'].shift(1)

    temp.loc[mask, 'Confirmed'] = np.nan
    temp.loc[mask, 'Deaths'] = np.nan
    temp.loc[mask, 'Recovered'] = np.nan

    # renaming columns
    temp.columns = ['Country', 'Date', 'New cases', 'New deaths', 'New recovered']
    # =================================================================

    # merging new values
    covid19_country = pd.merge(covid19_country, temp, on=['Country', 'Date'])

    # filling na with 0
    covid19_country = covid19_country.fillna(0)

    # fixing data types
    cols = ['New cases', 'New deaths', 'New recovered']
    covid19_country[cols] = covid19_country[cols].astype('int')

    covid19_country['New cases'] = covid19_country['New cases'].apply(lambda x: 0 if x<0 else x)

    return covid19_country

def day_wise_dataframe(covid19_country):
# Day wise
# ========
    # table
    print("Combine Dataframe Date wise")
    day_wise = covid19_country.groupby('Date')['Confirmed', 'Deaths', 'Recovered', 'Active', 'New cases', 'New deaths'].sum().reset_index()

    # number cases per 100 cases
    day_wise['Deaths / 100 Cases'] = round((day_wise['Deaths']/day_wise['Confirmed'])*100, 2)
    day_wise['Recovered / 100 Cases'] = round((day_wise['Recovered']/day_wise['Confirmed'])*100, 2)
    day_wise['Deaths / 100 Recovered'] = round((day_wise['Deaths']/day_wise['Recovered'])*100, 2)

    # no. of countries
    day_wise['No. of countries'] = covid19_country[covid19_country['Confirmed']!=0].groupby('Date')['Country'].unique().apply(len).values

    # fillna by 0
    cols = ['Deaths / 100 Cases', 'Recovered / 100 Cases', 'Deaths / 100 Recovered']
    day_wise[cols] = day_wise[cols].fillna(0)

    return day_wise

def country_wise_dataframe(covid19_country):
    print("Ccombine Dateframe Country Wise")
    # Country wise
    # ============
    # getting latest values
    country_wise = covid19_country[covid19_country['Date']==max(covid19_country['Date'])].reset_index(drop=True).drop('Date', axis=1)
    # group by country
    country_wise = country_wise.groupby('Country')['Confirmed', 'Deaths', 'Recovered', 'Active', 'New cases'].sum().reset_index()
    # per 100 cases
    country_wise['Deaths / 100 Cases'] = round((country_wise['Deaths']/country_wise['Confirmed'])*100, 2)
    country_wise['Recovered / 100 Cases'] = round((country_wise['Recovered']/country_wise['Confirmed'])*100, 2)
    country_wise['Deaths / 100 Recovered'] = round((country_wise['Deaths']/country_wise['Recovered'])*100, 2)

    cols = ['Deaths / 100 Cases', 'Recovered / 100 Cases', 'Deaths / 100 Recovered']
    country_wise[cols] = country_wise[cols].fillna(0)

    return country_wise
    
def combine_dataframe_country_population(country_wise):
    # load population dataset
    pop = pd.read_csv("population_by_country_2020.csv")

    # select only population
    pop = pop.iloc[:, :2]

    # rename column names
    pop.columns = ['Country/Region', 'Population']
    pop = pop.rename(columns={"Country/Region": "Country"})
    # merged data
    country_wise = pd.merge(country_wise, pop, on='Country', how='left')

    # # update population
    # cols = ['Burma', 'Congo (Brazzaville)', 'Congo (Kinshasa)', "Cote d'Ivoire", 'Czechia', 
    #         'Kosovo', 'Saint Kitts and Nevis', 'Saint Vincent and the Grenadines', 
    #         'Taiwan*', 'US', 'West Bank and Gaza', 'Sao Tome and Principe']
    # pops = [54409800, 89561403, 5518087, 26378274, 10708981, 1793000, 
    #         53109, 110854, 23806638, 330541757, 4543126, 219159]
    # for c, p in zip(cols, pops):
    #     country_wise.loc[country_wise['Country/Region']== c, 'Population'] = p

    # missing values
    # country_wise.isna().sum()
    # country_wise[country_wise['Population'].isna()]['Country/Region'].tolist()

    # Cases per population
    country_wise['Cases / Million People'] = round((country_wise['Confirmed'] / country_wise['Population']) * 1000000)

    return country_wise
def combine_df_from_week(country_wise, covid19_table):
    today = covid19_table[covid19_table['Date']==max(covid19_table['Date'])].reset_index(drop=True).drop('Date', axis=1)[['Country', 'Confirmed']]
    last_week = covid19_table[covid19_table['Date']==max(covid19_table['Date'])-timedelta(days=7)].reset_index(drop=True).drop('Date', axis=1)[['Country', 'Confirmed']]

    temp = pd.merge(today, last_week, on='Country', suffixes=(' today', ' last week'))

    # temp = temp[['Country/Region', 'Confirmed last week']]
    temp['1 week change'] = temp['Confirmed today'] - temp['Confirmed last week']

    temp = temp[['Country', 'Confirmed last week', '1 week change']]

    country_wise = pd.merge(country_wise, temp, on='Country')

    country_wise['1 week % increase'] = round(country_wise['1 week change']/country_wise['Confirmed last week']*100, 2)

    return country_wise