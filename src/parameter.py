class Para:
    def __init__(self):
        self.hostname="localhost"
        self.username="root"
        self.password="1234"
        self.dbname="contactgraph"
        self.duration= 14    # in days
        self.infectdist= 50 # in metres (infection radius, default value keep around 10)
        self.tstep = 3600  # the current timestep for activity data in seconds
        self.units = 10 #  maximum allowed units of tstep missing from the geo-coordinates data for imputation