from sandpiper.recipe.domain.recipe import Ingredient, InsertedRecipe, Recipe


class TestIngredient:
    def test_create_ingredient(self):
        # Act
        ingredient = Ingredient(name="絹豆腐", quantity="150g")

        # Assert
        assert ingredient.name == "絹豆腐"
        assert ingredient.quantity == "150g"

    def test_create_ingredient_with_complex_quantity(self):
        # Act
        ingredient = Ingredient(
            name="水（または豆乳・牛乳）",
            quantity="20ml（大さじ1と1/3）",
        )

        # Assert
        assert ingredient.name == "水（または豆乳・牛乳）"
        assert ingredient.quantity == "20ml（大さじ1と1/3）"


class TestRecipe:
    def test_create_recipe(self):
        # Arrange
        ingredients = [
            Ingredient(name="絹豆腐", quantity="150g"),
            Ingredient(name="きな粉（無糖）", quantity="50g"),
        ]
        steps = [
            "ボウルに絹豆腐を入れ、泡立て器でダマがなくなるまで滑らかに混ぜます。",
            "きな粉と砂糖を加え、粉っぽさがなくなるまでしっかりと混ぜ合わせます。",
        ]

        # Act
        recipe = Recipe(
            title="きな粉蒸しパン（豆腐バージョン）",
            reference_url="https://example.com/recipe",
            ingredients=ingredients,
            steps=steps,
        )

        # Assert
        assert recipe.title == "きな粉蒸しパン（豆腐バージョン）"
        assert recipe.reference_url == "https://example.com/recipe"
        assert len(recipe.ingredients) == 2
        assert len(recipe.steps) == 2

    def test_create_recipe_without_reference_url(self):
        # Act
        recipe = Recipe(
            title="簡単レシピ",
            reference_url=None,
            ingredients=[],
            steps=["混ぜる", "焼く"],
        )

        # Assert
        assert recipe.title == "簡単レシピ"
        assert recipe.reference_url is None
        assert len(recipe.ingredients) == 0
        assert len(recipe.steps) == 2


class TestInsertedRecipe:
    def test_create_inserted_recipe(self):
        # Act
        inserted_recipe = InsertedRecipe(
            id="notion-page-id-123",
            title="きな粉蒸しパン",
        )

        # Assert
        assert inserted_recipe.id == "notion-page-id-123"
        assert inserted_recipe.title == "きな粉蒸しパン"
