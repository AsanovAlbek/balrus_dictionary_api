from dataclasses import dataclass

@dataclass
class SFTPConfig:
    host: str
    port: int
    username: str
    password: str