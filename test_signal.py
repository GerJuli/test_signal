from  liesl import Session
import time
import numpy as np
import os
import pyxdf
import matplotlib.pyplot as plt

streamname = 'LuckyLoop'
subject = 'TeSt'
recording_time = 10

#%%
"""Record stream"""
streamargs = [{'name':streamname}]
session = Session(prefix=subject,
                  streamargs=streamargs)
conditions = [{'name': 'Eyes open', 'duration': 5}, {'name': 'Eyes closed', 'duration': 5}]


with session("task"):
    from reiz import Canvas, Cue, audio
    from reiz.visual import Mural
    canvas = Canvas()
    canvas.open()
    beep = audio.Hertz(frequency=800, duration_in_ms=100)
    buup = audio.Hertz(frequency=300, duration_in_ms=100)
    for condition in conditions:
        cue = Cue(canvas, visualstim=Mural(text=condition['name']), audiostim=beep)
        cue.show(duration=condition['duration'])
cue = Cue(canvas, visualstim=Mural(text='Finished'), audiostim=buup)
cue.show(duration=1000)
canvas.close()
#%%
"""Load last recorded stream"""
EEG_intervention_path_folder = f"{session.mainfolder}/{subject}/"
files = os.listdir(EEG_intervention_path_folder)
files = sorted(files)
last_EEG_file = files[-1]
EEG_intervention_path = f"{EEG_intervention_path_folder}{last_EEG_file}"

streams, fileheader = pyxdf.load_xdf(EEG_intervention_path) #load xdf file
#%%
"""Convert streams in dictr to make the easy to address"""
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
"""Plot channels"""
channels_to_plot = [1]
for channel_to_plot in channels_to_plot:
    """All channels normed to 1, to get a fast impression"""
    sampling_rate = streams_as_dict[streamname]['info']['effective_srate']
    samples_of_50Hz_period = int(round(sampling_rate/50))
    normed_signal = streams_as_dict[streamname]['time_series'][:,channel_to_plot]/np.max(streams_as_dict[streamname]['time_series'][:,channel_to_plot])
    filtered_signal = [normed_signal[i]-normed_signal[i-samples_of_50Hz_period] for i in range(50,len(normed_signal))]
    plt.plot(filtered_signal)

#%%
plt.close()
"""Power analysis of channels"""
channels_to_analyse = [1]
labels= []
for channel in channels_to_analyse:
    number_of_conditions = len(conditions)
    start_sample = 0
    data = streams_as_dict[streamname]['time_series'][:,channel]
    for idx, condition in enumerate(conditions):
        if not(idx == number_of_conditions-1):
            end_sample = int(condition['duration']*sampling_rate)
            sample_count = end_sample-start_sample
        else:
            end_sample = -1
            sample_count = len(data)-start_sample
        sampling_rate = streams_as_dict[streamname]['info']['effective_srate']
        condition_data = data[start_sample:end_sample]
        fft = np.fft.rfft(condition_data)
        power = abs(fft)
        x= [i*sampling_rate/sample_count for i in range(0,len(fft))]
        labels.append(f'Condition {condition["name"]}, channel: {channel}')
        plt.plot(x, power)
plt.xlabel("Frequency in Hz")
plt.ylabel("Power")
plt.legend(labels)