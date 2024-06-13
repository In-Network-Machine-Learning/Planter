# Planter Tutorial : Run RF<sub>EB</sub> on BMv2
![Planter Logo](../../images/logo.png)
<aside>
💡 A guide to set up RF<sub>EB</sub> on BMv2 via Planter.

</aside>


 

## Requirements

1. BMv2 supported
2. All needed python packets installed

## Let's "Planting" RF<sub>EB</sub> on BMv2 now

- Run Planter with ```-m``` (manually config) mode:
  
  ### Step 1: Directory options
  Input:
    ```
    python3 Planter.py -m
    ``` 
  
  Output:
    ```
    (base) changgang@linux:~/Planter$ python3 Planter.py -m
     ____    ___                    __ 
    /\  _`\ /\_ \                  /\ \__ 
    \ \ \L\ \//\ \      __      ___\ \ ,_\    __  _ __ 
     \ \ ,__/ \ \ \   /'__`\  /' _ `\ \ \/  /'__`/\`'__\ 
      \ \ \/   \_\ \_/\ \L\.\_/\ \/\ \ \ \_/\  __\ \ \/ 
       \ \_\   /\____\ \__/.\_\ \_\ \_\ \__\ \____\ \_\ 
        \/_/   \/____/\/__/\/_/\/_/\/_/\/__/\/____/\/_/ 
                                          Version 0.0.1

    Please set the following directories:
    - Where is your data folder? (default = '/home/Data')
    ``` 
  
  Press ```enter``` if default is correct. Otherwise, input the correct directory and press ```enter```:

  Output:
    ```
    - Where is your Planter folder? (default = '/home/Planter')
    ``` 
  Press ```enter``` if default is correct. Otherwise, input the correct directory and press ```enter```:
  
  ### Step 2: Model options
  Output:
    ```
    - Which model do you want to plant? (default = DT | options = -h) 
    ``` 
  
  Input ```RF```  press ```enter``` :

  Output:
    ```
    - Which type of model you want to plant? (default = 1 | options = -h) 
    ``` 
  
  Input ```EB```  press ```enter``` :
  
  Output:
    ```
    - Which dataset do you want to use? (default = UNSW_5_tuple | options = -h) 
    ``` 
  
  ### Step 3: Dataset options
  Input ```Iris```  press ```enter``` :

  Output:
    ```
    - Number of features? (default = 5) 
    ```
  Input ```4```  press ```enter``` :

  Output:
    ```
    src/configs/Planter_config.json is generated
    - Use the testing mode or not? (default = y) 
    ``` 
  
  :information_source: Testing mode randomly selects 2000 samples from the dataset for fast training.
  
  Input ```n```  press ```enter``` :

  Output:
    ```
    The shape of the dataset -  train x:  (105, 4) train y:  (105,) test x:  (45, 4) test y:  (45,)
    Add the following path: /home/Planter/src/models/RF/Type_EB
    - Number of trees? (default = 5) 
    ``` 
  Input ```5```  press ```enter``` :

  Output:
    ```
    - Number of depth? (default = 4)
    ``` 
  Input ```4```  press ```enter``` :

  Output:
    ```
    - Number of leaf nodes? (default = 1000) 
    ```  
  
  Input ```1000```  press ```enter``` :

  Output:
  
  (The output matrix gives the classification performance of the scikit-learn model on python.)
    ```
                   precision    recall  f1-score   support
    
               0     1.0000    1.0000    1.0000        13
               1     0.9500    0.9500    0.9500        20
               2     0.9167    0.9167    0.9167        12
    
        accuracy                         0.9556        45
       macro avg     0.9556    0.9556    0.9556        45
    weighted avg     0.9556    0.9556    0.9556        45

    Classification results are downloaded to log as src/logs/log.json
    The table for Tree: 4 is generated
    Generating vote to class table...Done
    Begin transfer: Feature table 0
    Input table has:  80 entries and:  6  different ranges and output TCAM entry has 15
    80th testing sample with correct matches: 100.0 % and 0 errors. 
    Begin transfer: Feature table 1
    Input table has:  45 entries and:  5  different ranges and output TCAM entry has 11
    45th testing sample with correct matches: 100.0 % and 0 errors. 
    Begin transfer: Feature table 2
    Input table has:  70 entries and:  7  different ranges and output TCAM entry has 16
    70th testing sample with correct matches: 100.0 % and 0 errors. 
    Begin transfer: Feature table 3
    Input table has:  26 entries and:  7  different ranges and output TCAM entry has 12
    26th testing sample with correct matches: 100.0 % and 0 errors. 

    Ternary_Table is generated
    Exact_Table is generated
    /home/Planter/src/configs/Planter_config.json is generated
    - Test the table or not? (default = y) 
    ``` 
  Input ```y```  press ```enter``` :

  Output:
  
  (The output matrix gives the classification performance from the pipeline logic by using the generated table entries on python.)
    ```
    Test the exact feature table, extract code, and decision table (feel free if the acc to sklearn is slightly lower than 1)
    switch_prediction: 1, test_y: 1, with acc: 0.956, with acc to sklearn: 1.0, with error: 0.0, M/A format macro f1: 0.955, macro f1: 0.955 
    The accuracy of the match action format of Random Forest is 0.9555555555555556
    
                   precision    recall  f1-score   support

               0     1.0000    1.0000    1.0000        13
               1     0.9500    0.9500    0.9500        20
               2     0.9167    0.9167    0.9167        12

        accuracy                         0.9556        45
       macro avg     0.9556    0.9556    0.9556        45
    weighted avg     0.9556    0.9556    0.9556        45
    
    src/configs/Planter_config.json is generated
    Exact match entries:  187
    Ternary match entries:  54
    - Which architecture do you use? (default = tna | options = -h) 
    ```  
  
  ### Step 4: Target & architecture options  
  Input ```v1model```  press ```enter``` :

  Output:
    ```
    - Which is the use case? (default = standard_classification | options = -h)
    ``` 
  Input ```performance``` press ```enter``` :

  Output:
    ```
    Add the following path: /home/Planter/src/use_cases/standard_classification
    Add the following path: /home/Planter/src/architectures/v1model
    Generating p4 files and load data file... Done
    - What is the target device? (default = Tofino | options = -h) 
    ```  
  
  Input ```bmv2```  press ```enter``` :

  Output:
    ```
    - Which type of mode do you want to choose? (default = software | options = -h) 
    ``` 
  Input ```software```  press ```enter``` :

  Output:
    ```
    Dump the targets info to src/configs/Planter_config.json
    Add the following path: /home/Planter/src/targets/bmv2/software
    - Send packets to which port? (default = 'eth0'):
    ```  
  
  Input ```eth0```  press ```enter``` :

  Output:
    ```
    - Please input your password for 'sudo' command:
    ``` 
  Input ```your_own_sudo_password```  press ```enter``` :

  Output:
  
  (The output matrix gives the classification result of generated P4 on BMv2 in emulated Mininet environment.)
    ```
    ip link show
    *** Killing stale mininet node processes
    pkill -9 -f mininet:
    *** Shutting down stale tunnels
    pkill -9 -f Tunnel=Ethernet
    pkill -9 -f .ssh/mn
    rm -f ~/.ssh/mn/*
    *** Cleanup complete.
    rm -f *.pcap
    rm -rf build pcaps logs
    mkdir -p build pcaps logs
    p4c-bm2-ss --p4v 16 --p4runtime-files build/RF_performance_Iris.p4.p4info.txt -o build/RF_performance_Iris.json RF_performance_Iris.p4
    sudo python3 ../../utils/run_exercise.py -t topology.json -j build/RF_performance_Iris.json -b simple_switch_grpc
    Reading topology file.
    Building mininet topology.
    Configuring switch s1 with file s1-commands.txt
    s1 -> gRPC port: 50051
    **********
    h1
    default interface: eth0 10.0.1.1        08:00:00:00:01:01
    **********
    Starting mininet CLI
    
    ======================================================================
    Welcome to the BMV2 Mininet CLI!
    ======================================================================
    Your P4 program is installed into the BMV2 software switch
    and your initial runtime configuration is loaded. You can interact
    with the network using the mininet CLI below.
    
    To inspect or change the switch configuration, connect to
    its CLI from your host operating system using this command:
      simple_switch_CLI --thrift-port <switch thrift port>

    To view a switch log, run this command from your host OS:
      tail -f /home/changgang/Documents/GitHub/Planter/src/targets/bmv2/software/model_test/test_environment/logs/<switchname>.log
    
    To view the switch output pcap, check the pcap files in /home/changgang/Documents/GitHub/Planter/src/targets/bmv2/software/model_test/test_environment/pcaps:
     for example run:  sudo tcpdump -xxx -r s1-eth1.pcap

    To view the P4Runtime requests sent to the switch, check the
    corresponding txt file in /home/changgang/Documents/GitHub/Planter/src/targets/bmv2/software/model_test/test_environment/logs:
     for example run:  cat /home/changgang/Documents/GitHub/Planter/src/targets/bmv2/software/model_test/test_environment/logs/s1-p4runtime-requests.txt

    mininet> Predicted load table time ... (0.037s)

    ==============================================================================================
    =        Two steps to exit Planter: 1. input 'exit', press 'return'; 2. press ctrl + c       =
    ==============================================================================================
    Test the switch model, the result should be the same as previous python test
    Switch model 45th prediction: 1, test_y: 1, with acc: 0.956, with acc to sklearn: 1.0, with error: 0.0, M/A format macro f1: 0.9556, macro f1: 0.9556

                   precision    recall  f1-score   support

               0     1.0000    1.0000    1.0000        13
               1     0.9500    0.9500    0.9500        20
               2     0.9167    0.9167    0.9167        12

        accuracy                         0.9556        45
       macro avg     0.9556    0.9556    0.9556        45
    weighted avg     0.9556    0.9556    0.9556        45

    ======================================= Test Finished ========================================
    mininet> 
    Process <load data> cost 0.0073s
    Process <train model> cost 0.0154s
    Process <convert model> cost 0.0182s
    Process <python-based test> cost 0.0779s
    ```  
  ### Test Finished! :tada:
  
    
