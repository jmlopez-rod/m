from m.core import Bad, Good
from m.pydantic import load_model, parse_model
from pydantic import BaseModel


class PydanticTestModel(BaseModel):
    """A test model."""

    int_prop: int
    str_prop: str
    list_int_prop: list[int]


def test_pydantic_parse_model() -> None:
    """Test pydantic parse_model."""
    py_obj = {
        'int_prop': 1,
        'str_prop': 'a',
        'list_int_prop': [1, 2, 3],
    }
    model_res_a = parse_model(PydanticTestModel, py_obj)
    assert isinstance(model_res_a, Good)
    model_a = model_res_a.value
    assert model_a.int_prop == 1
    assert model_a.str_prop == 'a'
    assert model_a.list_int_prop == [1, 2, 3]

    model_res_b = parse_model(list[PydanticTestModel], [py_obj])
    assert isinstance(model_res_b, Good)
    first_model = model_res_b.value[0]
    assert first_model.int_prop == 1

    model_res_c = parse_model(list[PydanticTestModel], {'oops': 'bad data'})
    assert isinstance(model_res_c, Bad)
    error_text = str(model_res_c.value)
    assert 'parse_model_failure' in error_text
    assert '1 validation error for list[PydanticTestModel]' in error_text


def test_pydantic_load_model() -> None:
    """Test pydantic load_model."""
    model_res_a = load_model(PydanticTestModel, 'oop_not_here.yaml')
    assert isinstance(model_res_a, Bad)
    error_text = str(model_res_a.value)
    assert 'pydantic.load_model_failure' in error_text
    assert 'file does not exist' in error_text
    assert 'oop_not_here.yaml' in error_text

    file_name = 'packages/python/tests/_fixtures/pydantic_test_model.yaml'
    model_res_b = load_model(PydanticTestModel, file_name)
    assert isinstance(model_res_b, Good)
    model = model_res_b.value
    assert model.int_prop == 1
    assert model.str_prop == 'a'
    assert model.list_int_prop == [1, 2, 3]

    file_name = 'packages/python/tests/_fixtures/pydantic_test_model_list.yaml'
    model_res_c = load_model(list[PydanticTestModel], file_name)
    assert isinstance(model_res_c, Good)
    first_model = model_res_c.value[0]
    assert first_model.int_prop == 1
