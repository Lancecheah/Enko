import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from pytickersymbols import PyTickerSymbols
import datetime as dt
import plotly.graph_objects as go
from plotly import tools
import plotly
import requests
import copy
import matplotlib.pyplot as plt
import re
from wordcloud import WordCloud, STOPWORDS
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import snscrape.modules.twitter as sntwitter
import nltk
import operator
import time
timestr = time.strftime("%Y%m%d-%H%M%S")
import base64
st.set_page_config(layout="wide")

nltk.download('vader_lexicon')  # required for Sentiment Analysis

stock_data = PyTickerSymbols()
indices = stock_data.get_all_indices()


#Top 3 metrics of US index
tickers = ['^DJI', '^GSPC', '^IXIC']
start = dt.datetime.today() - dt.timedelta(4)
end = dt.datetime.today()
cl_price = pd.DataFrame()
for ticker in tickers:
    cl_price[ticker] = yf.download(ticker, start, end)['Adj Close']

rename_tickers = ['DOW JONES', 'S&P 500', 'NASDAQ']
cl_price.columns = rename_tickers
price = cl_price.iloc[1]
daily_return = (cl_price.pct_change()*100).iloc[1]
df_display = pd.merge(price, daily_return, right_index=True,
                      left_index=True)

df_display.columns = ["prices", "daily_return"]
df_display = df_display.round(decimals=2)

col1, col2, col3 = st.columns(3)

col1_percent = f'{df_display.daily_return[0]}%'
col2_percent = f'{df_display.daily_return[1]}%'
col3_percent = f'{df_display.daily_return[2]}%'

col1.metric(df_display.index[0], df_display.prices[0], col1_percent)
col2.metric(df_display.index[1], df_display.prices[1], col2_percent)
col3.metric(df_display.index[2], df_display.prices[2], col3_percent)




def main():
    st.title("Trading System")

    menu = ["Stock", "Breakout","Sentiment" ]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Stock':
        indices_choice = st.sidebar.selectbox('Select Indices', indices)
        indices_stock = stock_data.get_stocks_by_index(indices_choice)
        stock_list = pd.DataFrame(list(indices_stock))
        stock_choice = st.sidebar.selectbox("Select Stock Symbol", stock_list.symbol)
        start = st.sidebar.date_input("Start Date")
        end = st.sidebar.date_input("End Date")

        df_tree = pd.read_excel("stocks.xlsx", engine='openpyxl')

        stocks = df_tree["Stocks"]
        index = df_tree["Index"]
        price = df_tree["Prices"]
        per_change = df_tree["Percentage Change %"]

        # Create Chart and store as figure (fig)

        fig = px.treemap(df_tree,
                         path=[index, stocks],
                         values=price,
                         color=per_change,
                         color_continuous_scale=["red", "yellow", "green"],
                         title="Stock Index Map")

        fig.update_layout(
            title_font_size=42,
            title_font_family="Arial"
        )
        if st.button("Display Tree Map"):
            plotly.offline.plot(fig, filename="Chart.html")

        col1, col2 = st.columns([3,1])

        with col1:
            st.info("Stock Analysis")
            df = yf.download(tickers=stock_choice, start=start, end=end)

            with st.expander("Stock Information"):
                stock = yf.Ticker(stock_choice)
                st.info(f"{stock.info['longBusinessSummary']}")

            trace1 = go.Line(
                x=df.index,
                y=df.Close,
                name="Price"
            )
            trace2 = go.Bar(
                x=df.index,
                y=df.Volume,
                name='Volume',
            )
            fig = tools.make_subplots(rows=2, cols=1,
                                      shared_xaxes=True,
                                      vertical_spacing=0.01,
                                      )
            fig.append_trace(trace1, 1, 1)
            fig.append_trace(trace2, 2, 1)
            fig['layout'].update(height=600, width=600)
            st.plotly_chart(fig,use_container_width=True)

            st.dataframe(df, height=160)



        with col2:
            st.info("News Headline")

            COMPANY_NAME = stock_choice

            NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
            NEWS_API_KEY = "5caa53b3551f4ddda139591fe8752485"

            news_params = {
                "apiKey": NEWS_API_KEY,
                "qInTitle": COMPANY_NAME,
            }

            news_response = requests.get(NEWS_ENDPOINT, params=news_params)
            articles = news_response.json()["articles"]
            three_articles = articles[:3]

            formatted_articles = [f"Headline: {article['title']}. \nBrief: {article['description']}" for article in
                                  three_articles]

            for article in formatted_articles:
                st.write(article)


        st.info("Fear and Greed Volatility Index - VIX")
        vix_df = yf.download(tickers="^VIX", start=start, end=end)
        st.line_chart(vix_df, use_container_width=True)

    elif choice == 'Breakout':

        def ATR(DF, n):
            "function to calculate True Range and Average True Range"
            df = DF.copy()
            df['H-L'] = abs(df['High'] - df['Low'])
            df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
            df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
            df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
            df['ATR'] = df['TR'].rolling(n).mean()
            # df['ATR'] = df['TR'].ewm(span=n,adjust=False,min_periods=n).mean()
            df2 = df.drop(['H-L', 'H-PC', 'L-PC'], axis=1)
            return df2['ATR']

        def CAGR(DF):
            "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
            df = DF.copy()
            df["cum_return"] = (1 + df["ret"]).cumprod()
            n = len(df) / 252
            CAGR = (df["cum_return"].tolist()[-1]) ** (1 / n) - 1
            return CAGR

        def volatility(DF):
            "function to calculate annualized volatility of a trading strategy"
            df = DF.copy()
            vol = df["ret"].std() * np.sqrt(252)
            return vol

        def sharpe(DF, rf):
            "function to calculate sharpe ratio ; rf is the risk free rate"
            df = DF.copy()
            sr = (CAGR(df) - rf) / volatility(df)
            return sr

        def max_dd(DF):
            "function to calculate max drawdown"
            df = DF.copy()
            df["cum_return"] = (1 + df["ret"]).cumprod()
            df["cum_roll_max"] = df["cum_return"].cummax()
            df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
            df["drawdown_pct"] = df["drawdown"] / df["cum_roll_max"]
            max_dd = df["drawdown_pct"].max()
            return max_dd

        indices_choice = st.sidebar.selectbox('Select Indices', indices)
        indices_stock = stock_data.get_stocks_by_index(indices_choice)
        stock_list = pd.DataFrame(list(indices_stock))
        multi_stock = st.sidebar.multiselect("Select Stock Symbol", stock_list.symbol)
        start = st.sidebar.date_input("Start Date")
        end = st.sidebar.date_input("End Date")
        period = st.sidebar.number_input("Period", min_value=5)

        st.subheader("Breakout Trading Strategy")
        with st.expander("Breakout wikipedia"):
            st.image("https://traderoomplus.com/wp-content/uploads/2019/06/Completed-breakout-e1578554832501.png")

        ohlc_daily = {}  # directory with ohlc value for each stock

        for ticker in multi_stock :
            ohlc_daily[ticker] = yf.download(ticker, start, end)
            ohlc_daily[ticker].dropna(inplace=True, how="all")

        multi_stock = ohlc_daily.keys()  # redefine stock_list variable after removing any stock_list with corrupted data

        # calculating ATR and rolling max price for each stock and consolidating this info by stock in a separate dataframe
        ohlc_dict = copy.deepcopy(ohlc_daily)
        tickers_signal = {}
        tickers_ret = {}
        for ticker in multi_stock:
            print("calculating ATR and rolling max price for ", ticker)
            ohlc_dict[ticker]["ATR"] = ATR(ohlc_dict[ticker], period)
            ohlc_dict[ticker]["roll_max_cp"] = ohlc_dict[ticker]["High"].rolling(period).max()
            ohlc_dict[ticker]["roll_min_cp"] = ohlc_dict[ticker]["Low"].rolling(period).min()
            ohlc_dict[ticker]["roll_max_vol"] = ohlc_dict[ticker]["Volume"].rolling(period).max()
            ohlc_dict[ticker].dropna(inplace=True)
            tickers_signal[ticker] = ""
            tickers_ret[ticker] = [0]

        # identifying signals and calculating daily return (stop loss factored in)
        for ticker in multi_stock:
            print("calculating returns for ", ticker)
            for i in range(1, len(ohlc_dict[ticker])):
                if tickers_signal[ticker] == "":
                    tickers_ret[ticker].append(0)
                    if ohlc_dict[ticker]["High"][i] >= ohlc_dict[ticker]["roll_max_cp"][i] and \
                            ohlc_dict[ticker]["Volume"][i] > 1.5 * ohlc_dict[ticker]["roll_max_vol"][i - 1]:
                        tickers_signal[ticker] = "Buy"
                    elif ohlc_dict[ticker]["Low"][i] <= ohlc_dict[ticker]["roll_min_cp"][i] and \
                            ohlc_dict[ticker]["Volume"][i] > 1.5 * ohlc_dict[ticker]["roll_max_vol"][i - 1]:
                        tickers_signal[ticker] = "Sell"

                elif tickers_signal[ticker] == "Buy":
                    if ohlc_dict[ticker]["Low"][i] < ohlc_dict[ticker]["Close"][i - 1] - ohlc_dict[ticker]["ATR"][i - 1]:
                        tickers_signal[ticker] = ""
                        tickers_ret[ticker].append(
                            ((ohlc_dict[ticker]["Close"][i - 1] - ohlc_dict[ticker]["ATR"][i - 1]) /
                             ohlc_dict[ticker]["Close"][i - 1]) - 1)
                    elif ohlc_dict[ticker]["Low"][i] <= ohlc_dict[ticker]["roll_min_cp"][i] and \
                            ohlc_dict[ticker]["Volume"][i] > 1.5 * ohlc_dict[ticker]["roll_max_vol"][i - 1]:
                        tickers_signal[ticker] = "Sell"
                        tickers_ret[ticker].append(
                            (ohlc_dict[ticker]["Close"][i] / ohlc_dict[ticker]["Close"][i - 1]) - 1)
                    else:
                        tickers_ret[ticker].append(
                            (ohlc_dict[ticker]["Close"][i] / ohlc_dict[ticker]["Close"][i - 1]) - 1)

                elif tickers_signal[ticker] == "Sell":
                    if ohlc_dict[ticker]["High"][i] > ohlc_dict[ticker]["Close"][i - 1] + ohlc_dict[ticker]["ATR"][i - 1]:
                        tickers_signal[ticker] = ""
                        tickers_ret[ticker].append((ohlc_dict[ticker]["Close"][i - 1] / (
                                ohlc_dict[ticker]["Close"][i - 1] + ohlc_dict[ticker]["ATR"][i - 1])) - 1)
                    elif ohlc_dict[ticker]["High"][i] >= ohlc_dict[ticker]["roll_max_cp"][i] and \
                            ohlc_dict[ticker]["Volume"][i] > 1.5 * ohlc_dict[ticker]["roll_max_vol"][i - 1]:
                        tickers_signal[ticker] = "Buy"
                        tickers_ret[ticker].append(
                            (ohlc_dict[ticker]["Close"][i - 1] / ohlc_dict[ticker]["Close"][i]) - 1)
                    else:
                        tickers_ret[ticker].append(
                            (ohlc_dict[ticker]["Close"][i - 1] / ohlc_dict[ticker]["Close"][i]) - 1)

            ohlc_dict[ticker]["ret"] = np.array(tickers_ret[ticker])

        # calculating overall strategy's KPIs
        strategy_df = pd.DataFrame()
        for ticker in multi_stock :
            strategy_df[ticker] = ohlc_dict[ticker]["ret"]
        strategy_df["ret"] = strategy_df.mean(axis=1)
        port_cagr = round(CAGR(strategy_df), 2)
        port_sharpe = round(sharpe(strategy_df, 0.025), 2)
        port_max = round(max_dd(strategy_df), 2)
        port_df = pd.DataFrame([port_cagr, port_sharpe, port_max], index=["Return", "Sharpe Ratio", "Max Drawdown"],
                               columns=["Portfolio"])
        st.info("Portfolio KPI Score")
        st.dataframe(port_df.T)

        with st.expander("Portfolio Chart"):
            st.bar_chart(port_df)

        # vizualization of strategy return
        fig = px.line((1 + strategy_df["ret"]).cumprod())
        st.plotly_chart(fig)

        # calculating individual stock's KPIs
        cagr = {}
        sharpe_ratios = {}
        max_drawdown = {}
        for ticker in multi_stock:
            print("calculating KPIs for ", ticker)
            cagr[ticker] = CAGR(ohlc_dict[ticker])
            sharpe_ratios[ticker] = sharpe(ohlc_dict[ticker], 0.025)
            max_drawdown[ticker] = max_dd(ohlc_dict[ticker])

        st.info("Individual Stock KPI Scores")
        KPI_df = pd.DataFrame([cagr, sharpe_ratios, max_drawdown], index=["Return", "Sharpe Ratio", "Max Drawdown"])
        st.dataframe(KPI_df.T)
        fig = px.bar(KPI_df.T, x=KPI_df.index, y=KPI_df.columns, barmode='group', orientation='h')
        st.plotly_chart(fig)

    else:
        st.subheader("Sentiment Analysis")
        query = st.sidebar.text_input("Query: ")
        noOfTweet = (st.sidebar.number_input("Enter the number of tweets you want to Analyze: ", min_value=0) - 1)
        start = st.sidebar.date_input("Start Date:")
        end = st.sidebar.date_input("End Date:")

        # Creating list to append tweet data
        tweets_list = []
        noOfDays = end - start

        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(
                query + ' lang:en since:' + str(start) + ' until:' + str(
                        end) + ' -filter:links -filter:replies').get_items()):
            if i > int(noOfTweet):
                break
            tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.username])

        # Creating a dataframe from the tweets list above
        df = pd.DataFrame(tweets_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])

        def make_downloadable(data):
            csvfile = data.to_csv(index=False)
            b64 = base64.b64encode(csvfile.encode()).decode()
            new_filename = 'nlp_result_{}_.csv'.format(timestr)
            st.markdown('### ** 📩 ⬇️ Download CSV file **')
            href = f'<a href= "data:file/csv;base64, {b64}" download="{new_filename}">Click here!</a>'
            st.markdown(href, unsafe_allow_html=True)

        st.dataframe(df)
        with st.expander("Download Text Analysis Results"):
            make_downloadable(df)

        # Create a function to clean the tweets
        @st.cache
        def cleanTxt(text):
            text = re.sub('@[A-Za-z0–9]+', '', text)  # Removing @mentions
            text = re.sub('#', '', text)  # Removing '#' hash tag
            text = re.sub('RT[\s]+', '', text)  # Removing RT
            text = re.sub('https?:\/\/\S+', '', text)  # Removing hyperlink
            return text

        df["Text"] = df["Text"].apply(cleanTxt)

        def percentage(part, whole):
            return round(100 * float(part) / float(whole))

        # Assigning Initial Values
        positive = 0
        negative = 0
        neutral = 0

        # Creating empty lists
        tweet_list1 = []
        neutral_list = []
        negative_list = []
        positive_list = []

        # Iterating over the tweets in the dataframe
        for tweet in df['Text']:
            tweet_list1.append(tweet)
            analyzer = SentimentIntensityAnalyzer().polarity_scores(tweet)
            neg = analyzer['neg']
            neu = analyzer['neu']
            pos = analyzer['pos']
            comp = analyzer['compound']

            if neg > pos:
                negative_list.append(tweet)  # appending the tweet that satisfies this condition
                negative += 1  # increasing the count by 1
            elif pos > neg:
                positive_list.append(tweet)  # appending the tweet that satisfies this condition
                positive += 1  # increasing the count by 1
            elif pos == neg:
                neutral_list.append(tweet)  # appending the tweet that satisfies this condition
                neutral += 1  # increasing the count by 1

        positive = percentage(positive, len(df))  # percentage is the function defined above
        negative = percentage(negative, len(df))
        neutral = percentage(neutral, len(df))

        # Converting lists to pandas dataframe
        tweet_list1 = pd.DataFrame(tweet_list1)
        neutral_list = pd.DataFrame(neutral_list)
        negative_list = pd.DataFrame(negative_list)
        positive_list = pd.DataFrame(positive_list)

        # using len(length) function for counting
        st.info(f"Since {noOfDays}, there have been, {len(tweet_list1)}, tweets on {query}")
        col33, col44, col55 = st.columns(3)
        with col33:
            st.success(f"Number of Positive Sentiment: {len(positive_list)}")
        with col44:
            st.warning(f"Number of Neutral Sentiment: {len(neutral_list)}")
        with col55:
            st.error(f"Number of Negative Sentiment: {len(negative_list)}")

        col66, col77 = st.columns(2)

        with col66:
            # **Creating PieCart**
            st.write("Pie Cart Visualization")
            labels = ['Positive [' + str(round(positive)) + '%]', 'Neutral [' + str(round(neutral)) + '%]',
                      'Negative [' + str(round(negative)) + '%]']
            sizes = [positive, neutral, negative]
            irises_colors = ['rgb(33, 75, 99)', 'rgb(79, 129, 102)', 'rgb(151, 179, 100)',
                             'rgb(175, 49, 35)', 'rgb(36, 73, 147)']
            fig = go.Figure(
                go.Pie(
                    labels=labels,
                    values=sizes,
                    hoverinfo="label+percent",
                    marker_colors=irises_colors,
                    pull=[0, 0, 0.2],
                    textinfo="value"
                ))
            st.plotly_chart(fig)
        with col77:
            with st.expander("Word Cloud Visualization"):
                # word cloud visualization
                def word_cloud(text):
                    stopwords = set(STOPWORDS)
                    allWords = ' '.join([twts for twts in text])
                    wordCloud = WordCloud(background_color='black', width=1600, height=800, stopwords=stopwords,
                                          min_font_size=20, max_font_size=150, colormap='prism').generate(allWords)
                    fig, ax = plt.subplots(figsize=(20, 10), facecolor='k')
                    plt.imshow(wordCloud)
                    ax.axis("off")
                    fig.tight_layout(pad=0)
                    st.pyplot(fig)

                st.write(f'Wordcloud for {query}')
                word_cloud(df['Text'].values)

        col88, col99 = st.columns(2)
        with col88:
            # word_cloud_sentiment(positive_list)
            count = WordCloud().process_text(str(positive_list))
            with st.expander("Top 5 Positive Keywords"):
                sorted_d = sorted(count.items(), key=operator.itemgetter(1), reverse=True)
                st.write("The top 5 Positive Sentiment: ", sorted_d[:5])

        with col99:
            count2 = WordCloud().process_text(str(negative_list))
            with st.expander("Top 5 Negative Keywords"):
                sorted_d2 = sorted(count2.items(), key=operator.itemgetter(1), reverse=True)
                st.write("The top 5 Negative Sentiment: ", sorted_d2[:5])



if __name__ == '__main__':
    main()