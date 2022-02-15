#authors: oakazan and huseyin
#automatation of ffmpeg H.264 and vmaf
"""
This script takes video paths and encode with encoder
and compare with vmaf tool
"""

import os,sys 
import numpy as np
import pandas as pd
import time
import csv
import json



original_video_path="/home/oakazan/"#It changes for each video path
original_video_name = original_video_path+"file_example_MP4_1920_18MG.mp4"#Original video path + Original video name



"""
data frame coulmns:Index, preset,CRF(Constant Rate Factor),runtime, file name, file size, codec type,vmaf score
"""
df = pd.DataFrame(columns=['PRESET TYPE','CRF','RUNTIME(sn)','FILE NAME','FILE SIZE(MB)','CODEC TYPE','VMAF SCORE'])#It keeps parameters for csv file

crf=["10","20","30","40","50"]#0 is min value,51 is max value
preset=["ultrafast","superfast","veryfast","faster","fast","medium","slow","slower","veryslow"]#encoding speed options





for p in preset:#for reach each preset type
    for c in crf:#for reach each crf value
        output_file = "h264_crf" + c + "_" + p + ".mp4"
        ffmpeg_command = "ffmpeg -i " + original_video_name + " -c:v libx264 -preset " + p + " -crf " + c + " -c:a copy " + output_file
        
        #x -> start time
        startime= time.time()
        os.system(ffmpeg_command)
        runtime = time.time() -startime
        runtime= int(runtime)

        #y -> stop time
        #y-x = runtime
        


        fileSize = os.path.getsize(original_video_path+""+output_file) #It keeps file size for dataFrame
        fileSize = fileSize/(1024*1024) #converting process(byte to megabyte)

        
        vmaf_command = vmaf_command = """ffmpeg  -i """+output_file+""" -i """+original_video_name+""" -lavfi "libvmaf=n_subsample=1000:model_path=/usr/local/share/model/vmaf_v0.6.1.json:log_fmt=json:log_path=./"""+output_file+""".json" -f null -"""
        os.system(vmaf_command)
        #vmaf command gives output as Json file, So we get data from that Json file


        output_json=output_file+'.json'
        #read file
        data={}
        # we need convert Json to dictionary
        with open(output_json) as json_file:
            data = json.load(json_file) 
            json_file.close()
        

        vmaf_value=data["frames"][0]["metrics"]["vmaf"]#It pulls the vmaf value from the json file created by this vmaf 
        

        #It appends the datas into dataFrame 
        df= df.append({'PRESET TYPE' : p,
                        'CRF' : c,
                        'RUNTIME' : runtime,
                        'FILE NAME' : output_file,
                        'FILE SIZE' : fileSize,
                        'CODEC TYPE' : 'H.264',
                        'VMAF SCORE' : vmaf_value },ignore_index=True) 

df.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')
df.to_csv('encode_result.csv')#Creates a csv file and dumps the encoder benchmark results into it