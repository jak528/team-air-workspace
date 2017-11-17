
# coding: utf-8

# In[580]:

import simplejson, urllib
import calendar
import time
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import numpy
import pandas as pd
import math
import csv
from ast import literal_eval as make_tuple

class sigmasearch():
    
    def __init__(self,key,geo_url,traffic_url,date_format):
        self.key = key
        self.geo_url = geo_url
        self.traffic_url = traffic_url
        self.date_format = date_format
        self.geo_locations = {}
        self.memory = {}
        self.model = {}

        
    def save_memory(self):
        df = pd.DataFrame(self.memory.items(), columns=['key','traffic'])
        df.to_csv("Memory.csv")
        
    def load_memory(self,fn):

        with open(fn,'r') as f:
            reader=csv.DictReader(f)
            for row in reader:
                self.memory[make_tuple(row['key'])] = make_tuple(row['traffic'])

    def geo_convertion(self,address):
        if address not in self.geo_locations:
            url = self.geo_url + address
            try:
                result= simplejson.load(urllib.urlopen(url)) 
                loc = result['results'][0]['geometry']['location']
                lat = loc['lat']
                lng = loc['lng']
            except:
                result= simplejson.load(urllib.urlopen(url)) 
                loc = result['results'][0]['geometry']['location']
                lat = loc['lat']
                lng = loc['lng']
                
            self.geo_locations[address] = str(lat) +","+ str(lng)
            return str(lat) +","+ str(lng)
        else:
            return self.geo_locations[address]

    def convert_time(self,T):
        return calendar.timegm(time.strptime(T, self.date_format))
    
    def convert_datetime(self,T):
        return datetime.datetime.strptime(T, self.date_format)
    
    def convert_string(self,T):
        return datetime.datetime.strftime(T, self.date_format)

    def get_ground_time(self,origin,destination,departure_time):
        if (origin,destination,departure_time) in self.memory:
            return self.memory[(origin,destination,departure_time)]
        else:
            print "Updating DataBase for " + str(departure_time)
            url = self.traffic_url.format(self.geo_convertion(origin),self.geo_convertion(destination))
            url += '&departure_time=' + str(self.convert_time(departure_time))
            url += '&key=' + self.key
            url += '&trafficModel=pessimistic'
            print url
            result= simplejson.load(urllib.urlopen(url))
            average = result['rows'][0]['elements'][0]['duration']['value']
            if 'duration_in_traffic' in result['rows'][0]['elements'][0]:
                traffic = result['rows'][0]['elements'][0]['duration_in_traffic']['value']
            else:
                traffic = average
            self.memory[(origin,destination,departure_time)] = (average,traffic)
            return average,traffic
    
    def get_ground_est_win(self,time_in,day,interval):
        hours = day * 24 / interval
        time_in = datetime.datetime.strptime(time_in,self.date_format)
        step = datetime.timedelta(hours=interval)
        ts = [(time_in + n*step).strftime(self.date_format) for n in range(-hours/2,hours/2)]
        idx = int(math.ceil(hours/2.0))
        return idx,ts
    
    def compute_traffic_index(self,origin,destination,departure_time,day = 1,interval=1):
       
        avg,benchtime = self.get_ground_time(origin,destination,departure_time)
        n = int(math.ceil(1.2*avg/1800.0))
        #print "Approximated Travel Time: " + str(30*n) + " mins"
        time_diff = datetime.timedelta(minutes=n*30)
        #departure_time = self.convert_datetime(departure_time) - time_diff
        #departure_time = self.convert_string(departure_time)
        
        idx,time_array = self.get_ground_est_win(departure_time,day,interval)
        
        tran_time = []
        for t in time_array:
            temp_t = self.convert_string(self.convert_datetime(t) - time_diff)
            #print (t,temp_t)
            #if temp_t in self.memory:
            #tran_time.append(self.memory[temp_t])
            #else:
            avg,ground_time = self.get_ground_time(origin,destination,temp_t)
            #self.memory[temp_t] = ground_time
            tran_time.append(ground_time)

        scores = pd.qcut(tran_time, 5, labels=[1,2,3,4,5])
        
        df = pd.DataFrame(index=time_array)
        df['Traffic Score'] = scores
        return tran_time[idx],scores[idx],df
    
    
    def compute_sigma_index(self,timestamp,carrier,number,org_zip,dest_zip,origin,destination):
        
        traffic_index = self.compute_traffic_index(org_zip,dest_zip,timestamp,day = 3,interval = 4)
        flight_index = self.compute_flight_index(timestamp,carrier,number,origin,destination)
        flight_index = (((flight_index - 0.49) * (100 - 0)) / (0.51 - 0.49)) + 0 
        traffic_index = traffic_index[1] * 20
        sigma_score = 0.7*traffic_index + 0.3*flight_index 
        return sigma_score
    
    def compute_flight_index(self,timestamp,carrier,number,origin,destination):
        if len(self.model) == 0:
            agent.load_data('FlightDely_201401_201708.csv')
            model = agent.generate_delay_model(origin,nrow=10000)
        row = self.generate_delay_row(timestamp,carrier,number,origin,destination)
        return self.model.predict_proba(row)[:,1] 
    
    def generate_delay_row(self,timestamp,carrier,number,origin,destination):
        t = self.convert_datetime(timestamp)
        dow = t.weekday()+1
        dom = t.day
        year = t.year
        month = t.month
        hour = t.hour
        carrier_mean = self.car_mean[carrier]
        dest_mean = self.dest_mean[destination]
        carrier = self.carreirs[carrier]
        dest = self.dests[destination]
        row = [year,month,dom,dow,carrier,hour,dest,carrier_mean,dest_mean]
        #print row
        return row
    
    def generate_delay_model(self,origin,dest=0,nrow=1000):
        if len(self.fd_raw) >0:
            df = self.preprocess_historical(origin,destination=0,num=nrow)
            X = df.loc[:,df.columns != 'DEP_DELAY'].values
            Y = list(df.loc[:,'DEP_DELAY'].values)
            #print X[0]
            bdt = AdaBoostClassifier(DecisionTreeClassifier(max_depth=3),
                                 algorithm = "SAMME",
                                learning_rate = 0.8)
            result = bdt.fit(X,Y)
            self.model = bdt
            return bdt
            #test_predict = bdt.predict_proba(X_test)[:,1]
    def load_data(self,fname):
        df = pd.read_csv(fname,header=0)
        self.fd_raw = df
        self.flight = {}
        self.dest = {}
        self.fd_processed = pd.DataFrame()
    
    def preprocess_historical(self,origin,destination=0,num = 1000):
        #df = pd.read_csv(fname,header=0)
        df = self.fd_raw
        df = df[-num:]
        df = df[df['ORIGIN']==origin]
        df["Flight_Num"] = df["UNIQUE_CARRIER"].map(str) + df["FL_NUM"].map(str)
        df = df[['YEAR','MONTH','DAY_OF_MONTH','DAY_OF_WEEK','UNIQUE_CARRIER','CRS_DEP_TIME','DEST','DEP_DELAY','Flight_Num']]
        df = df[np.isfinite(df['DEP_DELAY'])]
        Carrier_list = list(df['UNIQUE_CARRIER'].unique())
        Dest_list = list(df['DEST'].unique())
        Flight_list = list(df['Flight_Num'].unique())
            
        car_mean = self.cal_mean(df,Carrier_list,'UNIQUE_CARRIER')
        self.car_mean = car_mean
        df["Carrier_Mean"] = df["UNIQUE_CARRIER"].map(car_mean)
        dest_mean = self.cal_mean(df,Dest_list,'DEST')
        self.dest_mean = dest_mean
        df["Dest_Mean"] = df["DEST"].map(dest_mean)
        ontime_rate = self.ontime_rate(df,Flight_list)
        df['Ontime_Rate'] = df['Flight_Num'].map(ontime_rate)

        df.CRS_DEP_TIME = pd.cut(df.CRS_DEP_TIME, range(0,2600,100),labels=range(0,25))
        df['DEP_DELAY'] = np.where(df['DEP_DELAY']>=0, 1, 0)
        self.fd_processed = df.copy()
        
        
        dests = self.one_hot_encoding(df,Dest_list)
        carriers = self.one_hot_encoding(df,Carrier_list)
        self.carreirs = carriers
        self.dests = dests
        
        df['DEST'] = df['DEST'].map(dests)
        df['UNIQUE_CARRIER'] = df['UNIQUE_CARRIER'].map(carriers)

        df = df.drop(['Flight_Num'],axis=1)
        df = df.drop(['Ontime_Rate'],axis=1)
        return df
    
    def get_ontime_rate(self,orgin,destination,carrier,fligtno):
        stats = 0
        if len(self.fd_processed) > 0:
            df = self.fd_processed
            cond = (df['UNIQUE_CARRIER']==carrier) & (df['Flight_Num'] == flightno) & (df['DEST'] == destination)
            stats = df[cond]['Ontime_rate']
        return stats
        
    def carrier_mean(self,df,carrier_name,col_name):
        cur_carrier = df[df[col_name]==carrier_name]
        carrier_mean = np.mean(cur_carrier['DEP_DELAY'])
        return carrier_mean
    
    def cal_mean(self,df,carrier_list,col_name):
        Carrier_mean ={}
        for i in carrier_list:
            Carrier_mean[i]=self.carrier_mean(df,i,col_name)
        return Carrier_mean
    
    def ontime_rate(self,df,flight_list):
        flight_map={}
        for i in flight_list:
            total = len(df[df['Flight_Num']==i])
            ontime = len(df[(df['Flight_Num'] == i) & (df['DEP_DELAY'] < 8)])
            flight_map[i]= ontime/float(total)
        return flight_map

    def one_hot_encoding(self,df,l):
        m={}
        for i in range(len(l)):
            m[l[i]]= i 
        #print m
        return m
    
    def save_model(self,f,model):
        pickle.dump(model, open(f, 'wb'))
        
    def load_model(self,f):
        loaded_model = pickle.load(open(f, 'rb'))
        self.model = loaded_model
        #result = loaded_model.score(X_test, Y_test)
        
        # seperate dependent variables and independent variables

#def compute_delay_probability(self,flight_no,flight_date)


# In[581]:

# geo_url = "https://maps.googleapis.com/maps/api/geocode/json?address="
# traffic_url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={0}&destinations={1}"
# key = "AIzaSyDadt89iOaL7ox2rIOe9lqat66vpcthwYE"
# date_format ='%Y-%m-%d %H:%M:%S EST'
# agent = sigmasearch(key,geo_url,traffic_url,date_format)


# In[566]:

#traffic_time,index,df= agent.compute_traffic_index("Cornell Tech","JFK","2018-12-10 18:30:00 EST",3,4)
#agent.save_memory()
#agent.load_memory('memory.csv')


# In[567]:

# agent.load_data('FlightDely_201401_201708.csv')
# model = agent.generate_delay_model(origin="JFK",nrow=10000)


# In[585]:

#agent.generate_delay_row('2018-12-11 18:30:00 EST','B6','B61013','JFK','LGB')
sigma_score = agent.compute_sigma_index('2017-12-24 21:00:00 EST','B6','B61791','10044','JFK','JFK','LGB')
sigma_score
# agent.save_model('test',agent.model)
# agent.load_model('test')

