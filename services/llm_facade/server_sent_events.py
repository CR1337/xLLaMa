class ServerSentEvents:

    TEMPLATE: str = (
        "event: {event}\n"
        "data: {data}\n"
        "id: {id}\n"
        "retry: {retry}\n\n"
    )

    @classmethod
    def build_sse_data(
        cls, event: str, data: str, id_: str, retry: int
    ) -> str:
        return cls.TEMPLATE.format(
            event=event,
            data=data,
            id=id_,
            retry=retry
        )
