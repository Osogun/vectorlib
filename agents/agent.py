from google import genai
from google.genai import types
from .api_key import API_KEY
from .tools_registry import ToolsRegistry


class Agent:
    def __init__(self, model="gemini-3-flash-preview", config=None):
        self.client = genai.Client(api_key=API_KEY)
        self.model = model
        if config is None:
            config = types.GenerateContentConfig(
                temperature=0.2,
            )
        else:
            config = types.GenerateContentConfig(**config)
        self.tools_registry = ToolsRegistry()
        self.config = config
        self.contents = []

    def send_message(self, message):
        self.contents.append(
            types.Content(role="user", parts=[types.Part(text=message)])
        )
        response = self.client.models.generate_content(
            model=self.model, contents=self.contents, config=self.config
        )
        return response

    def handle_response(self, response):
        self.contents.append(response.candidates[0].content)
        if response.candidates[0].content.parts[0].function_call:
            try:
                tool_call = response.candidates[0].content.parts[0].function_call
                tool_response = self.tools_registry.execute(tool_call)
                self.contents.append(
                    types.Content(
                        role="function",
                        parts=[tool_response],
                    )
                )
                final_response = self.client.models.generate_content(
                    model=self.model, contents=self.contents, config=self.config
                )
                self.contents.append(final_response.candidates[0].content)
                print(final_response.text)
            except ValueError as e:
                print(str(e))
        else:
            print(response.text)

    def register_tool(self, tool):
        """Rejestruje narzędzie (BaseTool)"""
        self.tools_registry.register_tool(tool)
        # Aktualizuje konfiguracje agenta
        tool_declarations = self.tools_registry.get_tool_declarations()
        if tool_declarations:
            tools = types.Tool(function_declarations=tool_declarations)
            # Zachowaj obecne ustawienia config i dodaj tools
            config_dict = {
                "temperature": (
                    self.config.temperature
                    if hasattr(self.config, "temperature")
                    else 0.2
                ),
                "tools": [tools],
            }
            self.config = types.GenerateContentConfig(**config_dict)
