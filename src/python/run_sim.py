import traceback
try:
    import signals.sim_server as sim
    import signals.sentiment as sentiment
    import sys
    
    server = sim.SimServer('/home/ibraaaa/servers/1mon_preprocess/')
    result = server.query(sys.argv[1])  
    result = server.rank(result[0], result[1])
    
    for r in result:
        sentiment_score = 0#sentiment.Sentiment().calc_headline_sentiment_by_arabic(r[2]['url'])
        print "'",r[2]['url'], "','", r[0], "',", r[2]['news_site'], ',', r[2]['date'], ',' , r[1], ',', sentiment_score
except:
    print traceback.format_exc()