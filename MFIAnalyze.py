# -*- coding: utf-8 -*-

import pandas as pd;
import numpy as np;
import talib as ta;
from scipy import stats;
import matplotlib.pyplot as plt;
import statsmodels.api as sm;
import statsmodels.tsa.stattools as tools;
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf;
from statsmodels.tsa.seasonal import seasonal_decompose;
from statsmodels.tsa.arima_model import ARMA;


def CalMFI(day_data, win_len):
    # 校订数据框的 index
    day_data = day_data.reset_index(drop = True);
    
    # 计算 typical price 与 money flow
    TypPrice = (day_data.HPrice+day_data.LPrice+day_data.CPrice)/3;
    MF = TypPrice*day_data.NTrade;
    
    # 构建每日计算 MFI 的矩阵
    l = len(MF);
    win_MF = np.zeros([win_len,l-win_len+1]);
    win_TypPrice = np.zeros([win_len,l-win_len+1]);
    # 给矩阵赋值
    for i in range(win_len):
        win_MF[i,:] = MF[i:(l-win_len+1+i)];
        win_TypPrice[i,:] = TypPrice[i:(l-win_len+1+i)];
        
    # 根据矩阵批量计算 MFI
    PMF = np.sum(win_MF[1:,:]*(win_TypPrice[1:,:]>win_TypPrice[0:-1,:]),0);
    NMF = np.sum(win_MF[1:,:]*(win_TypPrice[1:,:]<win_TypPrice[0:-1,:]),0);
    MFI = 100-100/(1+PMF/NMF);
    MFI[np.isnan(MFI)]=50*np.ones(np.sum(np.isnan(MFI)));
    
    # 补齐 MFI 长度
    MFI  = np.append(np.nan*np.ones(win_len-1),MFI);
    return MFI; 


class TimeSeries(object):
    
    def __init__(self, TSData, *Date):
        
        # 生成时间序列
        TS = pd.Series(TSData);
        
        # 若有日期输入， 则重新选择 index
        if len(Date) != 0:
            day_index = [str(int(x)) for x in Date[0]];
            TS.index = pd.to_datetime(day_index);
        self.TS = TS[~np.isnan(TS)];
        
    def DrawTS(self):
        # 作出时间序列的图形
        fig = self.TS.plot();
        fig.grid();
        fig.set_xlabel("Time");
        fig.set_ylabel("MFI");
        plt.show;
        
    def ADFTest(self, max_lag = None):
        # 对时间序列进行 ADF 检验
        adf_test = tools.adfuller(self.TS, maxlag = max_lag, regression = 'c')
        
        # 对输出结果进行整理
        adf_output = pd.Series(adf_test[0:4], \
            index=['Test Statistic','p-value','Lags Used','Number of Observations Used'])
        for key,value in adf_test[4].items():
            adf_output['Critical Value (%s)'%key] = value;
        
        # 返回结果
        return adf_output;
        
    def DrawACF(self, lags = 40):
        
        fig = plt.figure(figsize=(7,7));
        ax1 = fig.add_subplot(211);
        # 作出自相关系数图
        plot_acf(self.TS, lags=lags, ax=ax1);
        ax2 = fig.add_subplot(212);
        # 作出偏自相关系数图
        plot_pacf(self.TS, lags=lags, ax=ax2);
        plt.show();
        
    def Diff(self, n = 1):
        # 对时间序列做差分
        dTS = self.TS.diff(n);
        dTS = TimeSeries(dTS);
        return dTS;
    
    def PredictARMA(self, p, q):
        # 返回 ARMA(p,q) 模型的结果
        model = ARMA(self.TS, order=(p, q));
        results_ARMA = model.fit( disp=-1, method='mle');
        return results_ARMA;
    
    def SelectModel(self, max_lag):
        # 初始化 BIC 以及模型阶数 (p,q) 的值 
        proper_bic = np.inf;
        new_bic = np.inf;
        proper_p = 0;
        proper_q = 0;
        model = None;
        
        # 对各个结束的模型进行测试，根据 BIC 的值返回最优结果
        for p in range(max_lag+1):
            for q in range(max_lag+1):
                try:
                    model = self.PredictARMA(p, q);
                    new_bic = model.bic;
                except:
                    continue;
                if new_bic < proper_bic:
                    proper_p = p;
                    proper_q = q;
        proper_model = self.PredictARMA(proper_p, proper_q);
        return proper_p, proper_q, proper_model;
    
if __name__ == "__main__":
    # 读取日线数据
    day_data = pd.read_csv('D:/Futures/au.csv', header = 'infer');
    
    # 计算 MFI 指标
    win_len = 26;
    MFI = CalMFI(day_data, win_len);
    
    # 生成 MFI 的时间序列并做平稳性检验
    MTS = TimeSeries(MFI, day_data.Date);
    
    # 画出 ACF，PACF 并对 ARMA 模型求解
    MTS.DrawACF();
    model = MTS.PredictARMA(2,0)
    
    #  对 MFI 进行预测
    para = model.conf_int();
    para = np.sum(para, 1)/2;
    
    
    
     
        

