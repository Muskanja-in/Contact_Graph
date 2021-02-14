import src
import datetime
#src.master.Run("20IN0F02",datetime.datetime.now()-datetime.timedelta(days=24)) # give two inputs, one device id and datetime
src.completegraph.fullgraphplot(datetime.datetime.strptime('2020-12-26 17:00:00', '%Y-%m-%d %H:%M:%S'),datetime.datetime.strptime('2020-12-27 17:00:00', '%Y-%m-%d %H:%M:%S')) #plot full graph
#src.trajectory.Run(datetime.datetime.strptime('2020-12-18 17:00:00', '%Y-%m-%d %H:%M:%S'),datetime.datetime.strptime('2020-12-29 17:00:00', '%Y-%m-%d %H:%M:%S'))
# trajectory function take time interval inputs and do the imputation for missing points with option to skip larger gap of missing points and saves the prediction in imputed table
#src.cluster1.Run(time1, time2)

