from dotenv import load_dotenv
load_dotenv() ## load all the environemnt variables
import google.generativeai as genai
import json
import os

# --- Configuration ---
PROMPT_DIR = "prompts"
INSTRUCTIONS_FILE = "instructions.txt"
DATA_ANNOTATION_FILE = "data_annotation.json" # Renamed for consistency with earlier suggestions

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = []

def load_prompt():
    global prompt
    instructions_path = os.path.join(PROMPT_DIR, INSTRUCTIONS_FILE)
    data_annotation_path = os.path.join(PROMPT_DIR, DATA_ANNOTATION_FILE)
    data_json_string = "[]"
    BASE_PROMPT_TEMPLATE = ""
    try:
        with open(instructions_path, 'r', encoding='utf-8') as f:
            instruction_template = f.read()
    except FileNotFoundError:
        print(f"ERROR: Prompt instructions file not found: {instructions_path}")
        BASE_PROMPT_TEMPLATE = "ERROR: Instructions file missing." # Set error state
        return
    except Exception as e:
        print(f"ERROR: Could not read prompt instructions: {e}")
        BASE_PROMPT_TEMPLATE = f"ERROR: Reading instructions failed: {e}"
        return

    try:
        with open(data_annotation_path, 'r', encoding='utf-8') as f:
            data = json.load(f) 
        # Convert the Python list of example dicts into a pretty-printed JSON string
        data_json_string = json.dumps(data, indent=2)
    except FileNotFoundError:
        print(f"ERROR: Prompt examples file not found: {data_annotation_path}")
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse prompt examples JSON from {data_annotation_path}")
    except Exception as e:
        print(f"ERROR: Could not read prompt examples: {e}")

    if "${DATA_ANNOTATION}" in instruction_template:
        BASE_PROMPT_TEMPLATE = instruction_template.replace("${DATA_ANNOTATION}", data_json_string)
    else:
        print("WARNING: Placeholder ${DATA_ANNOTATION} not found in instructions.txt. Examples will not be injected as expected.")

    return BASE_PROMPT_TEMPLATE

def get_openai_response(question, prompt):
    model=genai.GenerativeModel('gemini-2.0-flash')
    response=model.generate_content([prompt[0],question])
    # print(response)
    return response.text

def translate_nl_to_ledis_json(natural_language_query):
    # prompt.append(load_prompt())
    # print(prompt)
    # Call the OpenAI API to get the JSON response
    response = get_openai_response(natural_language_query, prompt)
    # Strip ``json...``` if present
    response_cleaned = response.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(response_cleaned)

# if __name__ == "__main__":
#     prompt.append(load_prompt())
#     print(prompt)

# if __name__ == "__main__":
#     question = "How are you today"
#     response = get_openai_response(question, prompt)
#     # Strip ``json...``` if present
#     response_cleaned = response.strip().removeprefix("```json").removesuffix("```").strip()
#     print(response_cleaned)
#     response_json = json.loads(response_cleaned)
#     print(response_json)