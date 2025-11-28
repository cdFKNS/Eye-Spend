import os
import toml
import google.generativeai as genai

# Load API Key
api_key = os.environ.get("API_KEY")
if not api_key:
    try:
        secrets = toml.load(".streamlit/secrets.toml")
        api_key = secrets.get("GEMINI_API_KEY")
    except Exception as e:
        pass

if not api_key:
    print("API Key not found!")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
