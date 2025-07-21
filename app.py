import chainlit as cl
from together import Together
import os
from chainlit.input_widget import Select, Switch, Slider
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_together import ChatTogether

API_KEY = os.getenv('TOGETHER_API_KEY') or ""

llm_exaone_32b = ChatTogether(
    api_key=API_KEY,
    model="lgai/exaone-3-5-32b-instruct",
    max_tokens=16000,
    temperature=0
)

client = Together(api_key=API_KEY)

wikipedia = WikipediaAPIWrapper(top_k_results=10, doc_content_chars_max=10000)
# memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=50)

@cl.step(type="tool")
def article_search_tool(tool_input: str):
    # how to show it searched wikipedia articles in the chat?
    return wikipedia.run(tool_input)

article_search_tool = Tool(
    name="Article Search",
    func=article_search_tool,
    description="Finds wikipedia articles related to the user's query.",
)

retriever_agent = initialize_agent(
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    llm=llm_exaone_32b,
    # verbose=True, # verbose option is for printing logs (only for development)
    max_iterations=5,
    max_execution_time=60,
    tools=[article_search_tool],
    prompt= "You are a smart retriever. You almost always use the Article Search tool provided to you to answer the user's question. Supplement your answer with your own knowledge as well. If you don't need to use the tool, just answer based on your own knowledge.",
)

@cl.on_chat_resume
async def on_chat_resume(thread):
    pass

@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    return [
        cl.ChatProfile(
            name="User",
            icon="https://cdn-icons-png.flaticon.com/512/2620/2620404.png",
            markdown_description="## Nimible Researcher V4",
            starters=[
            # Need more detailing
            cl.Starter(
                label="Ruy Lopez Opening",
                message="What is the Ruy Lopez opening in chess? Explain it in detail & prepare a step by step guide for beginners.",
                icon="https://cdn-icons-png.flaticon.com/512/7697/7697554.png",
                ),
            cl.Starter(
                label="Python script for daily email reports",
                message="Write a script to automate sending daily email reports in Python",
                icon="https://cdn-icons-png.flaticon.com/512/3098/3098090.png",
                ),
            cl.Starter(
                label="Vacation Planning",
                message="Plan a 7-day vacation to Japan, including flights, hotels, and activities.",
                icon="https://cdn-icons-png.flaticon.com/512/10963/10963675.png",
                )
            ],
        )
    ]

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    pass

@cl.on_audio_end
async def on_audio_end():
    pass

@cl.step(type="tool")
async def planning(msg: str):
    return f"Planning to respond to: {msg} \n1. Framing 2. Retrieving 3. Quality Enhancing 4. Critiquing 5. Answering"

@cl.step(type="tool")
async def quality_enhancer_tool(msg: str):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert bot. You will be provided with an answer & user input. Your task is to analyze it in the context of the user input and provide the best version of it possible. Ensure to provide and preserve citations & source links."
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        max_tokens=4096,
        stream=True,
        temperature=0,
    )
    # response.choices[0].message.content
    msg = cl.Message(content="", author="Nimible Researcher V4 Bot")
    for chunk in response:
        await msg.stream_token(chunk.choices[0].delta.content) 
    await msg.send()
    return msg.content

@cl.step(type="tool")
async def critique_answer_tool(msg: str):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert critic. Your task is to critique the answer in detail, find mistakes or missing information. From your own knowledge recommend improvements, add additional sources or citations and include them in your critique. Ensure to provide and preserve citations & source links."
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        model="lgai/exaone-deep-32b",
        max_tokens=16000,
        stream=True,
        temperature=0,
    )
    msg = cl.Message(content="", author="Nimible Researcher V4 Bot")
    for chunk in response:
        await msg.stream_token(chunk.choices[0].delta.content) 
    await msg.send()
    return msg.content

@cl.step(type="tool")
async def technical_writer_answer_tool(msg: str):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert technical writer. Your task is to present a detailed & verbose FINAL answer to the user's question, ensuring clarity and precision. Use markdown formatting for headings, bullet points, and code blocks where necessary. Ensure to provide and preserve citations. Do NOT mention anything about revisions, corrections, criticism or improvements in the answer WHATSOEVER. Just present the FINAL answer with detailed citations & source links. ONLY & ONLY the FINAL answer is expected. Do NOT mention anything about the previous steps or the process of arriving at this answer. Do NOT mention anything about the user input or the critique points. Just present the FINAL answer with detailed citations & source links.",
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        model="lgai/exaone-3-5-32b-instruct",
        max_tokens=16000,
        stream=True,
        temperature=0,
    )
    # response.choices[0].message.content
    msg = cl.Message(content="", author="Nimible Researcher V4 Bot")
    for chunk in response:
        await msg.stream_token(chunk.choices[0].delta.content) 
    await msg.send()
    return msg.content

@cl.step(type="tool")
async def rewrite_query_tool(msg: str):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert rephraser. Your task is to simply provide a better version of the user's input and structure it in a clear, crisp, precise & succinct manner. STRICTLY do NOT provide an answer whatsoever. If the input is already clear, just return it as is. You always revert in much fewer words than the input. You also convert questions into statements. For casual inputs such as hello hi etc. just respond with 'Hello! What topic do you want to research on?'.",
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        max_tokens=4096,
        stream=True,
        temperature=0,
    )
    # response.choices[0].message.content
    msg = cl.Message(content="", author="Nimible Researcher V4 Bot")
    for chunk in response:
        await msg.stream_token(chunk.choices[0].delta.content) 
    await msg.send()
    return msg.content

# @cl.action_callback("action_button")
# async def on_action(action):
#     await cl.Message(content=f"Executed {action.name}").send()
#     # Optionally remove the action button from the chatbot user interface
#     await action.remove()

# @cl.on_chat_start
# async def start():
#     # Sending an action button within a chatbot message
#     actions = [
#         cl.Action(name="action_button", payload={"value": "example_value"}, label="Click me!")
#     ]

#     await cl.Message(content="Interact with this action button:", actions=actions).send()

@cl.on_chat_start
async def start():
    await cl.ChatSettings(
        [
            # Select(
            #     id="Model",
            #     label="OpenAI - Model",
            #     values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
            #     initial_index=0,
            # ),
            Switch(id="Dummy", label="Dummy", initial=True),
            # Slider(
            #     id="Temperature",
            #     label="OpenAI - Temperature",
            #     initial=1,
            #     min=0,
            #     max=2,
            #     step=0.1,
            # ),
            # Slider(
            #     id="SAI_Steps",
            #     label="Stability AI - Steps",
            #     initial=30,
            #     min=10,
            #     max=150,
            #     step=1,
            #     description="Amount of inference steps performed on image generation.",
            # ),
            # Slider(
            #     id="SAI_Cfg_Scale",
            #     label="Stability AI - Cfg_Scale",
            #     initial=7,
            #     min=1,
            #     max=35,
            #     step=0.1,
            #     description="Influences how strongly your generation is guided to match your prompt.",
            # ),
            # Slider(
            #     id="SAI_Width",
            #     label="Stability AI - Image Width",
            #     initial=512,
            #     min=256,
            #     max=2048,
            #     step=64,
            #     tooltip="Measured in pixels",
            # ),
            # Slider(
            #     id="SAI_Height",
            #     label="Stability AI - Image Height",
            #     initial=512,
            #     min=256,
            #     max=2048,
            #     step=64,
            #     tooltip="Measured in pixels",
            # ),
        ]
    ).send()


@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)

@cl.on_message
async def main(message: cl.Message):
    rewritten_query, res, quality_answer, critique_answer='','','',''
    try:
        async with cl.Step(name="Planning Agent", type="llm") as step0:
            step0.output = "Plan: \n1. Framing \n2. Retrieving \n3. Quality Enhancing \n4. Critiquing \n5. Answering"
        async with cl.Step(name="Rewriter Agent", type="llm") as step00:
            step00.output = "Running Rewriter Agent"
            rewritten_query = await rewrite_query_tool(message.content)
            step00.output = "Rewriter Agent Finished"
            step00.output = "Retreiver Agent may take a while, please be patient..."
        msg3 = cl.Message(content=rewritten_query, author="Nimible Researcher V4 Bot")
        await msg3.send()
        if rewritten_query != "Hello! What topic do you want to research on?" and len(rewritten_query) > 0:
            async with cl.Step(name="Retriever Agent", type="llm") as step02:
                step02.output = "Running Retriever Agent"
                res = retriever_agent(rewritten_query)
                step02.output = "Retriever Agent Finished"
        else:
            return
        async with cl.Step(name="Quality Check Agent", type="llm") as step:
            step.output = "Running Quality Check Agent"
            quality_answer = await quality_enhancer_tool("user input: " + rewritten_query + "\nanswer: " + res['output'])
            step.output = "Quality Check Agent Finished"
        async with cl.Step(name="Critic Agent", type="llm") as step1:
            step1.output = "Running Critic Agent"
            critique_answer = await critique_answer_tool(quality_answer)
            step1.output = "Critic Agent Finished"
        async with cl.Step(name="Writer Agent", type="llm") as step8:
            step8.output = "Running Writer Agent"
            pass
        final_answer = await technical_writer_answer_tool("original user input: " + message.content + "\ncritique points: " + critique_answer)
    except Exception as e:
        pass