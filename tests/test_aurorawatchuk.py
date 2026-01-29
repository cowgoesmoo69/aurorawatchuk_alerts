from app.aurorawatchuk import get_status_ids, process_status_ids
import pytest


@pytest.fixture
def mock_awuk_request(mocker):
    """Fixture to mock AuroraWatchUK API XML responses."""

    def _mock(xml):
        class MockXMLResponse:
            def __init__(self, content):
                self.content = content

            def raise_for_status(self):
                pass

        return mocker.patch(
            "app.aurorawatchuk.requests.get",
            return_value=MockXMLResponse(xml),
        )

    return _mock


# get_status_ids() tests.
# Class to return mock XML responses via requests.get()
def test_get_status_ids_junk_xml(mock_awuk_request):
    mock_awuk_request(
        b"""
        moo
        """
    )
    result = get_status_ids(reduced_sensitivity=False)
    assert result == None


# Normal sensitivity test. Only alerting=true site should be returned.
def test_get_status_ids_normal(mock_awuk_request):
    mock_awuk_request(
        b"""
        <current_status api_version="0.2.5">
          <updated>
            <datetime>2026-01-01T00:00:00+0000</datetime>
          </updated>
        <site_status project_id="project:SAMNET" site_id="site:SAMNET:CRK2" site_url="http://aurorawatch-api.lancs.ac.uk/0.2.5/project/samnet/crk2.xml" status_id="red"/>
        <site_status alerting="true" project_id="project:AWN" site_id="site:AWN:SUM" site_url="http://aurorawatch-api.lancs.ac.uk/0.2.5/project/awn/sum.xml" status_id="green"/>
    </current_status>
    """
    )
    result = get_status_ids(reduced_sensitivity=False)
    assert len(result) == 1
    assert result[0]["status_id"] == "green"


# Reduced sensitivity test. All sites shoud be returned.
def test_get_status_ids_reduced(mock_awuk_request):
    mock_awuk_request(
        b"""
        <current_status api_version="0.2.5">
          <updated>
            <datetime>2026-01-01T00:00:00+0000</datetime>
          </updated>
        <site_status project_id="project:SAMNET" site_id="site:SAMNET:CRK2" site_url="http://aurorawatch-api.lancs.ac.uk/0.2.5/project/samnet/crk2.xml" status_id="red"/>
        <site_status alerting="true" project_id="project:AWN" site_id="site:AWN:SUM" site_url="http://aurorawatch-api.lancs.ac.uk/0.2.5/project/awn/sum.xml" status_id="green"/>
        <site_status project_id="project:COW" site_id="site:COW:MOO" site_url="abcdefghijklmnopqrstuvwxyz" status_id="brown"/>
    </current_status>
    """
    )
    result = get_status_ids(reduced_sensitivity=True)
    assert len(result) > 1
    assert result[0]["status_id"] == "red"
    assert result[1]["status_id"] == "green"
    assert result[2]["status_id"] == "brown"


# process_status_ids() tests.
# Invalid status ID tests.
def test_process_status_ids_unrecognised():
    # Single invalid.
    status_ids = [
        {"status_id": "purple"},
    ]
    assert process_status_ids(status_ids) == None
    # Multiple invalid.
    status_ids = [
        {"status_id": "purple"},
        {"status_id": "grey"},
        {"status_id": "blue"},
    ]
    assert process_status_ids(status_ids) == None
    # Mixture of valid and invalid.
    status_ids = [
        {"status_id": "purple"},
        {"status_id": "amber"},
        {"status_id": "blue"},
    ]
    assert process_status_ids(status_ids) == 2


# Rank combination tests.
def test_process_status_ids_ranks():
    # Single status tests.
    status_ids = [
        {"status_id": "green"},
    ]
    assert process_status_ids(status_ids) == 0
    status_ids = [
        {"status_id": "yellow"},
    ]
    assert process_status_ids(status_ids) == 1
    status_ids = [
        {"status_id": "amber"},
    ]
    assert process_status_ids(status_ids) == 2
    status_ids = [
        {"status_id": "red"},
    ]
    assert process_status_ids(status_ids) == 3
    # Multi status tests.
    status_ids = [
        {"status_id": "green"},
        {"status_id": "green"},
    ]
    assert process_status_ids(status_ids) == 0
    status_ids = [
        {"status_id": "green"},
        {"status_id": "yellow"},
    ]
    assert process_status_ids(status_ids) == 0
    status_ids = [
        {"status_id": "green"},
        {"status_id": "amber"},
    ]
    assert process_status_ids(status_ids) == 0
    status_ids = [
        {"status_id": "green"},
        {"status_id": "red"},
    ]
    assert process_status_ids(status_ids) == 0
    status_ids = [
        {"status_id": "yellow"},
        {"status_id": "green"},
    ]
    assert process_status_ids(status_ids) == 0
    status_ids = [
        {"status_id": "yellow"},
        {"status_id": "yellow"},
    ]
    assert process_status_ids(status_ids) == 1
    status_ids = [
        {"status_id": "yellow"},
        {"status_id": "amber"},
    ]
    assert process_status_ids(status_ids) == 1
    status_ids = [
        {"status_id": "yellow"},
        {"status_id": "red"},
    ]
    assert process_status_ids(status_ids) == 1
    status_ids = [
        {"status_id": "amber"},
        {"status_id": "green"},
    ]
    assert process_status_ids(status_ids) == 0
    status_ids = [
        {"status_id": "amber"},
        {"status_id": "yellow"},
    ]
    assert process_status_ids(status_ids) == 1
    status_ids = [
        {"status_id": "amber"},
        {"status_id": "amber"},
    ]
    assert process_status_ids(status_ids) == 2
    status_ids = [
        {"status_id": "amber"},
        {"status_id": "red"},
    ]
    assert process_status_ids(status_ids) == 2
    status_ids = [
        {"status_id": "red"},
        {"status_id": "green"},
    ]
    assert process_status_ids(status_ids) == 0
    status_ids = [
        {"status_id": "red"},
        {"status_id": "yellow"},
    ]
    assert process_status_ids(status_ids) == 1
    status_ids = [
        {"status_id": "red"},
        {"status_id": "amber"},
    ]
    assert process_status_ids(status_ids) == 2
    status_ids = [
        {"status_id": "red"},
        {"status_id": "red"},
    ]
    assert process_status_ids(status_ids) == 3
