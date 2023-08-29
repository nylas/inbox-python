from typing import List, Optional, TypeVar, Generic

T = TypeVar("T")


class ListResponse(tuple, Generic[T]):
    """
    List response object returned from the Nylas API.

    Attributes:
        data: The list of requested data objects.
        request_id: The request ID.
        next_cursor: The cursor to use to get the next page of data.
    """

    data: List[T]
    request_id: str
    next_cursor: Optional[str] = None

    def __new__(cls, data: List[T], request_id: str, next_cursor: Optional[str] = None):
        cls = tuple.__new__(cls, (data, request_id, next_cursor))
        cls.data = data
        cls.request_id = request_id
        cls.next_cursor = next_cursor
        return cls

    @classmethod
    def from_dict(cls, resp: dict, generic_type):
        converted_data = []
        for item in resp["data"]:
            converted_data.append(generic_type.from_dict(item))

        return cls(
            data=converted_data,
            request_id=resp["request_id"],
            next_cursor=resp.get("next_cursor", None),
        )
