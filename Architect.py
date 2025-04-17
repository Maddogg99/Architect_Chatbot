import openai
from flask import Flask, request, jsonify
import re
import json
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)


from openai import OpenAI
import json 
import re

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="",
)


# Chat with GPT function
def chat_with_gpt(prompt):
  response = client.chat.completions.create(
      extra_body={},
      model="deepseek/deepseek-r1-distill-llama-70b:free",
      messages=[
          {
            "role": "system",
            "content": (
                "You are a software architecture assistant. Given a system scenario, your job is to return:\n\n"
                "A JSON object with exactly these two fields:\n"
                "1. `Architecture` — valid Mermaid `graph TD` code representing the architecture.\n"
                "2. `explanation` — a concise description (max 50 words) of the chosen architecture style and patterns, and why they fit the scenario. \n"
                                    "Examples of architecture styles: Client-Server, Microservices, Event-Driven, Layered, Peer-to-Peer, etc.\n"
                                    "Examples of patterns: Message Queue, Pub/Sub, Load Balancer, Circuit Breaker, etc.\n\n"
                "### Mermaid Diagram Rules (Strict):\n"
                "- Start with: `graph TD`\n"
                "- Nodes must have **unique IDs**.\n"
                "- Labels inside square brackets `[]` must **always** be wrapped in **double quotes** (`\"Label Text\"`).\n"
                "- Labels containing special characters like parentheses `()`, square brackets `[]`, or slashes `/` must also be wrapped in **double quotes** (`\"Label Text\"`).\n"
                "- Do **not** use `/`, `()`, `[]`, or special characters like `-`, `+`, or `:` inside node **IDs** (they’re allowed in **labels only**).\n"
                "- Use `-->` for arrows. If adding a label, use `-->|Label|`, **not** `-->|Label|>` (extra `>` causes errors).\n"
                "- All open/close brackets must match.\n"
                "- No Markdown, code blocks, or extra text outside the JSON object.\n"
                "- Example of an invalid line that causes a parse error:\n"
                "  `Client[\"Client\"] -->|Websocket|> LoadBalancer[\"Load Balancer\"]`\n"
                "  This fails due to the **`>`** after the label — remove it to fix the error.\n"
                "- "
                "### Example Output:\n"
                '{\n'
                '  "Architecture": "graph TD\\n  Client[\"Web/Mobile Client\"] -->|Websocket| LoadBalancer[\"Load Balancer\"]\\n  LoadBalancer --> Backend[\"Backend Server\"]\\n  Backend -->|Messages|> MessageQueue[\"Message Queue (e.g., RabbitMQ)\"]",\n'
                '  "explanation": "This architecture uses the client-server style with a single backend entry point. It suits real-time communication scenarios with predictable request/response behavior, centralizing logic for easier maintenance and consistent data handling."\n'
                '}\n'
            )
          },
          {
              "role": "user",
              "content": prompt
          }
      ]
  )


  try:
    match = re.search(r'{.*}', response.choices[0].message.content, re.DOTALL)
    if match:
      json_str = match.group(0) # Extract the JSON string try:
      parsed_json = json.loads(json_str) # Convert string to JSON object
      print('\n')
      print(parsed_json.get('Architecture')) # Output the JSON object
      print('\n')
      print(parsed_json.get('explanation')) # Output the JSON object
      print("##########################")
      return parsed_json
  except json.JSONDecodeError as e:
    print(" JSON Decode Error:", e)
    return json.loads('{"Architecture": "", "explanation": ""}')





# Endpoint to call chat_with_gpt
@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Get user input from the request
        user_message = request.json.get("message")
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Call the chat_with_gpt function
        response = chat_with_gpt(user_message)

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
