from dotenv import load_dotenv
load_dotenv() ## load all the environemnt variables
import google.generativeai as genai
import json
import os

from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
global prompt, memory, chain, llm, base_prompt

# --- Configuration ---
PROMPT_DIR = "prompts"
INSTRUCTIONS_FILE = "instructions.txt"
DATA_ANNOTATION_FILE = "data_annotation.json"

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

    print("BASE PROMPT LOADED!")
    return BASE_PROMPT_TEMPLATE

def init_components():
    global memory, chain, llm, base_prompt
    # Load the prompt
    base_prompt = load_prompt()
    if base_prompt == "ERROR: Instructions file missing.":
        print("ERROR: Instructions file missing. Cannot proceed.")
        return

    # Initialize the memory
    memory = ConversationBufferMemory(return_messages=True)

    # Create the chat model
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0, google_api_key=os.getenv("GOOGLE_API_KEY"))
    base_prompt = load_prompt()

    # Define the prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=base_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{input}")
    ])

    chain = prompt_template | llm

# Memory-aware response
def get_openai_response(question, prompts=None):
    history = memory.load_memory_variables({})["history"]
    # print("History: ", history)
    formatted_input = {
        "input": question,
        "history": history
    }
    response = chain.invoke(formatted_input)
    memory.save_context({"input": question}, {"output": response.content})
    return response.content

def translate_nl_to_ledis_json(natural_language_query):
    # prompt.append(load_prompt())
    # print(prompt)
    # Call the OpenAI API to get the JSON response
    response = get_openai_response(natural_language_query)
    # Strip ``json...``` if present
    response_cleaned = response.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(response_cleaned)


# if __name__ == "__main__":
#     question = "How are you today"
#     response = get_openai_response(question, prompt)
#     # Strip ``json...``` if present
#     response_cleaned = response.strip().removeprefix("```json").removesuffix("```").strip()
#     print(response_cleaned)
#     response_json = json.loads(response_cleaned)
#     print(response_json)