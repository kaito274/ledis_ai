# Ledis AI 🧠💾 
A lightweight, AI-augmented in-memory data store inspired by Redis. This project supports string and list operations, and integrates natural language commands via a generative AI interface.


## 🔧 Features

- Basic Redis-like commands: `SET`, `GET`, `RPUSH`, `LPOP`, `LRANGE`, etc.
- Natural Language Interface: Use plain English to interact with Ledis via AI.
- Modular design for extensibility (CLI, Server, AI interface)
- Context memory with Langchain for AI interactions


## 📦 Requirements

- Python 3.10+
- `pip`, `venv`
- Access to Google Gemini API (or any supported Google Generative AI model)

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/kaito274/ledis_ai.git
cd ledis_ai
```


### 2️⃣ Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# OR
venv\Scripts\activate     # On Windows

pip install --upgrade pip
pip install -r requirements.txt
```


### 3️⃣ Set Up `GOOGLE_API_KEY`
Create a `.env` file in the project root with your Google API key:
```plaintext
GOOGLE_API_KEY=your_google_api_key_here
```
You need a Google API key for Gemini.  
- 🔑 Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).


### 4️⃣ Run the Application

#### A. Start the Ledis Server

```sh
python ledis_server.py
```

The server will start on `http://0.0.0.0:5000/`.

#### B. Start the Ledis CLI

Open another terminal (with the virtual environment activated):

```sh
python ledis_cli.py
```

You can now type commands (e.g., `SET mykey 123`, `GET mykey`, or `CHAT show all keys`) in the CLI.


### 5️⃣ Example Usage

```plaintext
127.0.0.1:5000> SET foo bar
OK
127.0.0.1:5000> GET foo
bar
127.0.0.1:5000> CHAT show all keys
KEYS -> "foo"
```


### 6️⃣ Troubleshooting

- If you see errors about missing prompt files, ensure `prompts/instructions.txt` and `prompts/data_annotation.json` exist.
- If you see API errors, check your `.env` and Google API key.
- If you see connection errors, make sure the server is running before starting the CLI.
