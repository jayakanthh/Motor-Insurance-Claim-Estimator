import ollama
import base64
import os

def check_ollama():
    print("Checking Ollama connection...")
    try:
        response = ollama.list()
        print("Available models:", response)
        
        # Check if llava:7b is present
        # The ollama library structure might have changed, let's print and see
        models = response.get('models', [])
        
        has_llava = False
        for m in models:
            # Check if model object has 'model' or 'name' attribute
            name = getattr(m, 'model', None) or getattr(m, 'name', None) or m.get('name')
            if name and 'llava:7b' in name:
                has_llava = True
                break
                
        if has_llava:
            print("✅ llava:7b model found.")
        else:
            print("❌ llava:7b model NOT found. Please run 'ollama pull llava:7b'")
            return

        print("\nTesting simple prompt...")
        chat_resp = ollama.chat(model='llava:7b', messages=[
            {'role': 'user', 'content': 'Is this a car?'}
        ])
        print("Response:", chat_resp['message']['content'])
        print("✅ Ollama is responding.")
        
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")

if __name__ == "__main__":
    check_ollama()
