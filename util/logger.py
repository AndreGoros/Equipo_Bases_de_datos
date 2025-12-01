import logging
from colorlog import ColoredFormatter
from typing import Optional

# Definición de colores ANSI para la consola
RESET = "\033[0m"
GRAY = "\033[90m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
WHITE = "\033[97m"

# Formato del log: Hora | Nivel | Nombre del Logger | Mensaje
LOG_FORMAT = (
    f"{RESET}{GRAY}%(asctime)s.%(msecs)03d{RESET} | "
    f"%(log_color)s%(levelname)-8s{RESET} | "
    f"{CYAN}%(name)s{RESET} | "
    f"{WHITE}%(message)s{RESET}"
)

class LoggerSessionManager:

    _instance: Optional["LoggerSessionManager"] = None

    def __new__(cls, *args, **kwargs):
        # Patrón Singleton para asegurar una única configuración compartida
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name: str = "app", log_level: int = logging.INFO):
        # Evita re-inicializar si ya fue creado
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.log_level = log_level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.propagate = False

        # Configuración del formateador con colores
        console_format = ColoredFormatter(
            fmt=LOG_FORMAT,
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            reset=True,
            style="%",
        )

        # --- Console Handler ---
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(log_level)
        self.console_handler.setFormatter(console_format)

        # --- Adjuntar handler si no existe ---
        if not self.logger.handlers:
            self.logger.addHandler(self.console_handler)

        # --- Interceptar loggers de librerías (SQLAlchemy, Uvicorn, FastAPI) ---
        # Esto unifica el estilo de todos los logs en la consola
        for framework_logger in [
            "uvicorn",
            "uvicorn.error",
            "uvicorn.access",
            "fastapi",
            "starlette",
            "sqlalchemy.engine", # Muestra las queries SQL
            # "sqlalchemy.pool", # Descomentar para ver conexiones del pool
            # "sqlalchemy.orm",
        ]:
            framework_logger_inst = logging.getLogger(framework_logger)
            framework_logger_inst.handlers.clear()
            framework_logger_inst.addHandler(self.console_handler)
            framework_logger_inst.setLevel(self.log_level)
            framework_logger_inst.propagate = False

        self._initialized = True

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Retorna el logger principal o un hijo con el nombre especificado.
        Ej: get_logger(__name__)
        """
        if name:
            return self.logger.getChild(name)
        return self.logger