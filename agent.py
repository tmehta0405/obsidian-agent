import ollama
import os
import random
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

def webSearch(query, max_results=5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

            search_context = f"Web search results for: {query}\n\n"
            for i, result in enumerate(results, 1):
                search_context += f"{i}. {result['title']}\n"
                search_context += f"   {result['body']}\n"
                search_context += f"   URL: {result['href']}\n\n"

            return search_context
    except Exception as e:
        print(f"Search error: {e}")
        return ""


def getVaultContents():
    vault_dir = "test_vault"
    vault_summary = "Existing notes in vault:\n\n"

    if not os.path.exists(vault_dir):
        return "No existing vault found."

    note_count = 0
    for root, dirs, files in os.walk(vault_dir):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                category = os.path.basename(root)

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    title_line = next((line for line in content.split('\n')
                                       if line.startswith('title:')), None)
                    if title_line:
                        title = title_line.split(':', 1)[1].strip()
                    else:
                        title = file.replace('.md', '').replace('_', ' ')

                vault_summary += f"- {title} (Category: {category})\n"
                note_count += 1

    vault_summary += f"\nTotal notes: {note_count}\n"
    return vault_summary


def generatePrompts():
    with open("texts/questions.txt", 'r', encoding='utf-8') as f:
        history = f.read()

    vault_contents = getVaultContents()

    with open("texts/question_template.txt", 'r', encoding='utf-8') as f:
        prompt = f.read().replace("{{HISTORY}}", history)

    prompt += f"\n\n{{VAULT_CONTENTS}}\n{vault_contents}\n\nMake sure to generate questions about topics NOT already covered in the vault."

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
        base_prompt = f.read().replace("{{TOPIC}}", question)

    system_instruction = """You can request web searches if you need current information or factual data.
    To request a search, respond with: SEARCH: <your search query>
    After receiving search results, write the note as requested."""

    messages = [
        {
            "role": "system",
            "content": system_instruction
        },
        {
            "role": "user",
            "content": base_prompt
        }
    ]

    max_iterations = 3
    for iteration in range(max_iterations):
        response = ollama.chat(
            model=os.getenv("OLLAMA_MODEL"),
            messages=messages
        )

        response_text = response['message']['content']

        if response_text.strip().startswith("SEARCH:"):
            search_query = response_text.replace("SEARCH:", "").strip()
            print(f"Searching for: {search_query}")

            search_results = webSearch(search_query, max_results=3)

            messages.append({
                "role": "assistant",
                "content": response_text
            })
            messages.append({
                "role": "user",
                "content": f"Here are the search results:\n\n{search_results}\n\nNow please write the note."
            })
        else:
            return response_text

    return response_text


def addToVault(note):
    try:
        title = next((line.split(':', 1)[1].strip()
                      for line in note.split('\n')
                      if line.startswith('title:')), None).lower().replace(" ", "_").replace("/", "")

        location = next((line.split(':', 1)[1].strip()
                         for line in note.split('\n')
                         if line.startswith('category:')), None).replace(" ", "_")
    except AttributeError:
        title = "note"
        location = "uncategorized"

    direc = "test_vault"
    path = f"{direc}/{location}"
    os.makedirs(path.lower(), exist_ok=True)

    try:
        with open(f"{path}/{title}.md", "w", encoding='utf-8') as f:
            f.write(note)
    except FileNotFoundError as e:
        return f"File not found error: {e}"


    print(f"wrote {path}/{title}.md", flush=True)
    

for i in range(5):
    note = makeNote(getQuestion())
    print(note)
    addToVault(note)

print("Making prompts")
generatePrompts()