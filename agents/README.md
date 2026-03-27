# System Narzędzi dla Agenta (Function Calling)

## Architektura

System narzędzi został zbudowany w oparciu o **wzorzec polimorfizmu** z klasą bazową `BaseTool`. Umożliwia to łatwe tworzenie nowych narzędzi przez dziedziczenie.

### Komponenty

1. **BaseTool** (`base_tool.py`) - abstrakcyjna klasa bazowa definiująca interfejs narzędzia
2. **ToolsRegistry** (`tools_registry.py`) - rejestr przechowujący i zarządzający narzędziami
3. **Agent** (`agent.py`) - agent AI wykorzystujący zarejestrowane narzędzia
4. **Narzędzia** (`tools/`) - konkretne implementacje narzędzi

## Tworzenie Nowego Narzędzia

### Krok 1: Dziedziczenie po BaseTool

```python
from vectorlib.agents.base_tool import BaseTool

class MojeNarzedzie(BaseTool):
    @property
    def name(self) -> str:
        return "nazwa_narzedzia"
    
    @property
    def description(self) -> str:
        return "Opis narzędzia dla modelu AI"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Opis parametru"
                }
            },
            "required": ["param1"]
        }
    
    def execute(self, param1, **kwargs) -> str:
        # Logika narzędzia
        return "Wynik działania"
```

### Krok 2: Rejestracja w Agencie

```python
from vectorlib.agents.agent import Agent
from vectorlib.agents.tools import MojeNarzedzie

agent = Agent()
narzedzie = MojeNarzedzie()
agent.register_tool(narzedzie)
```

## Przykład Użycia

```python
from vectorlib.agents.agent import Agent
from vectorlib.agents.tools import DownloadFromDictTool

# Stwórz agenta
agent = Agent()

# Zarejestruj narzędzie
download_tool = DownloadFromDictTool()
agent.register_tool(download_tool)

# Wyślij wiadomość
message = """
Pobierz dane dla ciepłomierzy z następującymi parametrami:
- Adres egeria: ['192.168.1.1']
- Węzeł: ['A1']
- Vector: ['V1']
Do folderu: 'output'
"""

response = agent.send_message(message)
agent.handle_response(response)
```

## Kompatybilność Wsteczna

System obsługuje również **stary format** narzędzi (funkcje zwracające tuple):

```python
# Stary format nadal działa
from vectorlib.datadownloader import from_excel_tool

agent.register_tool(from_excel_tool)  # Funkcja, nie instancja
```

## Dostępne Narzędzia

### DownloadFromDictTool
Pobiera dane z bazy danych na podstawie słownika Python.

### DownloadFromExcelTool
Pobiera dane z bazy danych na podstawie pliku Excel.

## Zalety Nowego Systemu

✅ **Polimorfizm** - łatwe tworzenie nowych narzędzi przez dziedziczenie  
✅ **Reużywalność** - jasny interfejs dla wszystkich narzędzi  
✅ **Czytelność** - kod narzędzia jest zorganizowany w klasie  
✅ **Kompatybilność** - obsługa zarówno nowego jak i starego formatu  
✅ **Typowanie** - lepsze wsparcie dla IDE i type checkerów
