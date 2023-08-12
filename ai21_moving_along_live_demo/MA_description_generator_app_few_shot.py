import streamlit as st
import requests
import re
import helpers as h

API_KEY = st.secrets['api-key']
selected_prompt = ""
few_shot_prompt_str = h.build_few_shot_prompt()
custom_model_prompt = h.read_txt(h.get_path("resources/custom_model_prompt.txt"))
custom_model_name = "ma_synthesized"
model_types = {
    "jumbo": "jumbo",
    "mid": "mid",
    "ultra": "ultra",
    "custom": "custom",
}
prompt_types = {
    "zero shot": "Zero-shot",
    "few shot": "Few-shot",
    "custom": "Custom model",
}


def validate_completion(response: str, business_name: str, lower_range=30, upper_range=50) -> bool:
    # 1. Validate business name in result
    # 2. Validate description is 30-50 words
    # return response.json()["completions"][0]["data"]["text"]
    words_arr = re.findall(r'\b\w+\b', response)
    completion_length = len(words_arr)
    print(f"Text length is: {completion_length}")
    if business_name is not None and business_name and lower_range <= completion_length <= upper_range:
        return True
    return False


# Main function - sending a completion request to Jurassic-2 models
def generate_text_by_params(input_model, input_text, temp=0, top_p=1, model="mid"):
    if input_model == "Custom model":
        model_url = f"https://api.ai21.com/studio/v1/j2-ultra/{custom_model_name}/complete"
    else:
        model_url = f"https://api.ai21.com/studio/v1/j2-ultra/complete"
    # Send the completion request
    response = requests.post(model_url,
                             headers={"Authorization": f"Bearer {API_KEY}"},
                             json={
                                 "prompt": input_text,
                                 "numResults": 1,
                                 "maxTokens": 60,
                                 "temperature": temp,
                                 "topKReturn": 0,
                                 "topP": top_p,
                                 "stopSequences": ["##"]
                             }
                             )
    if response.status_code != 200:
        raise Exception(f"Completion request failed with status {response.status_code}")
    return response.json()["completions"][0]["data"]["text"]


def get_prompt_by_selected_method(input_str):
    #     make prompt only with given attributes for zero shot or custom model
    if selected_model == prompt_types["zero shot"]:
        return h.single_prompt_builder(input_str)
    #     make prompt few shot with attributes
    elif selected_model == prompt_types["few shot"]:
        return h.single_prompt_builder(input_str, few_shot_prompt_str)
    #   make prompt for custom model with synthesized examples
    elif selected_model == prompt_types["custom"]:
        return h.single_prompt_builder(input_str, custom_model_prompt)
    return None


# Main:
# 1. Set sidebar attributes
# Fine tune temperature
# Fine tune TopP
# Select model

st.sidebar.title("Moving Along - AI21 Studio")
# Temperature config
st.sidebar.subheader("Temperature")
temperature = st.sidebar.slider("For a low temperature, we get a higher weight for the most probable token", min_value=0.00,
                                max_value=1.0, step=0.01, value=0.5)
st.sidebar.write("Temperature value: ", temperature)
# TopP config
st.sidebar.subheader("Top P")
top_p = st.sidebar.slider("Remove the tail of the tokens with the lowest probabilities (0 none/1all)", min_value=0.00, max_value=1.0, step=0.01,
                          value=0.9)
st.sidebar.write("TopP value: ", top_p)
st.header("Description Generation Portal")
st.subheader("Easily create compelling, engaging, and SEO-optimized business descriptions for any business website.")
options = prompt_types.values()
selected_model = st.sidebar.selectbox(label="Selected module", options=prompt_types.values(), index=1)

st.subheader("Business attributes")
st.write(f"Instruction: *{h.prompt_req}*")
business_name = st.text_input("Business Name", placeholder="Artisan Brew Co.", value="Artisan Brew Co.")
business_location = st.text_input("Location", placeholder="Austin, TX", value="Austin, TX")
business_services = st.text_input("Services", placeholder="Craft Beer Tasting, Brewery Tours, Private Events",
                                  value="Craft Beer Tasting, Brewery Tours, Private Events")
business_benefits = st.text_input("Benefits",
                                  placeholder="Locally Crafted Beers, Knowledgeable Brewers, Beer Club",
                                  value="Locally Crafted Beers, Knowledgeable Brewers, Beer Club")
if st.button(label="GENERATE CONTENT") and h.check_null_or_empty(business_name):
    input_prompt = {
            'Business name': business_name,
            'Location': business_location,
            'Services': business_services,
            'Benefits': business_benefits
    }
    new_prompt = get_prompt_by_selected_method(input_prompt)
    if not new_prompt:
        st.error("Problem with model selection or prompt, please try a different model or inputs")
    new_prompt += "\nWebsite content: \n"
    completion = generate_text_by_params(selected_model, input_text=new_prompt, temp=temperature, top_p=top_p,
                                         model="ultra")
    if not completion:
        st.error("Invalid input or problem connecting to server, please try again.")
    elif validate_completion(completion, business_name, 30, 50):
        st.subheader("Business Description")
        words = re.findall(r'\b\w+\b', completion)
        text_length = len(words)
        st.write(completion + f"\n\nWord count: {len(words)}")
    else:
        print(f"Completion: {completion}")
        word_count = len(completion.split())
        st.warning(f"Response was generated but did not meet criteria, please try again \n\n(word count: {word_count})")
elif not h.check_null_or_empty(business_name):
    st.error("No business name provided")
