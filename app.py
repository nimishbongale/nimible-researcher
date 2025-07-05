import chainlit as cl
from together import Together
import os
from chainlit.input_widget import Select, Switch, Slider
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_together import ChatTogether

llm_exaone_32b = ChatTogether(
    max_retries=1,
    api_key=os.getenv('TOGETHER_API_KEY') or "",
    model="lgai/exaone-3-5-32b-instruct",
    max_tokens=2048,
    streaming=True,
)

SINGLE_GENERATOR_PROMPT = """
You're an experienced researcher named Nimible. Your goal is to perform a deep research & provide a succinct answer to <user input>. 
Always mention citations or sources of information you used to generate your answer.
Your response should be in markdown format, with proper headings and structure. Avoid LaTeX or other complex formatting.
"""

client = Together(api_key=os.getenv('TOGETHER_API_KEY') or "d69f5296633534623211c714c634026e6bb294269629a9b1ac82caebed30015d")
wikipedia = WikipediaAPIWrapper(top_k_results=5, doc_content_chars_max=5000)
memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=50)
prompt = PromptTemplate(
    template="""You're an experienced researcher named Nimible. Your goal is to perform a deep & thorough research. 
Always mention citations or sources of information you used to generate your answer at the very end. Be as verbose as possible.
Don't admit a mistake or say that you don't know something, just try to answer the question as best as you can.

Current Plan: {input}

Conversation History: {chat_history}

If the tool response is not enough, use your own knowledge to supplement it.
""",
    input_variables=["input", "chat_history"],
)

plan_prompt = PromptTemplate(
    input_variables=["input", "chat_history"],
    template="""Prepare plan for task execution. (e.g. retrieve current date to find weather forecast)

    Tools which can be used: article_search_tool (Article Search). Refrain from using this for general queries.

    Ask yourself if you need to use the article search tool or not. For most cases, you may not need it.
    You have no other tools at your disposal. If you don't need to use any tools, just pass the input as a result.

    Current Question: {input}

    Conversation History: {chat_history}

    Output look like this:
    '''
        Question: {input}

        Execution plan: [execution_plan]

        Rest of needed information: [rest_of_needed_information]
    '''

    IMPORTANT: if there is no question, or plan is not need (YOU HAVE TO DECIDE!), just populate {input} (pass it as a result). Then output should look like this:
    '''
        input: {input}
    '''
    """,
)

plan_chain = ConversationChain(
    llm=llm_exaone_32b,
    memory=memory,
    input_key="input",
    prompt=plan_prompt,
    output_key="output",
)

@cl.step(type="tool")
def article_search_tool(tool_input: str):
    return wikipedia.run(tool_input)

article_search_tool = Tool(
    name="Article Search",
    func=article_search_tool,
    description="A tool STRICTLY to be used sparingly. Find wikipedia articles about topics which you have no knowledge about. Use very precise questions.",
)

# Initialize Agent
agent = initialize_agent(
    type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    tools=[article_search_tool],
    llm=llm_exaone_32b,
    # verbose=True, # verbose option is for printing logs (only for development)
    max_iterations=5,
    prompt=prompt,
    memory=memory,
    handle_parsing_errors=True,
)

@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    return [
        cl.ChatProfile(
            name="User",
            icon="https://fastly.picsum.photos/id/24/4855/1803.jpg?hmac=ICVhP1pUXDLXaTkgwDJinSUS59UWalMxf4SOIWb9Ui4",
            markdown_description="## Nimible Researcher V3",
            starters=[
            cl.Starter(
                label="Explain superconductors",
                message="Explain superconductors like I'm five years old.",
                # icon="/public/learn.svg",
                ),
            cl.Starter(
                label="Python script for daily email reports",
                message="Write a script to automate sending daily email reports in Python",
                # icon="/public/terminal.svg",
                ),
            cl.Starter(
                label="Text inviting friend to wedding",
                message="Write a text asking a friend to be my plus-one at a wedding next month. I want to keep it super short and casual, and offer an out.",
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

@cl.step()
async def Thinking():
    return "Thinking"

@cl.on_chat_start
async def start():
    await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="OpenAI - Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
                initial_index=0,
            ),
            Switch(id="Streaming", label="OpenAI - Stream Tokens", initial=True),
            Slider(
                id="Temperature",
                label="OpenAI - Temperature",
                initial=1,
                min=0,
                max=2,
                step=0.1,
            ),
            Slider(
                id="SAI_Steps",
                label="Stability AI - Steps",
                initial=30,
                min=10,
                max=150,
                step=1,
                description="Amount of inference steps performed on image generation.",
            ),
            Slider(
                id="SAI_Cfg_Scale",
                label="Stability AI - Cfg_Scale",
                initial=7,
                min=1,
                max=35,
                step=0.1,
                description="Influences how strongly your generation is guided to match your prompt.",
            ),
            Slider(
                id="SAI_Width",
                label="Stability AI - Image Width",
                initial=512,
                min=256,
                max=2048,
                step=64,
                tooltip="Measured in pixels",
            ),
            Slider(
                id="SAI_Height",
                label="Stability AI - Image Height",
                initial=512,
                min=256,
                max=2048,
                step=64,
                tooltip="Measured in pixels",
            ),
        ]
    ).send()


@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)

@cl.on_message
async def main(message: cl.Message):
    try:
        await Thinking()
        plan_result = plan_chain.run(message.content)
        # Agent execution
        res = agent(str(plan_result))
        # Send message
        msg2 = cl.Message(content=res['output'], author="Nimible Researcher V3 Bot")
        await msg2.send()
    except Exception as e:
        pass

    # response = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": SINGLE_GENERATOR_PROMPT
    #         },
    #         *cl.chat_context.to_openai(),
    #         {
    #             "role": "user",
    #             "content": message.content
    #         }
    #     ],
    #     model="lgai/exaone-deep-32b",
    #     max_tokens=18000,
    #     stream=True
    # )

    # msg = cl.Message(content="", author="Nimible Researcher V3 Bot")
    # for chunk in response:
    #     await msg.stream_token(chunk.choices[0].delta.content) 
    # await msg.send()