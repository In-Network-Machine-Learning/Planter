########################################################################
# Copyright (c) 2021 Noa Zilberman, Changgang Zheng
# All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at :
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################
#
# Functions: This file extracts the log file's info.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import json
import os
import time

def compare_to_baseline(file, baseline):
    resources = json.load(open(file,'r'))
    resources_baseline = json.load(open(baseline, 'r'))

    sram_baseline=int(resources_baseline['mau']['srams'])
    tcam_baseline=int(resources_baseline['mau']['tcams'])
    latency_baseline=int(resources_baseline['mau']['latency'][0]['cycles'])

    sram=int(resources['mau']['srams'])/sram_baseline
    tcam=int(resources['mau']['tcams'])/tcam_baseline
    mems=(sram+tcam)/2
    lat=int(resources['mau']['latency'][0]['cycles'])/latency_baseline
    cycle = resources['mau']['latency'][0]['cycles']
    print("The tested model requires relatively - Latency: {:.4} Memory: {:.4} SRAM: {:.4} TCAM: {:.4}  cycles: {}".format(lat,mems,sram,tcam,cycle))
    print("The tested model requires absolute - Latency: "+str(int(resources['mau']['latency'][0]['cycles'])) +" SRAM: "+str(int(resources['mau']['srams']))+" TCAM: "+str(int(resources['mau']['tcams'])))


def absolute_result(file):
    resources = json.load(open(file,'r'))
    sram=int(resources['mau']['srams'])/960
    tcam=int(resources['mau']['tcams'])/288
    mems=(sram+tcam)/2
    cycle = resources['mau']['latency'][0]['cycles']
    print("The tested model requires relatively - Memory: {:.4} SRAM: {:.4} TCAM: {:.4} Latency (cycles): {}".format(mems,sram,tcam,cycle))
    print("The tested model requires absolute - Latency: "+str(int(resources['mau']['latency'][0]['cycles'])) +" SRAM: "+str(int(resources['mau']['srams']))+" TCAM: "+str(int(resources['mau']['tcams'])))


def extract_stage_consumption(file_name):
    with open(file_name, 'r') as file:
        for i, line in enumerate(file.readlines()):
            if i == 1:
                print(line,end="")
                break

def print_log_file(file_name):
    while True:
        if os.path.exists(file_name):
            time.sleep(1)
            break
    with open(file_name, 'r') as file:
        for i, line in enumerate(file.readlines()):
            print(line, end="")
