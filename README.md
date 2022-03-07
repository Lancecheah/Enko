# Enko

# Several ways of analyzing the 7 major forex pair 

### Introduction
We are use Yahoo Financial dataset of the 7 Major Forex Pair from 01/01/2012 to 31/01/2022.
The following pair of forex pair are being use:
AUDUSD, USDCAD, USDCHF, EURUSD, GBPUSD, USDJPY, NZDUSD
The source of data from yahoo.finance (https://pypi.org/project/yfinance/ )
To find any opportunity between investing & trading for long term. 

### Technologies
Programming languages : Python

### Library 
* import numpy
* import pandas 
* import matplotlib.pyplot 
* import seaborn 
* import yfinance 

### Launch
In jupyter notebook / Lab prefer

### Table of contents
* [Dataset](https://github.com/Lancecheah/Enko/edit/main/README.md#dataset)
* [Normalisation of the data](https://github.com/Lancecheah/Enko/edit/main/README.md#normalisation-of-the-data)  
* [Best Forex Pair Return Over Time](https://github.com/Lancecheah/Enko/edit/main/README.md#best-forex-pair-return-over-time)
* [Risk & Return](https://github.com/Lancecheah/Enko/edit/main/README.md#risk--return)
* [What was the Average Monthly Return of each forex pair?](https://github.com/Lancecheah/Enko/edit/main/README.md#what-was-the-average-monthly-return-of-each-forex-pair)
* [Analysis Statistical arbitrage](https://github.com/Lancecheah/Enko/edit/main/README.md#analysis-statistical-arbitrage)
* [Simple moving average (SMA) A trend following indicator](https://github.com/Lancecheah/Enko/edit/main/README.md#simple-moving-average-sma-a-trend-following-indicator)
* [BOLLINGER BANDS identify the degree of real-time volatility for a currency pair](https://github.com/Lancecheah/Enko/edit/main/README.md#bollinger-bands-identify-the-degree-of-real-time-volatility-for-a-currency-pair)
* [Nonfarm payrolls Strategy If Wed is greater than Thur than sell](https://github.com/Lancecheah/Enko/edit/main/README.md#nonfarm-payrolls-strategy-if-wed-is-greater-than-thur-than-sell)
* [Volume Profile to Draw Support & Resistance ](https://github.com/Lancecheah/Enko/edit/main/README.md#volume-profile-to-draw-support--resistance)



-----

#### Dataset
![image](https://user-images.githubusercontent.com/48453212/157033329-f4f23d37-2534-4cd0-ab67-2999dfba1ab2.png)
-----
#### Normalisation of the data
![image](https://user-images.githubusercontent.com/48453212/157034837-a708c428-e02a-49ec-a4b5-8ee2afe65a66.png)
-----
#### Best Forex Pair Return Over Time
![image](https://user-images.githubusercontent.com/48453212/157034997-cb4c1fcf-f0ea-41a7-92fd-cd69ae01644f.png)
-----
#### Risk & Return
![image](https://user-images.githubusercontent.com/48453212/157035223-16e9fb5c-e80c-4591-9e4b-9965dfc632b1.png)
-----
#### What was the Average Monthly Return of each forex pair?
(Good for Trading – A lot of data points is close to 5% movement)
![image](https://user-images.githubusercontent.com/48453212/157035521-2598cbc3-2b4f-4ab7-bb8b-396062a80604.png)
-----
#### Analysis Statistical arbitrage
(We must find such currency pairs that move in the same direction and have a strong relationship - correlation. The correlation coefficient must be greater than 0.9.
-----
Temporary divergences often occur between these currency pairs. The presence of such discrepancies can be identified using the coefficient of cointegration.
It should be no more than 0.05.)
![image](https://user-images.githubusercontent.com/48453212/157035967-6a0a2059-ce11-41c5-9691-f97f040fc2b2.png)
-----
#### Simple moving average (SMA) A trend following indicator
![image](https://user-images.githubusercontent.com/48453212/157036153-9b72433b-bb2d-4abc-ba58-7dfa51c7b337.png)
-----
#### BOLLINGER BANDS identify the degree of real-time volatility for a currency pair
![image](https://user-images.githubusercontent.com/48453212/157036460-00b5ab1e-9ced-4033-85de-519a1c0edb30.png)
-----
#### Nonfarm payrolls Strategy If Wed is greater than Thur than sell
![image](https://user-images.githubusercontent.com/48453212/157036711-dc9ecec0-b6ae-487b-a82e-8c71306d9eba.png)
![image](https://user-images.githubusercontent.com/48453212/157037052-1bd059c6-63b7-4e81-94d8-b7ccc7c496e1.png)
-----
#### Volume Profile to Draw Support & Resistance 
![image](https://user-images.githubusercontent.com/48453212/157037105-aba86686-bbc5-4818-b0a4-c1deaf19f6ea.png)
-----

## Note
The analysis above are for education purpose only, strictly not meant for anyone to take a trade or to make any money with it. Please perform your own research and risk management when you use the above data. 
