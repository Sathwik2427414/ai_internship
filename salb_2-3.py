import google.generativeai as genai
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import json
import datetime

load_dotenv()

GEMINI_API_KEY = os.getenv("API_KEY_GEMINI")

genai.configure(api_key=GEMINI_API_KEY)

GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_CX = os.getenv("GOOGLE_CSE_CX")
if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_CX:
    raise ValueError("Google Custom Search API keys (GOOGLE_CSE_API_KEY, GOOGLE_CSE_CX) not found in .env.")

search_service = build("customsearch", "v1", developerKey=GOOGLE_CSE_API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def Google Search_tool(query: str):
    try:
        res = search_service.cse().list(q=query, cx=GOOGLE_CSE_CX, num=5).execute()
        if 'items' in res:
            results = []
            for item in res['items']:
                results.append({
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'snippet': item.get('snippet')
                })
            return json.dumps(results)
        else:
            return json.dumps({"error": "No search results found."})
    except Exception as e:
        return json.dumps({"error": f"Google Search API error: {e}"})

tools = [
    {
        "name": "Google Search",
        "description": "Searches Google for real-time information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query."
                }
            },
            "required": ["query"]
        }
    }
]

def main():
    print("Welcome to the Gemini-powered Assistant!")
    print("Ask me anything (e.g., 'What's the weather in Mumbai?', 'Tell me about AI.', 'What is the current price of Bitcoin?').")
    print("Type 'exit' to quit.")

    while True:
        user_message = input("\nYou: ")
        if user_message.lower() == 'exit':
            print("Assistant: Goodbye!")
            break

        try:
            response = chat.send_message(
                user_message,
                tools=tools
            )

            if response.candidates and response.candidates[0].function_calls:
                function_call = response.candidates[0].function_calls[0]
                function_name = function_call.name
                function_args = function_call.args

                print(f"Assistant: (Calling tool: {function_name} with args: {function_args})")

                if function_name == "Google Search":
                    tool_output = Google Search_tool(function_args.get("query"))
                else:
                    tool_output = json.dumps({"error": f"Unknown tool: {function_name}"})

                final_response = chat.send_message(
                    genai.types.ToolCodeResponse(tool_code_results=[
                        genai.types.ToolCodeResult(
                            tool_name=function_name,
                            content=tool_output
                        )
                    ])
                )
                print(f"Assistant: {final_response.text}")

            else:
                print(f"Assistant: {response.text}")

        except Exception as e:
            print(f"Assistant: An error occurred: {e}")
            print("Please ensure your API keys are correct and you have internet connectivity.")

if __name__ == "__main__":
    main()