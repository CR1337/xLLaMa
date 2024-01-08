class ServerSentEvents:

    RETRY_PERIOD: int = 240000  # ms (4 minutes)

    @classmethod
    def build_sse_data(
        cls, event: str, data: str, id: int
    ) -> str:
        return (
            f"event: {event}\n"
            f"data: {data}\n"
            f"id: {id}\n"
            f"retry: {cls.RETRY_PERIOD}\n\n"
        )
