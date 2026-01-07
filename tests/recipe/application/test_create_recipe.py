from unittest.mock import Mock

from sandpiper.recipe.application.create_recipe import (
    CreateRecipe,
    CreateRecipeRequest,
    IngredientRequest,
)
from sandpiper.recipe.domain.recipe import InsertedRecipe, Recipe
from sandpiper.recipe.domain.recipe_repository import RecipeRepository
from sandpiper.recipe.domain.shopping_repository import ShoppingRepository


class TestCreateRecipe:
    def setup_method(self):
        self.mock_recipe_repository = Mock(spec=RecipeRepository)
        self.mock_shopping_repository = Mock(spec=ShoppingRepository)
        self.create_recipe = CreateRecipe(
            recipe_repository=self.mock_recipe_repository,
            shopping_repository=self.mock_shopping_repository,
        )

    def test_create_recipe_basic(self):
        # Arrange
        self.mock_shopping_repository.find_or_create.side_effect = [
            "shopping-page-id-1",
            "shopping-page-id-2",
        ]
        self.mock_recipe_repository.save.return_value = InsertedRecipe(
            id="recipe-page-id",
            title="きな粉蒸しパン",
        )

        request = CreateRecipeRequest(
            title="きな粉蒸しパン",
            reference_url="https://example.com/recipe",
            ingredients=[
                IngredientRequest(name="絹豆腐", quantity="150g"),
                IngredientRequest(name="きな粉", quantity="50g"),
            ],
            steps=["混ぜる", "レンジで加熱する"],
        )

        # Act
        result = self.create_recipe.execute(request)

        # Assert
        assert result.id == "recipe-page-id"
        assert result.title == "きな粉蒸しパン"

        # Verify shopping repository was called for each ingredient
        assert self.mock_shopping_repository.find_or_create.call_count == 2
        self.mock_shopping_repository.find_or_create.assert_any_call("絹豆腐")
        self.mock_shopping_repository.find_or_create.assert_any_call("きな粉")

        # Verify recipe repository was called with correct arguments
        self.mock_recipe_repository.save.assert_called_once()
        saved_recipe = self.mock_recipe_repository.save.call_args[0][0]
        saved_ingredient_ids = self.mock_recipe_repository.save.call_args[0][1]

        assert isinstance(saved_recipe, Recipe)
        assert saved_recipe.title == "きな粉蒸しパン"
        assert saved_recipe.reference_url == "https://example.com/recipe"
        assert len(saved_recipe.ingredients) == 2
        assert len(saved_recipe.steps) == 2
        assert saved_ingredient_ids == ["shopping-page-id-1", "shopping-page-id-2"]

    def test_create_recipe_without_reference_url(self):
        # Arrange
        self.mock_shopping_repository.find_or_create.return_value = "shopping-page-id"
        self.mock_recipe_repository.save.return_value = InsertedRecipe(
            id="recipe-page-id",
            title="簡単レシピ",
        )

        request = CreateRecipeRequest(
            title="簡単レシピ",
            reference_url=None,
            ingredients=[IngredientRequest(name="卵", quantity="1個")],
            steps=["焼く"],
        )

        # Act
        result = self.create_recipe.execute(request)

        # Assert
        assert result.title == "簡単レシピ"
        saved_recipe = self.mock_recipe_repository.save.call_args[0][0]
        assert saved_recipe.reference_url is None

    def test_create_recipe_with_empty_ingredients(self):
        # Arrange
        self.mock_recipe_repository.save.return_value = InsertedRecipe(
            id="recipe-page-id",
            title="食材なしレシピ",
        )

        request = CreateRecipeRequest(
            title="食材なしレシピ",
            reference_url=None,
            ingredients=[],
            steps=["何かする"],
        )

        # Act
        result = self.create_recipe.execute(request)

        # Assert
        assert result.title == "食材なしレシピ"
        self.mock_shopping_repository.find_or_create.assert_not_called()
        saved_ingredient_ids = self.mock_recipe_repository.save.call_args[0][1]
        assert saved_ingredient_ids == []

    def test_create_recipe_with_many_steps(self):
        # Arrange
        self.mock_shopping_repository.find_or_create.return_value = "shopping-page-id"
        self.mock_recipe_repository.save.return_value = InsertedRecipe(
            id="recipe-page-id",
            title="複雑なレシピ",
        )

        steps = [
            "ボウルに絹豆腐を入れ、泡立て器でダマがなくなるまで滑らかに混ぜます。",
            "きな粉と砂糖を加え、粉っぽさがなくなるまでしっかりと混ぜ合わせます。",
            "卵を割り入れ、水（または豆乳・牛乳）を加えて生地を柔らかくします。",
            "ベーキングパウダーを加え、さっくりと混ぜ合わせます。",
            "クッキングシートを敷いた耐熱容器に生地を流し込み、ふんわりラップをかけます。",
            "500Wの電子レンジで約6分加熱します。",
            "真ん中に爪楊枝を刺して、ベタッとした生地がついてこなければ完成です。",
        ]

        request = CreateRecipeRequest(
            title="複雑なレシピ",
            reference_url="https://youtube.com/watch?v=xxx",
            ingredients=[IngredientRequest(name="食材A", quantity="適量")],
            steps=steps,
        )

        # Act
        result = self.create_recipe.execute(request)

        # Assert
        assert result.title == "複雑なレシピ"
        saved_recipe = self.mock_recipe_repository.save.call_args[0][0]
        assert len(saved_recipe.steps) == 7


class TestCreateRecipeRequest:
    def test_create_request(self):
        # Act
        request = CreateRecipeRequest(
            title="テストレシピ",
            reference_url="https://example.com",
            ingredients=[
                IngredientRequest(name="食材1", quantity="100g"),
            ],
            steps=["手順1"],
        )

        # Assert
        assert request.title == "テストレシピ"
        assert request.reference_url == "https://example.com"
        assert len(request.ingredients) == 1
        assert len(request.steps) == 1


class TestIngredientRequest:
    def test_create_ingredient_request(self):
        # Act
        ingredient = IngredientRequest(name="絹豆腐", quantity="150g")

        # Assert
        assert ingredient.name == "絹豆腐"
        assert ingredient.quantity == "150g"
