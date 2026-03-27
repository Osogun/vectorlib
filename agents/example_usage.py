# Przykład użycia narzędzi z klasą BaseTool

from vectorlib.agents.agent import Agent
from vectorlib.agents.tools import DownloadFromDictTool, DownloadFromExcelTool

# Stwórz agenta
agent = Agent()

# Zarejestruj narzędzia (nowy format - instancje BaseTool)
download_dict_tool = DownloadFromDictTool()
download_excel_tool = DownloadFromExcelTool()

agent.register_tool(download_dict_tool)
agent.register_tool(download_excel_tool)

# Przykład 1: Pobieranie danych ze słownika
print("=== Przykład 1: Pobieranie danych ze słownika ===")
message1 = """
Pobierz dane dla następujących ciepłomierzy do folderu 'output':
- Adres egeria: ['192.168.1.1', '192.168.1.2']
- Węzeł: ['A1', 'A2']
- Vector: ['V1', 'V2']
Zakres dat: od 2024-01-01 00:00:00 do 2024-12-31 23:59:59
"""

response1 = agent.send_message(message1)
agent.handle_response(response1)

# Przykład 2: Pobieranie danych z Excela
print("\n=== Przykład 2: Pobieranie danych z pliku Excel ===")
message2 = """
Pobierz dane z pliku 'input/cieplomierze.xlsx' do folderu 'output'.
Zakres dat: cały dostępny zakres (domyślny).
"""

response2 = agent.send_message(message2)
agent.handle_response(response2)
