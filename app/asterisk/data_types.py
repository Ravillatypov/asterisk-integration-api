from dataclasses import dataclass


@dataclass
class CallNumbers:
    from_pin: str
    from_number: str
    request_number: str
    request_pin: str

    def __bool__(self) -> bool:
        num1, num2 = self.src, self.dst
        min_length = min(len(num1), len(num2))
        min_length = 10 if min_length > 10 else min_length
        return all((num1, num2, min_length, num1[-min_length:] != num2[-min_length:]))

    @property
    def src(self) -> str:
        return self.from_pin or self.from_number

    @property
    def dst(self) -> str:
        return self.request_pin or self.request_number
