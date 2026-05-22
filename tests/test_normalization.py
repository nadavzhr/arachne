from arachne.models.schema import EmploymentType, ExperienceLevel
from arachne.utils.normalization import normalize_record


def test_normalize_record_maps_shared_schema_fields() -> None:
    job = normalize_record(
        "test",
        None,
        {
            "title": "Backend Engineer",
            "url": "https://example.com/jobs/1",
            "locations": [{"name": "Tel Aviv"}, {"name": "Remote"}],
            "isRemote": "false",
            "jobType": "Full-Time",
            "level": "new college graduate",
        },
    )

    assert job.location == "Tel Aviv, Remote"
    assert job.remote is False
    assert job.employment_type == EmploymentType.FULL_TIME
    assert job.experience_level == ExperienceLevel.ENTRY
