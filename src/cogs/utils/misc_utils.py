from typing import Union, Dict
from math import ceil


async def paginator(lst: list, page: int) -> Dict[str, Union[int, str]]:
    """
    Divides content into 10 element pages

    Parameters
    -----------
    lst: A list of strings
    page: The page

    Returns
    -----------
    dict: A dictionay containing content and metadata
        {
            pagecount: int
            page: int
            page_content: str
        }
    """

    pagecount = ceil(len(lst) / 10)

    if not page or page <= 0 or page > pagecount:
        page = 1

    start_index = (page - 1) * 10
    end_index = page * 10

    page_content = lst[start_index:end_index]

    page_data = {
        'pagecount': pagecount,
        'page': page,
        'page_content': page_content
    }
    return page_data
