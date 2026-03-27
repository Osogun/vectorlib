from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Klasa bazowa dla narzędzi używanych przez Agent.

    Każde narzędzie musi zdefiniować:
    - name: nazwa funkcji
    - description: opis funkcji
    - parameters: schemat parametrów (JSON Schema)
    - execute: logika wykonania funkcji
    """

    @property  # property pozwala używac funkjci jak atrybutu, np tool.name zamiast tool.name()
    @abstractmethod
    def name(self) -> str:
        """Nazwa narzędzia (używana w function calling)"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Opis narzędzia dla modelu AI"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """
        Schemat parametrów w formacie JSON Schema.

        Przykład:
        {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."},
                "param2": {"type": "integer", "description": "..."}
            },
            "required": ["param1"]
        }
        """
        pass

    @abstractmethod
    # args jest krotką argumentów nienazwanych, kwargs jest słownikiem argumentów nazwanych
    # operator * pozwala na wypakowanie krotki lub listy do pojedynczych argumentów, np func(*args) zamiast func(args[0], args[1], ...)
    # operator ** pozwala na wypakowanie słownika do argumentów nazwanych, np func(**kwargs) zamiast func(param1=kwargs['param1'], param2=kwargs['param2'])
    def execute(self, *args, **kwargs) -> str:
        """
        Wykonuje funkcję narzędzia.

        Args:
            **kwargs: Parametry przekazane z function call

        Returns:
            str: Wynik działania funkcji (przekazywany z powrotem do modelu)
        """
        pass

    def get_declaration(self) -> dict:
        """Zwraca deklarację narzędzia w formacie wymaganym przez GenAI"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
