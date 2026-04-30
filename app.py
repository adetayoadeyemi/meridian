import gradio as gr
import asyncio
from agent import run_agent


def run_async(coro):
    return asyncio.run(coro)


def chat(user_input, history):
    history = history or []

    response = run_async(run_agent(user_input, history))
    reply = response if isinstance(response, str) else (str(response) if response is not None else "")

    history = list(history)
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})

    return history, history


with gr.Blocks() as demo:
    gr.Markdown("Meridian Support Assistant")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Ask about products, orders...")

    state = gr.State([])

    msg.submit(chat, [msg, state], [chatbot, state]).then(
        lambda: "", None, msg
    )

demo.launch()