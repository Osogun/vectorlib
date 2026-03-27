from google import genai
from google.genai import types
from .api_key import API_KEY
from .base_tool import BaseTool


class ToolsRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, tool):
        """
        Rejestruje narzędzie w rejestrze.

        Obsługuje dwa formaty:
        1. Funkcja zwracająca (func, declaration) - stary format
        2. Instancja BaseTool - nowy format
        """
        if isinstance(tool, BaseTool):
            # Nowy format: instancja BaseTool
            self.tools[tool.name] = {
                "declaration": tool.get_declaration(),
                "func": tool.execute,
            }
        else:
            # Stary format: funkcja zwracająca tuple
            func, tool_declaration = tool()
            self.tools[tool_declaration["name"]] = {
                "declaration": tool_declaration,
                "func": func,
            }

    def get_tool_declarations(self):
        """Zwraca listę deklaracji wszystkich zarejestrowanych narzędzi"""
        return [tool_data["declaration"] for tool_data in self.tools.values()]

    def execute(self, tool_call):
        tool_name = tool_call.name
        if tool_name in self.tools:
            func = self.tools[tool_name]["func"]
            args = tool_call.args
            result = func(**args)
            tool_response = types.Part.from_function_response(
                name=tool_name, response={"result": result}
            )
            return tool_response
        else:
            raise ValueError(f"Tool {tool_name} not found in registry.")
