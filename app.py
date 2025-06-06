import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import itertools

df = pd.read_csv('startup_clean.csv')
df['investors name'] = df['investors name'].fillna('Undisclosed')
df['investors name']= df['investors name'].str.replace('\\\\xc2\\\\xa0', '')
df['investors name']= df['investors name'].str.replace('\\\\n', ' ')
df['investors name']= df['investors name'].str.replace('\\\\xe2\\\\x80\\\\x99s', '')
df['date'] = df['date'].replace({'05/072018':'05/07/2018', '01/07/015':'01/07/2015', '22/01//2015':'22/01/2015'})
df['date'] = pd.to_datetime(df['date'],format='mixed')
df['investor'] =df['investors name'].str.split(',')

st.set_page_config(page_title='Startup Funding Analysis', layout='wide')

def load_startup_details(startup):
    st.title(startup)

    col1, col2,col3 = st.columns(3)
    with col1:
        #display the vertical 
        vertical = df[df['startup'] == startup]['vertical']
        if not vertical.values.any():
            vertical = 'Not Available'
        else:
            vertical = vertical.values[0]
        st.metric(label="Vertical", value=vertical)

    with col2:
        #display the city
        city = df[df['startup'] == startup]['city']
        if not city.values.any():
            city = 'Not Available'
        else:
            city = city.values[0]
        st.metric(label="City", value=city)

    with col3:
        # Total amount invested in the startup
        amount = df[df['startup'] == startup]['amount'].sum()
        st.metric(label="Total Amount Invested", value=f"${amount:,.2f}")

    # Display the last 5 investments
    st.subheader('Last 5 Investments')
    last_5_df = df[df['startup'] == startup].head()[['date', 'investors name', 'amount']]
    st.dataframe(last_5_df)

    c1, c2 = st.columns(2)
    with c1:
        # display all the investors
        st.subheader('Investors')
        investor_lists = df[df['startup'] == startup]['investor'].dropna().tolist()
        flat_investors = list(itertools.chain.from_iterable(
            i if isinstance(i, list) else [i] for i in investor_lists
        ))
        def clean_investor_name(name):
            name = str(name).strip()
            name = re.sub(r'[^A-Za-z0-9&\-\s\']+', '', name)
            name = re.sub(r'\s+', ' ', name)
            return name.title()
        investor_list = sorted(set(clean_investor_name(inv) for inv in flat_investors if inv and inv.strip()))
        investor_series = pd.Series(investor_list)
        st.dataframe(investor_series)

    with c2:
        # display the year wise investment
        st.subheader('Year Wise Investment')
        df['year'] = df['date'].dt.year
        year_wise_investment = df[df['startup'] == startup].groupby('year')['amount'].sum()
        fig, ax = plt.subplots()
        ax.plot(year_wise_investment.index, year_wise_investment.values, marker='o')
        ax.set_xlabel('Year')
        ax.set_ylabel('Amount Invested')
        ax.set_title(f'Year Wise Investment for {startup}')
        st.pyplot(fig)
    
def clean_startup_name(name):
    try:
        name = name.encode('latin1').decode('utf-8', 'ignore')
    except:
        pass
    name = name.strip()
    name = re.sub(r'^https?://\S+', '', name)
    name = re.sub(r'[^A-Za-z0-9&\-\s\']+', '', name)
    name = name.title()
    name = re.sub(r'\s+', ' ', name)
    return name

df['Startup Name Cleaned'] = df['startup'].astype(str).apply(clean_startup_name)
unique_names = sorted(set(name for name in df['Startup Name Cleaned'] if name))

def load_overall_analysis():
    #Total amount invested
    c1, c2, c3, c4= st.columns(4)
    total = round(df.amount.sum())
    with c2:
        st.metric(label="Total Amount Invested", value=f"${total:,}")

    #max amount infused in the startup
    max_amount = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(3)
    with c1:
        st.metric(label="Maximum Amount Invested in a Startup", value=f"${max_amount.max():,}")

    # Avg funding size
    avg = df.groupby('startup')['amount'].sum().mean()
    with c3:
        st.metric(label="Average Funding Size", value=f"${avg:,.2f}")

    #total funded startups
    total_startups = df['startup'].nunique()
    with c4:
        st.metric(label="Total Funded Startups", value=f"{total_startups:,}")


    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Top 3 Startups by Maximum Investment')
        fig, ax = plt.subplots()
        ax.bar(max_amount.index, max_amount.values)
        st.pyplot(fig)

    with col2:
        st.subheader('Top 5 Verticals by Total Investment')
        vertical = df.groupby('vertical')['amount'].sum().sort_values(ascending=False).head(5)
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical, labels=vertical.index, autopct='%1.1f%%')
        st.pyplot(fig1)

    co1, co2 = st.columns(2)
    with co1:
        st.subheader('Top 5 Cities by Total Investment')
        city = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(5)
        fig2, ax2 = plt.subplots()
        ax2.pie(city, labels=city.index, autopct='%1.1f%%')
        st.pyplot(fig2)
    with co2:
        st.subheader('Month on Month Investment Trend')
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year

        selected_option = st.selectbox('Select Option', ['Number of Startups Funded', 'Total Amount Invested'])
        if selected_option == 'Number of Startups Funded':
            temp2 = df.groupby(['year', 'month'])['amount'].count().reset_index()
        else:
            temp2 = df.groupby(['year', 'month'])['amount'].sum().reset_index()

        temp2['x_axis'] = temp2['month'].astype('str') + '-' + temp2['year'].astype('str')
        
        temp2['x_axis'] = pd.to_datetime(temp2['x_axis'], format='%m-%Y')
        temp2 = temp2.sort_values(by='x_axis')
        fig3, ax3 = plt.subplots()
        ax3.plot(temp2['x_axis'], temp2['amount'], marker='o')
        st.pyplot(fig3)
        
def load_investor_details(investor):
    st.title(investor)
    last_5_df = df[df['investors name'].str.contains(investor)].head()[['date', 'startup', 'vertical', 'city', 'amount']]
    
    # Most recent investment
    st.subheader('Most Recent Investments')
    st.dataframe(last_5_df)

    col1, col2 = st.columns(2)
    with col1:
        # biggest Investments
        big = df[df['investors name'].str.contains(investor)].groupby('startup')['amount'].sum().sort_values(ascending=False).head(7)
        st.subheader('Biggest Investments')
        fig, ax = plt.subplots()
        ax.bar(big.index, big.values)
        st.pyplot(fig)

    with col2:
        vertical= df[df['investors name'].str.contains(investor)].groupby('vertical')['amount'].sum().sort_values(ascending=False).head(7)
        st.subheader('Verticals of Investment')
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical, labels=vertical.index, autopct='%1.1f%%')
        st.pyplot(fig1)

    c1, c2 = st.columns(2)
    with c1:
        df['year'] = df['date'].dt.year
        year = df[df['investors name'].str.contains(investor)].groupby('year')['amount'].sum()
        st.subheader('Investments by Year')
        fig2, ax2 = plt.subplots()
        ax2.plot(year.index, year.values)
        st.pyplot(fig2)

st.sidebar.title('Startup Funding Analysis')

option =st.sidebar.selectbox('Select Option', ['Overall Analysis', 'Startup Analysis', 'Investor Analysis'])

if option=='Overall Analysis':
    st.title('Overall Analysis ')
    # btn0 = st.sidebar.button('Show Overall Analysis')
    load_overall_analysis()
elif option == 'Startup Analysis':
    selected_startup = st.sidebar.selectbox('Select Startup', unique_names)
    btn1 = st.sidebar.button('Find Startup Details')
    st.title('Startup Analysis ')

    if btn1:
        load_startup_details(selected_startup)
elif option == 'Investor Analysis':
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(set(df['investors name'].str.split(',').sum()), reverse=True))
    btn2 = st.sidebar.button('Find Investor Details')
    st.title('Investor Analysis ')
    
    if btn2:
        load_investor_details(selected_investor)
