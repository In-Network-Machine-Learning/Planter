# Adding Your Own Design
![Planter Logo](../../images/logo.png)
<aside>
💡 A guide to add your own dataset.

</aside>

## Adding your own dataset
 
 To use your own dataset, a load data file ```name_data.py``` should be created under ```./src/load_data``` folder. The load data file is responsible for loading the source data and preprocessing it based on your needs. The returned dataset should follow the same standard: ```return X_train, y_train, X_test, y_test, used_features```.

### ****The**** `name_data.py` ****file****

This file includes the preprocessing of the dataset. To prepare the training and learning on a new dataset, the dataset loading and preprocessing steps are necessary. With the `.csv` dataset files saved in a directory, several preprocessing steps need to be added in this load data file `name_data.py`, such as a) reading the dataset, b) replacing/removing the N/A values, c) encoding & selecting the features, and d) splitting the training/testing sets. The file includes one main function described below. 

### `load_data` **function**

- The overview of `load_data(*)` function

    ```python
    def load_data(num_features, data_dir):
        label_index = ... # the name of dataset label index 
        file_dir = data_dir+... # the dataset directory 
        files = []
        
        # read all the files under the dataset folder
        for dirpath, dirnames, filenames in os.walk(file_dir):
            for file in filenames:
              files.append(os.path.join(dirpath, file))
        ...
        return X_train, np.array(y_train), X_test, np.array(y_test), used_features
    ```

- The input of `load_data(*)` function

    ```python
    num_features # integer
                 # number of features to be used for model training
                 # read from the user input
    data_dir     # string
                 # the dataset directory    
    ```

- The output of `load_data(*)` function

    ```python
    X_train # data frame/ndarray/list
            # training data
    y_train # data frame/ndarray/list
            # the training labels
    X_test # data frame/ndarray/list
           # testing data
    y_test # data frame/ndarray/list
           # testing labels
    used_features # int
                  # number of used features
    ```
