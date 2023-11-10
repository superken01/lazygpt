import chainlit as cl
from agent import create_agent


@cl.on_chat_start
def start_chat():
    pass


@cl.on_message
async def main(message: cl.Message):
    agent = cl.user_session.get("agent")
    if agent is None:
        agent = create_agent(
            system_message="盡量使用function完成任務 儘量使用中文回答",
            streaming=True,
            verbose=True,
        )
        cl.user_session.set("agent", agent)

    callback = cl.LangchainCallbackHandler(stream_final_answer=True)
    result = await cl.make_async(agent)(
        {"input": message.content}, callbacks=[callback]
    )
    await cl.Message(content=result["output"]).send()
