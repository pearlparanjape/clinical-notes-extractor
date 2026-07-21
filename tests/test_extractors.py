from src.extractor import extract_demographics, extract_symptoms, extract_blood_tests
from src.fake_client import FakeClient


def test_good_demographics():
    client = FakeClient('{"sex": "male", "age": 45}')
    result = extract_demographics("any note", client)
    assert result["status"] == "ok"
    assert result["data"]["age"] == 45


def test_demographics_bad_age_type():
    client = FakeClient('{"sex": "male", "age": "forty-five"}')
    result = extract_demographics("any note", client)
    assert result["status"] == "error"
    assert result["stage"] == "validation"


def test_demographics_garbage():
    client = FakeClient("this is not json at all")
    result = extract_demographics("any note", client)
    assert result["status"] == "error"
    assert result["stage"] == "json_parse"


def test_demographics_truncated_json():
    client = FakeClient('{"sex": "male", "age":')
    result = extract_demographics("any note", client)
    assert result["status"] == "error"
    assert result["stage"] == "json_parse"


def test_good_symptoms():
    client = FakeClient(
        '[{"name": "fever", "negated": false, "explicit": true, '
        '"onset_or_duration": null, "severity": null}]'
    )
    result = extract_symptoms("any note", client)
    assert result["status"] == "ok"


def test_empty_symptoms_is_valid():
    client = FakeClient("[]")
    result = extract_symptoms("any note", client)
    assert result["status"] == "ok"  # empty list = no symptoms, NOT an error


def test_good_lab_tests():
    client = FakeClient(
        '[{"test_name": "WBC", "sample_type": "blood", '
        '"result_type": "quantitative", "result": "14000 cell/uL"}]'
    )
    result = extract_blood_tests("any note", client)
    assert result["status"] == "ok"


def test_lab_test_bad_result_type_rejected():
    client = FakeClient(
        '[{"test_name": "WBC", "result_type": "numeric", "result": "5"}]'
    )
    result = extract_blood_tests("any note", client)
    assert result["status"] == "error"
    assert result["stage"] == "validation"


def test_fenced_json_is_stripped():
    client = FakeClient('```json\n{"sex": "male", "age": 45}\n```')
    result = extract_demographics("any note", client)
    assert result["status"] == "ok"
    assert result["data"]["age"] == 45


def test_symptoms_garbage():
    client = FakeClient("not json")
    result = extract_symptoms("any note", client)
    assert result["status"] == "error"
    assert result["stage"] == "json_parse"


def test_symptoms_bad_bool():
    client = FakeClient(
        '[{"name": "fever", "negated": "maybe", "explicit": true, '
        '"onset_or_duration": null, "severity": null}]'
    )
    result = extract_symptoms("any note", client)
    assert result["status"] == "error"
    assert result["stage"] == "validation"


def test_lab_tests_garbage():
    client = FakeClient("not json")
    result = extract_blood_tests("any note", client)
    assert result["status"] == "error"
    assert result["stage"] == "json_parse"
