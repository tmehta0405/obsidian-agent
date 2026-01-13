import ollama
import os
import random
from dotenv import load_dotenv

load_dotenv()

with open("texts/questions.txt", 'r') as f:
    lines = f.readlines()
    question = random.choice(lines)

print(question)

def makeNote(question):
    with open("texts/template.txt", 'r') as f:
        prompt = f.read().replace("{{TOPIC}}", question)

    print(prompt)

    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    return response['message']['content']


def addToVault(note):
    try:
        title = (next((line.split(':', 1)[1].strip()
                         for line in note.split('\n')
                         if line.startswith('title:')), None).lower().replace(" ", "_"))

        location = next((line.split(':', 1)[1].strip()
                         for line in note.split('\n')
                         if line.startswith('category:')), None)
    except AttributeError:
        return

    path = f"test_vault/{location}"
    os.makedirs(path, exist_ok=True)

    with open(f"{path}/{title}.md", "w") as f:
        f.write(note)

    return f"{title} added to {location}."

note = makeNote(question)
print(note)
addToVault(note)