from dataclasses import dataclass


@dataclass
class CallNumbers:
    from_pin: str
    from_number: str
    request_number: str
    request_pin: str

    def __bool__(self) -> bool:
        return all((self.src, self.dst))

    @property
    def src(self) -> str:
        return self.from_pin or self.from_number

    @property
    def dst(self) -> str:
        return self.request_pin or self.request_number
