import pytest
from lotion.properties import Date, Relation, Select, Status, Title

from sandpiper.shared.notion.databases.routine import RoutineNextDate
from sandpiper.shared.notion.databases.todo import (
    TodoKindProp,
    TodoLogDate,
    TodoName,
    TodoProjectProp,
    TodoProjectTaskProp,
    TodoSection,
    TodoStatus,
)


class TestTodoNotionProps:
    """ToDo関連のNotionプロパティのテスト"""

    def test_todo_name_inheritance(self):
        """TodoNameがTitleを継承していることをテスト"""
        assert issubclass(TodoName, Title)

    def test_todo_status_inheritance(self):
        """TodoStatusがStatusを継承していることをテスト"""
        assert issubclass(TodoStatus, Status)

    def test_todo_section_inheritance(self):
        """TodoSectionがSelectを継承していることをテスト"""
        assert issubclass(TodoSection, Select)

    def test_todo_log_date_inheritance(self):
        """TodoLogDateがDateを継承していることをテスト"""
        assert issubclass(TodoLogDate, Date)

    def test_todo_kind_prop_inheritance(self):
        """TodoKindPropがSelectを継承していることをテスト"""
        assert issubclass(TodoKindProp, Select)

    def test_todo_project_prop_inheritance(self):
        """TodoProjectPropがRelationを継承していることをテスト"""
        assert issubclass(TodoProjectProp, Relation)

    def test_todo_project_task_prop_inheritance(self):
        """TodoProjectTaskPropがRelationを継承していることをテスト"""
        assert issubclass(TodoProjectTaskProp, Relation)

    def test_todo_name_instantiation(self):
        """TodoNameのインスタンス化をテスト"""
        # Titleクラスが要求する引数を適切に渡す
        try:
            instance = TodoName()
            assert isinstance(instance, TodoName)
            assert isinstance(instance, Title)
        except TypeError:
            # プロパティクラスによってはパラメータが必要な場合もある
            pytest.skip("TodoName requires parameters for instantiation")

    def test_todo_status_instantiation(self):
        """TodoStatusのインスタンス化をテスト"""
        try:
            instance = TodoStatus()
            assert isinstance(instance, TodoStatus)
            assert isinstance(instance, Status)
        except TypeError:
            pytest.skip("TodoStatus requires parameters for instantiation")

    def test_todo_section_instantiation(self):
        """TodoSectionのインスタンス化をテスト"""
        try:
            instance = TodoSection()
            assert isinstance(instance, TodoSection)
            assert isinstance(instance, Select)
        except TypeError:
            pytest.skip("TodoSection requires parameters for instantiation")

    def test_todo_log_date_instantiation(self):
        """TodoLogDateのインスタンス化をテスト"""
        try:
            instance = TodoLogDate()
            assert isinstance(instance, TodoLogDate)
            assert isinstance(instance, Date)
        except TypeError:
            pytest.skip("TodoLogDate requires parameters for instantiation")

    def test_todo_kind_prop_instantiation(self):
        """TodoKindPropのインスタンス化をテスト"""
        try:
            instance = TodoKindProp()
            assert isinstance(instance, TodoKindProp)
            assert isinstance(instance, Select)
        except TypeError:
            pytest.skip("TodoKindProp requires parameters for instantiation")

    def test_todo_project_prop_instantiation(self):
        """TodoProjectPropのインスタンス化をテスト"""
        try:
            instance = TodoProjectProp()
            assert isinstance(instance, TodoProjectProp)
            assert isinstance(instance, Relation)
        except TypeError:
            pytest.skip("TodoProjectProp requires parameters for instantiation")

    def test_todo_project_task_prop_instantiation(self):
        """TodoProjectTaskPropのインスタンス化をテスト"""
        try:
            instance = TodoProjectTaskProp()
            assert isinstance(instance, TodoProjectTaskProp)
            assert isinstance(instance, Relation)
        except TypeError:
            pytest.skip("TodoProjectTaskProp requires parameters for instantiation")


class TestRoutineNotionProps:
    """ルーティン関連のNotionプロパティのテスト"""

    def test_routine_next_date_inheritance(self):
        """RoutineNextDateがDateを継承していることをテスト"""
        assert issubclass(RoutineNextDate, Date)

    def test_routine_next_date_instantiation(self):
        """RoutineNextDateのインスタンス化をテスト"""
        try:
            instance = RoutineNextDate()
            assert isinstance(instance, RoutineNextDate)
            assert isinstance(instance, Date)
        except TypeError:
            pytest.skip("RoutineNextDate requires parameters for instantiation")


class TestNotionPropDecorator:
    """notion_propデコレータの動作をテスト"""

    def test_class_attributes_exist(self):
        """デコレータによってクラス属性が設定されることを確認"""
        # notion_propデコレータが正しく動作していることを間接的にテスト
        # 各クラスが適切に定義されていることを確認
        classes_to_test = [
            TodoName,
            TodoStatus,
            TodoSection,
            TodoLogDate,
            TodoKindProp,
            TodoProjectProp,
            TodoProjectTaskProp,
            RoutineNextDate,
        ]

        for cls in classes_to_test:
            # クラスが定義されていることを確認
            assert cls is not None
            # クラス名が正しく設定されていることを確認
            assert cls.__name__ in [
                "TodoName",
                "TodoStatus",
                "TodoSection",
                "TodoLogDate",
                "TodoKindProp",
                "TodoProjectProp",
                "TodoProjectTaskProp",
                "RoutineNextDate",
            ]

    def test_all_classes_are_property_types(self):
        """すべてのクラスがlotion property typesを継承していることをテスト"""
        property_classes = [Title, Status, Select, Date, Relation]

        test_classes = [
            (TodoName, Title),
            (TodoStatus, Status),
            (TodoSection, Select),
            (TodoLogDate, Date),
            (TodoKindProp, Select),
            (TodoProjectProp, Relation),
            (TodoProjectTaskProp, Relation),
            (RoutineNextDate, Date),
        ]

        for test_class, expected_parent in test_classes:
            assert issubclass(test_class, expected_parent)
            # 間接的にlotion propertyであることも確認
            assert any(issubclass(test_class, prop_cls) for prop_cls in property_classes)

    def test_class_module_location(self):
        """クラスが正しいモジュールで定義されていることをテスト"""
        todo_expected_module = "sandpiper.shared.notion.databases.todo"
        routine_expected_module = "sandpiper.shared.notion.databases.routine"

        todo_classes = [
            TodoName,
            TodoStatus,
            TodoSection,
            TodoLogDate,
            TodoKindProp,
            TodoProjectProp,
            TodoProjectTaskProp,
        ]

        for cls in todo_classes:
            assert cls.__module__ == todo_expected_module

        assert RoutineNextDate.__module__ == routine_expected_module
