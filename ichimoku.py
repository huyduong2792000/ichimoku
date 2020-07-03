# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

#import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np
import decimal
import plotly.graph_objects as go


class Ichimoku():
    """
    @param: ohcl_df <DataFrame> 

    Required columns of ohcl_df are: 
        Date<Float>,Open<Float>,High<Float>,Close<Float>,Low<Float>
    """
    def __init__(self, ohcl_df):
        self.ohcl_df = ohcl_df

    def run(self):
        tenkan_window = 7
        kijun_window = 22
        senkou_span_b_window = 44
        cloud_displacement = 22
        chikou_shift = -22
        ohcl_df = self.ohcl_df
        

#         print(ohcl_df)
        # the period is the difference of last two dates
        last_date = ohcl_df["Date"].iloc[-1]
        period = last_date - ohcl_df["Date"].iloc[-2]

        # Add rows for N periods shift (cloud_displacement)
        ext_beginning = last_date+period
        ext_end = last_date + ((period*cloud_displacement)+period)
        dates_ext = list(self.drange(ext_beginning, ext_end, period))
        dates_ext_df = pd.DataFrame({"Date": dates_ext})
#         print(dates_ext_df)
        dates_ext_df.index = dates_ext # also update the df index
        ohcl_df = ohcl_df.append(dates_ext_df)
#         ohcl_df = ohcl_df.set_index(ohcl_df['Date'].apply(lambda x:datetime.utcfromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S')))
#         ohcl_df['Date'] = mdates.date2num(pd.to_datetime(ohcl_df['Date']).tolist())
        # Tenkan 
        tenkan_sen_high = ohcl_df['High'].rolling( window=tenkan_window ).max()
        tenkan_sen_low = ohcl_df['Low'].rolling( window=tenkan_window ).min()
        ohcl_df['tenkan_sen'] = (tenkan_sen_high + tenkan_sen_low) /2
        # Kijun 
        kijun_sen_high = ohcl_df['High'].rolling( window=kijun_window ).max()
        kijun_sen_low = ohcl_df['Low'].rolling( window=kijun_window ).min()
        ohcl_df['kijun_sen'] = (kijun_sen_high + kijun_sen_low) / 2
        # Senkou Span A 
        ohcl_df['senkou_span_a'] = ((ohcl_df['tenkan_sen'] + ohcl_df['kijun_sen']) / 2).shift(cloud_displacement)
        # Senkou Span B 
        senkou_span_b_high = ohcl_df['High'].rolling( window=senkou_span_b_window ).max()
        senkou_span_b_low = ohcl_df['Low'].rolling( window=senkou_span_b_window ).min()
        ohcl_df['senkou_span_b'] = ((senkou_span_b_high + senkou_span_b_low) / 2).shift(cloud_displacement)
        # Chikou
        ohcl_df['chikou_span'] = ohcl_df['Close'].shift(chikou_shift)

        self.ohcl_df = ohcl_df
        return ohcl_df

    def plot(self):
#         fig, ax = plt.subplots() 
        fig= plt.figure(figsize=(16,9))
        ax= fig.add_axes([0.1,0.1,0.8,0.8])

        self.plot_candlesticks(fig, ax)
        self.plot_ichimoku(fig, ax)
        self.pretty_plot(fig, ax)
#         plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.show()

    def pretty_plot(self, fig, ax):
        ax.legend()
        fig.autofmt_xdate()
#         ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
#         ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
#         ax.xaxis_date()
#         print(ax.xaxis)
#         ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        # Chart info
        title = 'Ichimoku Demo (ETH)'
        bgcolor = '#ffffff'
        grid_color = '#363c4e'
        spines_color = 'black'
        # Axes
        plt.title(title, color='black')
        plt.xlabel('Date', color=spines_color, fontsize=20)
        plt.ylabel('Price (ETH)', color=spines_color, fontsize=20)

#         ax.set_facecolor(bgcolor)
#         ax.grid(linestyle='-', linewidth='0.5', color=grid_color)
#         ax.yaxis.tick_right()
#         ax.set_yscale("log", nonposy='clip')
#         fig.patch.set_facecolor(bgcolor)
#         fig.patch.set_edgecolor(bgcolor)
#         plt.rcParams['figure.facecolor'] = bgcolor
#         plt.rcParams['savefig.facecolor'] = bgcolor
#         ax.spines['bottom'].set_color(spines_color)
#         ax.spines['top'].set_color(spines_color) 
#         ax.spines['right'].set_color(spines_color)
#         ax.spines['left'].set_color(spines_color)
        ax.tick_params(axis='x', colors=spines_color, size=7)
        ax.tick_params(axis='y', colors=spines_color, size=7)
#         fig.tight_layout()
#         ax.autoscale_view()

    def plot_ichimoku(self, fig, ax, view_limit=100):
        d2 = self.ohcl_df.loc[:, ['Date','tenkan_sen','kijun_sen','senkou_span_a','senkou_span_b', 'chikou_span']]
        d2 = d2.tail(view_limit)
#         date_axis = d2.index.values
        date_axis = d2['Date']
#         print(date_axis)
        
        # ichimoku
        plt.plot(date_axis, d2['tenkan_sen'], label="tenkan", color='#0496ff', alpha=0.65,linewidth=2)
        plt.plot(date_axis, d2['kijun_sen'], label="kijun", color="#991515", alpha=0.65,linewidth=2)
        plt.plot(date_axis, d2['senkou_span_a'], label="span a", color="#ff0000", alpha=0.65,linewidth=0.5)
        plt.plot(date_axis, d2['senkou_span_b'], label="span b", color="black", alpha=0.65, linewidth=0.5)
        plt.plot(date_axis, d2['chikou_span'], label="chikou", color="#008000", alpha=0.65, linewidth=2)
        # green cloud
        ax.fill_between(date_axis, d2['senkou_span_a'], d2['senkou_span_b'], where=d2['senkou_span_a']> d2['senkou_span_b'], facecolor='#008000', interpolate=True, alpha=0.25)
        # red cloud
        ax.fill_between(date_axis, d2['senkou_span_a'], d2['senkou_span_b'], where=d2['senkou_span_b']> d2['senkou_span_a'], facecolor='#ff0000', interpolate=True, alpha=0.25)

    def plot_candlesticks(self, fig, ax, view_limit=100):
        # plot candlesticks
        candlesticks_df = self.ohcl_df.loc[:, ['Date','Open','High','Low', 'Close']]
        candlesticks_df = candlesticks_df.tail(view_limit)
        
#         candlesticks_df['Date'] = pd.to_datetime(candlesticks_df['Date']).tolist()
#         layout = dict(
# #         title="FB Facebook",
#         xaxis=go.layout.XAxis(title=go.layout.xaxis.Title( text="Time (EST - New York)"), rangeslider=dict (visible = False)),
#         yaxis=go.layout.YAxis(title=go.layout.yaxis.Title( text="Price $ - US Dollars")),
#         width=1000,
#         height=800
#         )
#         data = [go.Candlestick(x=candlesticks_df.index.values,
#                        open=candlesticks_df['Open'], high=candlesticks_df['High'],
#                        low=candlesticks_df['Low'], close=candlesticks_df['Close'])]
#         fig = go.Figure(data = data, layout = layout)
#         fig.show()
#         ax.xaxis_date()
#         print(ax)
        # plot candlesticks
        candlestick_ohlc(ax, candlesticks_df.values, width=40, colorup='#83b987', colordown='#eb4d5c', alpha=0.5 )

    def drange(self, x, y, jump): 
        while x < y:
            yield x
            x += jump