import json
import os, sys
import numpy as np
import pandas as pd
import time
import csv

original_video_path="/home/oakazan/" #It changes for each video path
input_video_name="Big_Buck_Bunny_1080_10s_30MB.mp4"
original_video_name = original_video_path + input_video_name #Original_video_name + Original_video_path

df = pd.DataFrame(columns=['PRESET TYPE','CRF','RUNTIME','FILE NAME','FILE SIZE_original','FILE SIZE_encoded','CODEC TYPE','VMAF SCORE','BITRATE_original','BITRATE_encoded','FPS_original','FPS_encoded'])#It keeps parameters for csv file

crf=["10","20","30","40","50"]#0 is min value,51 is max value
preset=["ultrafast","superfast","veryfast","faster","fast","medium","slow","slower","veryslow"]#encoding speed options


fileSize_original= os.path.getsize(original_video_name)#It keeps file size for dataFrame
fileSize_original=9.537*(10**-7)*(fileSize_original)
fileSize_original=round(fileSize_original,2)
#ffprobe -v quiet -print_format json -show_format -show_streams '/path/media/thevideo.mp4' > thevideo.json

ffprobe_command="""ffprobe -v quiet -print_format json -show_format -show_streams """+original_video_name+""" > """ + input_video_name+ """_ffprobe.json"""
os.system(ffprobe_command)

BITRATE_original=float()
FPS_original=float()
ffprobe_dict=dict()

with open(input_video_name +'_ffprobe.json') as tempjsonFile :
    ffprobe_dict=json.load(tempjsonFile)
    BITRATE_original=int(ffprobe_dict['streams'][0]['bit_rate'])
    FPS_original=ffprobe_dict['streams'][0]['r_frame_rate']
    
    FPS_original=FPS_original.split("/")
    FPS_original=float(FPS_original[0]) / float(FPS_original[1])



for p in preset:#for reach each preset type
    for c in crf:#for reach each crf value

        output_file="h265_crf" + c + "_" + p + ".mp4"
        ffmpeg_command = "ffmpeg -i "+original_video_name+" -c:v libx265 -crf "+ c +" -preset "+ p +" -c:a aac -b:a 128k "+ output_file



        startime= time.time()
        os.system(ffmpeg_command)
        runtime = time.time() -startime
        runtime= int(runtime)

        ffprobe_command="""ffprobe -v quiet -print_format json -show_format -show_streams """+ original_video_path + output_file +""" > """ + output_file+ """_ffprobe.json"""
        os.system(ffprobe_command)

        BITRATE_encoded=int()
        FPS_encoded=int()
        ffprobe_dict_encoded=dict()

        with open(output_file +'_ffprobe.json') as temp_encoded_jsonFile :
            ffprobe_dict_encoded=json.load(temp_encoded_jsonFile)
            BITRATE_encoded=int(ffprobe_dict_encoded['streams'][0]['bit_rate'])
            FPS_encoded=ffprobe_dict_encoded['streams'][0]['r_frame_rate']

            FPS_encoded=FPS_encoded.split("/")
            FPS_encoded=float(FPS_encoded[0]) / float(FPS_encoded[1])

        #####ffprobe process


        fileSize_encoded= os.path.getsize(original_video_path+output_file)#It keeps file size for dataFrame
        fileSize_encoded=9.537*(10**-7)*(fileSize_encoded)
        fileSize_encoded=round(fileSize_encoded,2)


        vmaf_command = vmaf_command = """ffmpeg  -i """+output_file+""" -i """+original_video_name+""" -lavfi "libvmaf=n_subsample=1000:model_path=/usr/local/share/model/vmaf_v0.6.1.json:log_fmt=json:log_path=./"""+output_file+""".json" -f null -"""
        os.system(vmaf_command)

        temporary_dict=dict()
        with open(output_file +'.json') as jsonFile :
            temporary_dict=json.load(jsonFile)

        vmaf_value= temporary_dict['frames'][0]['metrics']['vmaf']  #It pulls the vmaf value from the json file created by this vmaf

        df= df.append({'PRESET TYPE' : p,
                    'CRF' : c,
                    'RUNTIME' : runtime,
                    'FILE NAME' : output_file,
                    'FILE SIZE_original':fileSize_original,
                    'FILE SIZE_encoded' : fileSize_encoded,
                    'CODEC TYPE' : 'H.265',
                    'VMAF SCORE' : vmaf_value,
                    'BITRATE_original':BITRATE_original ,
                    'BITRATE_encoded' :BITRATE_encoded,
                    'FPS_original':FPS_original,
                    'FPS_encoded':FPS_encoded} , ignore_index=True)

df.to_csv('encode_result_265.csv')#Creates a csv file and dumps the encoder benchmark results into it.
