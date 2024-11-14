# IRWA

## Students

|Name | Email | UPF uNum |
| --- | --- | --- |
| Clara Pena | clara.pena01@estudiant.upf.edu | u186416 |
| Yuyan Wang | yuyan.wang01@estudiant.upf.edu | u199907 |

## How to Run the Notebook

0. The recommended approach would be to create a Python3 virtual environment and activate it; however it is not essentially needed. Skip to next step if you don't want to use a venv.

    ```
    $ python -m venv <nameVenv>
    $ source <youPathToVenvActivate>
    ```

1. Installing the necessary packages. We are providing the requirements.txt file.

    ```
    $ pip install -r requirements.txt
    ```

2. Use the corresponding Python3 as the Jupyter Notebook Kernel

3. Locate yourself inside the project part folder that you would like to execute. E.g. for part 1 you should cd the folder named `Part1`

    ```
    $ cd <projectPartXFolder>
    ```

4. The structure of the working directory for each part should look like:

    * [Part 1](./Part1/project1.ipynb): 
        ```
        Part1/
        ├── data/
        │   ├── evaluation_gt.csv
        │   ├── farmers-protest-tweets.json
        │   └── tweet_document_ids_map.csv
        ├── Fonts/
        │   ├── NotoSans.ttf
        │   ├── NotoSansDevanagari.ttf
        │   └── NotoSansGurmukhi.ttf
        ├── project1.ipynb
        └── processed_data.csv  # This will be generated after running the script
        ```
    
    * [Part 2](./Part2/project2.ipynb):
        ```
        Part2/
        ├── data/
        │   ├── processed_data.csv  # This would be the one generated from Part 1
        │   ├── evaluation_gt.csv
        │   └── personalized_evaluation_gt.csv
        └── project2.ipynb
        ```
    
    * [Part 3](./Part3/project3.ipynb):
        ```
        Part3/
        ├── data/
        │   ├── processed_data.csv  # This would be the one generated from Part 1
        ├── visualizations/ # All png will be generated after running the notebook
        │   ├── bjpparti.png 
        │   ├── humanrightviolat.png 
        │   ├── indiaprotest.png 
        │   ├── modishame.png 
        │   └── supportfarmer.png 
        └── project3.ipynb
        ```