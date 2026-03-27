from ..base_tool import BaseTool
from ...datadownloader import DataDownloader


class DownloadFromExcelTool(BaseTool):
    """Narzędzie do pobierania danych z bazy danych na podstawie pliku Excel"""

    @property
    def name(self) -> str:
        return "download_from_excel"

    @property
    def description(self) -> str:
        return (
            "Pobiera dane z bazy danych dla ciepłomierzy zadeklarowanych w pliku Excel. "
            "Plik musi zawierać kolumny: 'Adres egeria', 'Węzeł', 'Vector'. "
            "Funkcja przyjmuje ścieżkę do pliku Excel, ścieżkę do folderu docelowego oraz opcjonalnie "
            "zakres dat do pobrania danych. Domyślny zakres dat to od 2023-01-01 do 2025-12-31."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "excel_path": {
                    "type": "string",
                    "description": "Ścieżka do pliku Excel",
                },
                "vector_folder": {
                    "type": "string",
                    "description": "Ścieżka do folderu docelowego",
                },
                "start_range": {
                    "type": "string",
                    "description": "Opcjonalny początek zakresu dat w formacie YYYY-MM-DD HH:MM:SS",
                },
                "end_range": {
                    "type": "string",
                    "description": "Opcjonalny koniec zakresu dat w formacie YYYY-MM-DD HH:MM:SS",
                },
            },
            "required": ["excel_path", "vector_folder"],
        }

    def execute(
        self, excel_path, vector_folder, start_range=None, end_range=None
    ) -> str:
        """
        Wykonuje pobieranie danych z bazy danych na podstawie pliku Excel.

        Args:
            excel_path: Ścieżka do pliku Excel
            vector_folder: Ścieżka do folderu docelowego
            start_range: Początek zakresu dat (opcjonalnie)
            end_range: Koniec zakresu dat (opcjonalnie)

        Returns:
            str: Komunikat o wyniku operacji
        """
        if start_range is None:
            start_range = DataDownloader.DEFAULT_START_RANGE
        if end_range is None:
            end_range = DataDownloader.DEFAULT_END_RANGE

        try:
            DataDownloader.from_excel(
                excel_path, vector_folder, start_range=start_range, end_range=end_range
            )
            return f"Data downloaded successfully to {vector_folder}."
        except Exception as e:
            return f"Failed to download data: {str(e)}"
