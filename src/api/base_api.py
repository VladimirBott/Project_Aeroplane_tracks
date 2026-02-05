from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseAPI(ABC):
    """Базовый абстрактный класс для всех API клиентов."""

    @abstractmethod
    def _connect_to_api(self, url: str, params: Optional[Dict] = None,
                        headers: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Приватный метод для подключения к API."""
        pass

    @abstractmethod
    def get_data(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Абстрактный метод для получения данных."""
        pass