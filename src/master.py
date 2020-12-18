from .func import *
from . import parameter as param
import mysql.connector
import pandas as pd
import datetime

def Run(deviceid, time_ref):
	""" 
    Function print the nodes which came in contact with infected node in past few days. 
  
    Require two table named identity and activity to retrive the data and duration from parameters. 
  
    Parameters: 
    deviceid (string): Contains the device id
    time_ref (datetime): Reference time from which we want to check for the past duration days
  
    Returns: 
    None: Currently only prints, make changes in the last line to return value 
  
    """
	prm = param.Para()
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
	query = ("SELECT * FROM identity ")
	db_cursor.execute(query)
	df1=pd.DataFrame(db_cursor.fetchall())
	df1.columns= ['node','deviceid','student','rollno']
	inf_node= df1[df1.deviceid==deviceid].iloc[0]['node']
	query = ("SELECT MIN(time) FROM activity")
	db_cursor.execute(query)
	row = db_cursor.fetchone()
	begin_time=row[0]
	query = ("SELECT * FROM activity WHERE time BETWEEN '{}' AND '{}'".format(max(begin_time,time_ref-datetime.timedelta(days=prm.duration)),time_ref))  ## incomplete
	db_cursor.execute(query)
	df2=pd.DataFrame(db_cursor.fetchall())
	if df2.empty:
		print("Empty activity database, Try again with different date or deviceid")
		return
	df2.columns= ['slno','time','node','lat','long']
	df_inf= df2[df2.node==inf_node]
	df2= df2[df2.node!=inf_node]
	score={}
	for i in range(len(df_inf)):
		time_inf= df_inf.iloc[i,1]
		score_tmp= decayfunc(time_inf,time_ref)
		df_tmp= df2[df2.time==time_inf]
		for j in range(len(df_tmp)):
			if proximityfunc(df_inf.iloc[i,3],df_inf.iloc[i,4],df2.iloc[j,3],df2.iloc[j,4]):
				try:
					score[df_tmp.iloc[j,2]]+= score_tmp
				except:
					score[df_tmp.iloc[j,2]]= score_tmp

	ans=sorted( ((v,k) for k,v in score.items()), reverse=True)
	for (val,key) in ans:
		print("node no. => ",key," and score =>",val)