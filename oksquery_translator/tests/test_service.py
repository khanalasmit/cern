import pytest

from oksquery_translator.service import OksQueryService, ServiceInputError


class FakeSchemaRetriever:
    def environment_probe(self):
        return {
            "oks_dump": "/usr/bin/oks_dump",
            "config_module": "available",
            "schema_dir": "/schema",
            "oks_dump_status": "OK",
            "class_count": 2,
            "classes": ["Application", "Computer"],
        }


class FakePipeline:
    def __init__(self):
        self.schema_retriever = FakeSchemaRetriever()
        self.calls = []

    def answer(self, question, version=None, interpret=True):
        self.calls.append(("answer", question, version, interpret))
        return {
            "status": "success",
            "answer": "",
            "target_class": "Computer",
            "oks_query": '(all (object-id "" !=))',
            "result_count": 3,
            "results": [
                {"id": "host-1", "attributes": {}},
                {"id": "host-2", "attributes": {}},
                {"id": "host-3", "attributes": {}},
            ],
            "attempts": 1,
            "version": version or "current",
            "version_used": version or "current",
        }

    def translate_only(self, question, version=None):
        self.calls.append(("translate", question, version))
        return {
            "status": "success",
            "target_class": "Computer",
            "oks_query": '(all (object-id "" !=))',
            "attempts": 1,
        }


class EmptyResultPipeline(FakePipeline):
    def answer(self, question, version=None, interpret=True):
        self.calls.append(("answer", question, version, interpret))
        return {
            "status": "success",
            "answer": "",
            "target_class": "Application",
            "oks_query": '(all ("Name" "rc_trigger_1" =))',
            "result_count": 0,
            "results": [],
            "attempts": 1,
            "version": version or "current",
            "version_used": version or "current",
        }


def test_query_is_stateless_and_skips_interpreter():
    pipeline = FakePipeline()
    service = OksQueryService(pipeline=pipeline, max_results=2)

    result = service.query("List all computers.")

    assert result["status"] == "success"
    assert result["result_count"] == 3
    assert len(result["results"]) == 2
    assert result["warnings"]
    assert pipeline.calls == [("answer", "List all computers.", None, False)]


def test_translate_does_not_execute():
    pipeline = FakePipeline()
    service = OksQueryService(pipeline=pipeline)

    result = service.translate("List all computers.", version="tdaq-14-00-00")

    assert result["status"] == "success"
    assert result["results"] == []
    assert pipeline.calls == [("translate", "List all computers.", "tdaq-14-00-00")]


def test_empty_success_result_is_explicit_and_not_a_server_error():
    result = OksQueryService(pipeline=EmptyResultPipeline()).query(
        "Which applications are named rc_trigger_1?"
    )

    assert result["status"] == "success"
    assert result["result_count"] == 0
    assert "matched no objects" in result["message"]
    assert any("do not retry" in warning for warning in result["warnings"])


@pytest.mark.parametrize("question", ["", "   ", None])
def test_question_validation(question):
    service = OksQueryService(pipeline=FakePipeline())
    with pytest.raises(ServiceInputError):
        service.query(question)


def test_version_validation_rejects_paths_and_unknown_forms():
    service = OksQueryService(pipeline=FakePipeline())
    for version in ("../../etc/passwd", "hash:/tmp/repo", "not-a-version"):
        with pytest.raises(ServiceInputError):
            service.query("List computers", version=version)


@pytest.mark.parametrize(
    "version",
    ["hash:abc123", "date:2024-03-15", "tag:r123@ATLAS", "tdaq-14-00-00", "run:123", "r123"],
)
def test_version_validation_accepts_supported_selectors(version):
    service = OksQueryService(pipeline=FakePipeline())
    service.translate("List computers", version=version)


def test_environment_probe_is_non_secret():
    result = OksQueryService(pipeline=FakePipeline()).environment_probe()
    assert result["status"] == "success"
    assert result["class_count"] == 2
