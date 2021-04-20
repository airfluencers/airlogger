
class AirTraceIdRequired(Exception):

    def __init__(self) -> None:
        self.http_response = "x-air-trace-id must be present in header"
        super().__init__("Trace id must be existent in context.")


class InvalidArgsType(Exception):
    def __init__(self) -> None:
        super().__init__("Log args must be a dict with")


class InvalidHookResult(Exception):
    def __init__(self) -> None:
        super().__init__("Request hook log result must be a serializable dict")