class ServerSentEvents:

    @classmethod
    def build_sse_data(
        cls, event: str, data: str, id: int, retry: int
    ) -> str:
        return f"event: {event}\ndata: {data}\nid: {id}\nretry: {retry}\n\n"
