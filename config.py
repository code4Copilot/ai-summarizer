# AI文本摘要工具的設定檔
# 在此程式載入環境變數並且定義OpenAI常數
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API設定: API_KEY和Model_NAME 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
# 文本摘要器設定:MAX_INPUT_LENGTH, 和SuMMARY_LENGTHS值有短,  中, 長三種選項     
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 4000))
SUMMARY_LENGTHS = {
    "short": int(os.getenv("SUMMARY_LENGTH_SHORT", 100)),
    "medium": int(os.getenv("SUMMARY_LENGTH_MEDIUM", 300)),
    "long": int(os.getenv("SUMMARY_LENGTH_LONG", 600)),
}
# Gradio設定：GRADIO_SHARE和GRADIO_SERVER_PORT 
GRADIO_SHARE = os.getenv("GRADIO_SHARE", "False") == "True"
GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", 7860))
# 驗證OPENAPI_API_KEY是否存在: 建立validate_config()函式檢查API_KEY是否存在
# 若不存在則引發錯誤訊息, 存在回傳True
def validate_config():
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY未設定。請在環境變數中提供有效的API金鑰。")
    return True
