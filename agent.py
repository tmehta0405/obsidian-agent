import ollama
import os
import random
from dotenv import load_dotenv

load_dotenv()

def generatePrompts():
    with open("texts/questions.txt", 'r', encoding='utf-8') as f:
        history = f.read()

    with open("texts/question_template.txt", 'r', encoding='utf-8') as f:
        prompt = f.read().replace("{{HISTORY}}", history)

    response = ollama.chat(
        model=os.getenv("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    print("Made questions")

    with open('texts/questions.txt', 'a', encoding='utf-8') as f:
        f.write(response['message']['content'])


def getQuestion():
    with open("texts/questions.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines = [line for line in lines if line.strip()]

    question = random.choice(lines)
    lines.remove(question)

    with open("texts/questions.txt", 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return question

def makeNote(question):
    with open("texts/obsidian_template.txt", 'r', encoding='utf-8') as f:
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
        title = next((line.split(':', 1)[1].strip()
                         for line in note.split('\n')
                         if line.startswith('title:')), None).lower().replace(" ", "_")

        location = next((line.split(':', 1)[1].strip()
                         for line in note.split('\n')
                         if line.startswith('category:')), None)
    except AttributeError:
        return

    direc = "test_vault"
    path = f"{direc}/{location}"
    os.makedirs(path.lower(), exist_ok=True)

    with open(f"{path}/{title}.md", "w", encoding='utf-8') as f:
        f.write(note)

    return f"{title} added to {location}."


note = makeNote(getQuestion())
print(note)
addToVault(note)
generatePrompts()



