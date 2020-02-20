from  liesl import Session
import time
import numpy as np
import os
import pyxdf
import matplotlib.pyplot as plt

streamname = 'LuckyLoop'
subject = 'TeSt'
recording_time = 10

streamargs = [{'name':streamname}]


session = Session(prefix=subject,
                  streamargs=streamargs)


with session("task"):
    time.sleep(recording_time)

#%%

EEG_intervention_path_folder = f"{session.mainfolder}/{subject}/"
files = os.listdir(EEG_intervention_path_folder)
files = sorted(files)
last_EEG_file = files[-1]
EEG_intervention_path = f"{EEG_intervention_path_folder}{last_EEG_file}"

streams, fileheader = pyxdf.load_xdf(EEG_intervention_path) #load xdf file
#%%
streams_as_dict = {}
for ix, stream in enumerate(streams):
    streamname = stream['info']['name'][0]
    streams_as_dict[streamname] = stream
    print(streamname)
    if any(stream['time_stamps']):
        print("\tDuration: {} s".format(stream['time_stamps'][-1] - stream['time_stamps'][0]))
    print(stream.keys())
    print("")
#%%
channels_to_plot = [11,14,15]
for channel_to_plot in channels_to_plot:
    """All channels normed to 1, to get a fast impression"""
    plt.plot(streams_as_dict[streamname]['time_series'][:,channel_to_plot]/np.max(streams_as_dict[streamname]['time_series'][:,channel_to_plot]))