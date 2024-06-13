# Adding Your Own Design
![Planter Logo](../../images/logo.png)
<aside>
💡 A guide to add your own architecture.

</aside>

## Adding your own architecture
To add new P4 architecture, we need to add a new generator file ```p4_generator.py``` under the directory ```./src/architectures/<architecture_name>```. File ```p4_generator.py``` is the key component in the P4 generation process which is able to drive the model related file ```dedicated_p4.py``` and the use case related file```common_p4.py``` to collaboratively generate overall the P4 file.
### The ```p4_generator.py``` file
In ```p4_generator.py```, the key function is ```main(*)```, which will be called by ```Planter.py```. The ```main(*)``` is able to call functions in ```dedicated_p4.py``` and ```common_p4.py```.

#### Import functions
```
from dedicated_p4 import *
from common_p4 import *
``` 

#### ```main(*)``` function
- The overview of ```main(*)``` function
    ```
    def def main():
        # 1. Load configuration from file
        config, Planter_config = load_config(config_file)
        # 2. Write an introduction in your P4 file header
        add_model_intro(p4_file, config)
        # 3. Call functions in ```p4_generator.py```, ```dedicated_p4.py``` and ```common_p4.py```
        #    to generate your P4 file
        return 
    ``` 
