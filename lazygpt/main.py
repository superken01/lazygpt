import chainlit as cl


@cl.on_chat_start
def start_chat():
    pass


@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=message.content).send()
