import mysql.connector
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
from pykalman import KalmanFilter
import numpy as np
import datetime
from numpy import ma
from . import parameter as param

prm = param.Para()
tstep = prm.tstep
units = prm.units

def kalmanprocess(Time,X):
    # time step
    dt = Time[2] - Time[1]

    # transition_matrix  
    F = [[1,  dt,   0.5*dt*dt], 
         [0,   1,          dt],
         [0,   0,           1]]  

    # observation_matrix   
    H = [1, 0, 0]

    # transition_covariance 
    Q = [[   1,     0,     0], 
         [   0,  1e-4,     0],
         [   0,     0,  1e-6]] 

    # observation_covariance 
    R = [0.04] # max error = 0.6m

    # initial_state_mean
    X0 = [0,
          0,
          0]

    # initial_state_covariance
    P0 = [[ 10,    0,   0], 
          [  0,    1,   0],
          [  0,    0,   1]]

    n_timesteps = len(Time)
    n_dim_state = 3

    filtered_state_means = np.zeros((n_timesteps, n_dim_state))
    filtered_state_covariances = np.zeros((n_timesteps, n_dim_state, n_dim_state))

    # Kalman-Filter initialization
    kf = KalmanFilter(transition_matrices = F, 
                      observation_matrices = H, 
                      transition_covariance = Q, 
                      observation_covariance = R, 
                      initial_state_mean = X0, 
                      initial_state_covariance = P0)


    # iterative estimation for each new measurement
    for t in range(n_timesteps):
        if t == 0:
            filtered_state_means[t] = X0
            filtered_state_covariances[t] = P0
        else:
            filtered_state_means[t], filtered_state_covariances[t] = (
            kf.filter_update(
                filtered_state_means[t-1],
                filtered_state_covariances[t-1],
                observation = X[t])
            )
    return filtered_state_means[:, 0]

def kimpute(Time, X, Y):
    xin=[]
    yin=[]
    tin=[]
    msk=[]
    j=0
    for i in range(Time[0],Time[-1]+1,tstep):
        if i==Time[j]:
            xin.append(X[j])
            yin.append(Y[j])
            msk.append(0)
            j+=1
        else:
            xin.append(0)
            yin.append(0)
            msk.append(1)
        tin.append(i)
    xinmask= ma.array(xin,mask=msk)
    yinmask= ma.array(yin,mask=msk)
    return (tin,kalmanprocess(tin,xinmask),kalmanprocess(tin,yinmask))

def imputer(df1,time_lower):
    start_time= time_lower
    lstep= tstep*units
    prev = 0
    Time =[]
    X=[]
    Y=[]
    tmpt=[0]
    tmpx=[df1.iloc[0,-2]]
    tmpy=[df1.iloc[0,-1]]
    for i in range(1,len(df1)):
        t = int((df1.iloc[i,1]-df1.iloc[i-1,1]).total_seconds())
        if t>lstep:
            if len(tmpt) >1:
                Time.append(tmpt)
                X.append(tmpx)
                Y.append(tmpy)
            tmpt=[]
            tmpx=[]
            tmpy=[]
        tmpt.append(int((df1.iloc[i,1]-time_lower).total_seconds()))
        tmpx.append(df1.iloc[i,-2])
        tmpy.append(df1.iloc[i,-1])
        prev= df1.iloc[i,1]
    if len(tmpt)>1:
        Time.append(tmpt)
        X.append(tmpx)
        Y.append(tmpy)
    imp_points=[]
    for i in range(len(Time)):
        time,retx,rety=kimpute(Time[i],X[i],Y[i])
        for t in range(len(time)):
            if time[t] not in Time[i]:
                imp_points.append([time[t],retx[t],rety[t]])
    ret = pd.DataFrame(imp_points)
    for i in range(len(ret)):
        ret.iloc[i,0]= datetime.timedelta(seconds=int(ret.iloc[i,0])*tstep)+time_lower
    return ret   

def Run(time_lower, time_upper):
    """ 
    Function print the overall node graph within the selected time window. 
  
    Require two table named identity and activity to retrive the data. 
  
    Parameters: 
    time_lower (datetime): Lower time limit
    time_upper (datetime): Upper time limit
  
    Returns: 
    None: Currently only prints, make changes in the last line to return value 
  
    """

    try:
        db_connection = mysql.connector.connect(
        host=prm.hostname,
        user=prm.username,
        passwd=prm.password,
        database= prm.dbname
        )
        db_cursor = db_connection.cursor()
    except:
        print("Can't Connect to database, check credentials in parameter file")

    query = ("SELECT * FROM activity WHERE time BETWEEN '{}' AND '{}'".format(time_lower,time_upper))
    db_cursor.execute(query)
    df2=pd.DataFrame(db_cursor.fetchall())
    if df2.empty:
        print("Empty activity database, Try again with different date or deviceid")
        return
    df2.columns= ['slno','time','node','lat','long']
    df2.lat = df2.lat.astype(float)
    df2.long = df2.long.astype(float)
    df2_grps= df2.groupby('node')

    for node,df in df2_grps:
        #print(node,df)
        tmp= imputer(df,time_lower)
        #print(tmp)
        query="INSERT INTO imputed(time,node,latitude,longitude) VALUES (%s,%s,%s,%s)"
        for i in range(len(tmp)):
            tm= datetime.datetime(tmp.iloc[i,0].year,tmp.iloc[i,0].month,tmp.iloc[i,0].day,tmp.iloc[i,0].hour,tmp.iloc[i,0].minute,tmp.iloc[i,0].second)
            db_cursor.execute(query,(tm,node,float(tmp.iloc[i,1]),float(tmp.iloc[i,2])))

        #####################plot Latitude################
        #plt.scatter(df.Time,df.Latitude, label="Filtered position")
        #plt.scatter(tmp.iloc[:,0],tmp.iloc[:,1])
        #plt.show()