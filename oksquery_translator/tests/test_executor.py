"""Regression tests for structured OKS result extraction."""

from types import SimpleNamespace
import sys

from oksquery_translator.executor import ExecutionResult, Executor


def test_parse_oks_dump_preserves_numeric_attribute_values():
    output = '''\
Found 1 matching query "(all (\"Memory\" \"500\" >))" in class "Computer":
Object "localhost@Computer"
  Memory: 1024
  CPU: 1100
  NumberOfCores: 1
  RLogin: "ssh"
'''

    objects = Executor._parse_oks_dump_output(output, "Computer")

    assert objects == [{
        "id": "localhost",
        "class": "Computer",
        "attributes": {
            "Memory": "1024",
            "CPU": "1100",
            "NumberOfCores": "1",
            "RLogin": '"ssh"',
        },
    }]


def test_config_backend_fills_proxy_attribute_values_from_native_output(monkeypatch):
    class FakeObject:
        def __init__(self, object_id):
            self._object_id = object_id

        def UID(self):
            return self._object_id

    class FakeDB:
        def attributes(self, target_class):
            assert target_class == "Computer"
            return {"Memory": object(), "CPU": object()}

        def get_objs(self, target_class, query):
            assert target_class == "Computer"
            assert query == '(all ("Memory" "500" >))'
            return [FakeObject("localhost")]

    class FakeConfiguration:
        def __new__(cls, connection):
            assert connection.endswith("computers.data.xml")
            return FakeDB()

    monkeypatch.setitem(
        sys.modules,
        "config",
        SimpleNamespace(Configuration=FakeConfiguration),
    )

    executor = Executor(data_file="computers.data.xml")
    native_result = ExecutionResult(
        success=True,
        objects=[{
            "id": "localhost",
            "class": "Computer",
            "attributes": {"Memory": "1024", "CPU": "1100"},
        }],
        count=1,
    )
    calls = []

    def fake_native(*args, **kwargs):
        calls.append((args, kwargs))
        return native_result

    monkeypatch.setattr(executor, "_execute_oks_dump", fake_native)

    result = executor._execute_config(
        "Computer",
        '(all ("Memory" "500" >))',
        max_objects=200,
        version_label="current",
        data_file="computers.data.xml",
        oks_dump_path="/usr/bin/oks_dump",
    )

    assert result.success
    assert result.count == 1
    assert result.objects[0]["attributes"] == {"Memory": "1024", "CPU": "1100"}
    assert calls
