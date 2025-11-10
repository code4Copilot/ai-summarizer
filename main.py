import os
import gradio as gr
from summarizer import Summarizer

# 建立 Summarizer 實例（會使用環境或 config 的 API key）
s = Summarizer()

def summarize_gradio(text: str, length: str) -> str:
    """
    呼叫 Summarizer 並回傳摘要或錯誤訊息（會顯示在同一個輸出框）。
    """
    if not text or not text.strip():
        return "Error: 請提供要摘要的文字。"

    try:
        resp = s.summarize(text, length=length, language="zh-tw")
        if resp.get("success"):
            return resp.get("summary", "")
        else:
            return f"Error: {resp.get('error', '未知錯誤')}"
    except Exception as e:
        return f"Error: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("## AI 文本摘要器")
    with gr.Row():
        inp = gr.Textbox(
            label="輸入文字（最多 5000 字元）",
            placeholder="在此貼上或輸入要摘要的文字...",
            lines=10,
            max_length=5000
        )
        out = gr.Textbox(
            label="摘要結果 / 錯誤訊息",
            lines=10,
            interactive=False
        )

    with gr.Row():
        length = gr.Radio(
            choices=["short", "medium", "long"],
            value="short",
            label="摘要長度"
        )
        btn = gr.Button("提交")

    # 範例輸入（會自動填入輸入框與長度選項）
    examples = [
        [
            "本專案的目標是建立一個簡單可用的 AI 文本摘要工具，能夠處理各種類型的文章並產生精簡摘要，方便使用者快速掌握重點。",
            "short"
        ],
        [
            "氣候變遷已經對全球生態系統造成明顯影響。本研究蒐集多年的觀測資料，分析溫度變化、降雨模式與物種分佈的變化，並提出可能的調適策略以減緩負面影響。",
            "medium"
        ]
    ]
    gr.Examples(examples=examples, inputs=[inp, length], label="範例輸入")

    btn.click(fn=summarize_gradio, inputs=[inp, length], outputs=out)

if __name__ == "__main__":
    # Allow containerized deployment to bind to 0.0.0.0 and pick port via env
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("GRADIO_SERVER_PORT", os.getenv("PORT", "7860")))
    # Optional: set share=True to create a public link (not recommended for production)
    demo.launch(server_name=server_name, server_port=server_port)