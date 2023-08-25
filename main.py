from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
import chainlit as cl
import PyPDF2
from io import BytesIO
from config import *

@cl.on_chat_start
async def init():
    all_texts=[]
    metadatas=[]
    texts=[]
    files = None
    embeddings = OpenAIEmbeddings()
    await cl.Message(
            content=f"Bienvenue !.\n Je m'appele JOE DAN et je suis votre assistant juridique !",
        ).send()
    while files == None:
                files = await cl.AskFileMessage(
                    content="Veuillez télécharger un fichier texte ou PDF pour commencer !", 
                    accept=["text/plain", "application/pdf"],max_files=10,max_size_mb=100
                ).send()

    msg = cl.Message(content=f"Processing ...",author="System Administrator")
    await msg.send()
    for file in files:
        if file.name.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(BytesIO(file.content))
            text = ""
            for page_num in range( len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num] .extract_text()
            all_texts.append({"name": file.name, "text": text})
        else:
            text = file.content.decode("utf-8")
            all_texts.append({"name": file.name, "text": text})

        for text_info in all_texts:
                chunks = text_splitter.split_text(text_info["text"])
        for idx, chunk in enumerate(chunks):
                texts.append(chunk)
                metadatas.append({"source": f"{text_info['name']}_{idx}"})

        docsearch = await cl.make_async(Chroma.from_texts)(
                texts, embeddings, metadatas=metadatas,            )
            # Create a chain that uses the Chroma vector store
        chain = RetrievalQAWithSourcesChain.from_chain_type(
                ChatOpenAI(temperature=0, streaming=True),
                chain_type="stuff",
                retriever=docsearch.as_retriever(),
                chain_type_kwargs=chain_type_kwargs
            )

            # Save the metadata and texts in the user session
        cl.user_session.set("metadatas", metadatas)
        cl.user_session.set("texts", texts)
        msg.content = "Traitement de  terminé. Vous pouvez maintenant poser des questions !"
        await msg.update()
        cl.user_session.set("chain", chain)


@cl.on_message
async def main(message):

    chain = cl.user_session.get("chain")  # type: RetrievalQAWithSourcesChain
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True
    res = await chain.acall(message, callbacks=[cb])
    answer = res["answer"]
    sources = res["sources"].strip()
    source_elements = []

    # Get the metadata and texts from the user session
    metadatas = cl.user_session.get("metadatas")
    all_sources_ = [m["source"] for m in metadatas]
    texts = cl.user_session.get("texts")
    if sources:
        found_sources = []

        # Add the sources to the message
        for source in sources.split(","):
            source_name = source.strip().replace(".", "")
          

            # Get the index of the source
            try:
                index = all_sources_.index(source_name)
                print("index")
            except ValueError:
                index = all_sources_.index(source)
                continue
            text = texts[index]
            found_sources.append(source_name)
            # Create the text element referenced in the message
            source_elements.append(cl.Text(content=text, name=source_name))

        if found_sources:
            answer += f"\nSources: {', '.join(found_sources)}"
        else:
            answer += "\nPas de sources"
    print(source_elements)
    if cb.has_streamed_final_answer:
        cb.final_stream.elements = source_elements
        await cb.final_stream.update()
    else:
        await cl.Message(content=answer, elements=source_elements).send()



