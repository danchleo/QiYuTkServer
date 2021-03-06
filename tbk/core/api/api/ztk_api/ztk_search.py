from typing import Optional, List

from fastapi import Depends, Body
from pydantic import BaseModel
from pydantic import Field
from structlog.stdlib import BoundLogger
from ztk_api import ZTK, SearchArgs, SearchModel

from core.logger import get_logger
from core.resp.base import ResponseModel, ApiResp
from core.vendor.ztk import get_ztk_api_v2
from ...api import fields
from ...api.app import app
from ...api_utils import api_inner_wrapper


class SearchResponseModel(ResponseModel):
    data: Optional[List[SearchModel]] = Field(None, title="详细数据")


class SearchForm(BaseModel):
    """
    全网搜索
    """

    q: str = Field(..., title="商品标题")

    page: int = fields.page_field
    page_size: int = fields.page_size_field
    sort: str = fields.sort_fields

    youquan: Optional[int] = Field(None, title="是否有券", description="1 为有券，其它值为全部商品")

    def to_data(self) -> SearchArgs:
        return SearchArgs.from_dict(self.dict())


@app.post(
    "/ztk/search",
    tags=["折淘客"],
    summary="全网商品搜索",
    description="",
    response_model=SearchResponseModel,
)
async def ztk_search(
    f: SearchForm = Body(..., title="请求参数"),
    logger: BoundLogger = Depends(get_logger),
    ztk: ZTK = Depends(get_ztk_api_v2),
):
    @api_inner_wrapper(logger)
    async def inner():
        data = f.to_data()
        j = await ztk.search(data)
        return ApiResp.from_data(j.content).to_dict()

    return await inner
