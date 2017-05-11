# -*- coding: utf-8 -*-

import requests as rq;
from bs4 import BeautifulSoup as bs;
import pandas as pd;

def SHFE(wordpath):
    
    # 读取指定的文字库
    Words = pd.read_csv(wordpath, header = 'infer', encoding = "GBK");
    
    # 给请求指定一个请求头来模拟chrome浏览器
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'};
               
    # 给定网址（上期所 黄金）
    web = 'http://www.shfe.com.cn'
    web_url = 'http://www.shfe.com.cn/bourseService/marketresearch/internationalmarket/';
    
    # 读取网页数据并生成对 html 文档进行转换
    title_web = rq.get(web_url, headers=headers);
    info = bs(title_web.text, 'lxml');
    
    # 在树中搜索标题
    title = info.find_all('a', target="_blank");
    
    # 初始化分数
    score = 0;
    
    for element in title:
        # 获取标题中的超链接
        link = element.get('href');
        
        # 选择 ‘收市报道’ 和 ‘每日情报’
        if ('upload' in link)|('bourseService' in link):
            
            # 生成正文链接并读取网页数据
            url = web+link;
            detail_web = rq.get(url, headers=headers);
            info = bs(detail_web.text, 'lxml');
            article = info.find_all('div', class_="article-detail-text");
            
            # 如果正文有内容，则对正文进行比对
            if len(article) != 0:
                article = str(article[0]);
                for i in range(len(Words)):
                    if Words.loc[i, 'Words' ] in article:
                        score += Words.loc[i, 'Sign']; # 计算分数
    # 返回分数
    return score;



def FinSina(wordpath):
    
    # 读取指定的文字库
    Words = pd.read_csv(wordpath, header = 'infer', encoding = "GBK");
    
    #给请求指定一个请求头来模拟chrome浏览器
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'};
               
    # 给定网址（新浪财经 黄金分析）
    web_url = 'http://roll.finance.sina.com.cn/finance/gjs/hjfx/index_1.shtml';
    
    # 读取网页数据
    title_web = rq.get(web_url, headers=headers);
    
    # 修改编码方式对 html 文档进行转换
    title_web.encoding = 'GBK';
    info = bs(title_web.text, 'lxml');
    
    # 在树中搜索标题
    title = info.find_all('a', target="_blank");
    
    # 初始化分数
    score = 0;
    
    for element in title:
        # 获取标题中的超链接
        url = element.get('href');
        
        # 并读取网页数据并进行转换
        detail_web = rq.get(url, headers=headers);
        detail_web.encoding = 'utf-8';
        info = bs(detail_web.text, 'lxml');
        
        # 搜索文章正文
        article = info.find_all('div', id="artibody");
        
        # 如果正文有内容，则对正文进行比对
        if len(article) != 0:
            article = str(article[0]);
            for i in range(len(Words)):
                if Words.loc[i, 'Words' ] in article:
                    score += Words.loc[i, 'Sign'];
    # 返回分数
    return score;
                
if __name__ == "__main__":
    
    # 给定文字库路径
    wordpath = 'D:/Futures/words.csv';
    
    # 返回上期所行情分析结果
    score1 = SHFE(wordpath);
    
    # 返回新浪行情分析结果
    score2 = FinSina(wordpath);
    
        
        
    
    