import pandas as pd
import random
from pathlib import Path

prompt_req = "Write an engaging and promotional website description for an SMB with the following attributes:"


def get_path(file_name):
    path = Path(__file__).parent / f"{file_name}"
    return path


def build_data_set(file_path: str):
    path = get_path(file_path)
    data = pd.read_csv(path)
    new_data = []
    for index, row in data.iterrows():
        prompt_str = prompt_req + "\n"
        prompt_str += "Business name: " + row['Business name']+"\n"
        prompt_str += "Location: " + row['Location'] + "\n"
        prompt_str += "Services: " + row['Services'] + "\n"
        prompt_str += "Benefits: " + row['Benefits'] + "\n"
        prompt_str += "Website content:"
        new_item = [prompt_str, " " + row['Website content']]
        new_data.append(new_item)
    df = pd.DataFrame(new_data, columns=['prompt', 'completion'])
    new_file_path = "resources/custom_ma_model_dataset_synthesized.csv"
    df.to_csv(new_file_path, index=False)


def build_few_shot_prompt(file_path="resources/moving_along_examples_short.csv"):
    path = get_path(file_path)
    data = pd.read_csv(path)
    prompt_str = ""
    for index, row in data.iterrows():
        prompt_str = single_prompt_builder(row, prompt_str)
        prompt_str += "\nWebsite content: \n" + row['Website content'] + "\n\n##\n\n"
    return prompt_str


def single_prompt_builder(row_data, prompt_str=""):
    prompt_str += prompt_req
    if row_data['Business name']:
        prompt_str += "Business name: " + row_data['Business name'] + "\n"
    if "Location" in row_data and row_data["Location"] is not None:
        prompt_str += "Location: " + row_data['Location'] + "\n"
    else:
        print("Location is empty")
    if "Services" in row_data and row_data["Services"] is not None:
        prompt_str += "Services: " + row_data['Services'] + "\n"
    else:
        print("Services are empty")
    if "Benefits" in row_data and row_data["Benefits"] is not None:
        prompt_str += "Benefits: " + row_data['Benefits'] + "\n"
    else:
        print("Benefits are empty")
    return prompt_str


def check_null_or_empty(business_name):
    if business_name is not None and business_name:
        return True
    return False

def read_txt(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            # print(file_content)
            return file_content
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
