
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import dotenv
dotenv.load_dotenv()
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')








system_template = """Tu es un expert du droit ohada et tu es francophone.
Utilisez les éléments de contexte suivants pour répondre à la question de l'utilisateur.
Si vous ne connaissez pas la réponse, contentez-vous de dire que vous ne savez pas, ne cherchez pas à inventer une réponse.
Incluez TOUJOURS une section "SOURCES" dans votre réponse!.
La section "SOURCES" doit être une référence à la source du document à partir de laquelle vous avez obtenu votre réponse.

Exemple de votre réponse en Français:



```
FINAL ANSWER: This Agreement is governed by English law.
SOURCES: 28-pl
```

commence!
----------------
{summaries}"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)
chain_type_kwargs = {"prompt": prompt}
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
