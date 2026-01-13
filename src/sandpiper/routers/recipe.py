"""レシピ管理API"""

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from sandpiper.app.app import SandPiperApp
from sandpiper.recipe.application.create_recipe import CreateRecipeRequest, IngredientRequest
from sandpiper.routers.dependency.deps import get_sandpiper_app

router = APIRouter(
    prefix="/recipe",
    tags=["recipe"],
)

# テンプレート設定
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/new", response_class=HTMLResponse)
async def recipe_form(request: Request) -> HTMLResponse:
    """レシピ登録フォームを表示する"""
    return templates.TemplateResponse("recipe_form.html", {"request": request})


class IngredientApiRequest(BaseModel):
    name: str
    quantity: str


class CreateRecipeApiRequest(BaseModel):
    title: str
    reference_url: str | None = None
    ingredients: list[IngredientApiRequest]
    steps: list[str]


@router.post("")
async def create_recipe(
    request: CreateRecipeApiRequest,
    sandpiper_app: SandPiperApp = Depends(get_sandpiper_app),
) -> JSONResponse:
    """レシピを作成する

    Args:
        request: レシピ作成リクエスト
        sandpiper_app: SandPiper アプリケーション

    Returns:
        JSONResponse: 作成されたレシピの情報
    """
    create_request = CreateRecipeRequest(
        title=request.title,
        reference_url=request.reference_url,
        ingredients=[IngredientRequest(name=ing.name, quantity=ing.quantity) for ing in request.ingredients],
        steps=request.steps,
    )
    inserted_recipe = sandpiper_app.create_recipe.execute(create_request)
    return JSONResponse(
        content={
            "id": inserted_recipe.id,
            "title": inserted_recipe.title,
        }
    )
