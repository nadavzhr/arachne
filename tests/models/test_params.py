from arachne.models.schema import EmploymentType, ExperienceLevel, JobSearchCriteria
from arachne.sources.amazon.params import AmazonParams
from arachne.sources.apple.params import AppleParams
from arachne.sources.google.params import GoogleParams
from arachne.sources.meta.params import MetaParams
from arachne.sources.microsoft.params import MicrosoftParams
from arachne.sources.nvidia.params import NvidiaParams


def test_shared_search_maps_to_microsoft_query() -> None:
    search = JobSearchCriteria(
        title="platform engineer",
        locations=["Tel Aviv, Israel"],
        remote=True,
        experience_levels=[ExperienceLevel.ENTRY, ExperienceLevel.MID],
    )

    query = MicrosoftParams.from_search(search).to_query()

    assert query["query"] == "platform engineer"
    assert query["location"] == "Tel Aviv, Israel"
    assert query["filter_include_remote"] == "1"
    assert query["filter_seniority"] == ["Entry", "Mid-Level"]


def test_shared_search_maps_to_provider_specific_vocabulary() -> None:
    search = JobSearchCriteria(
        title="software engineer",
        locations=["Israel"],
        employment_types=[EmploymentType.FULL_TIME],
        experience_levels=[ExperienceLevel.ENTRY, ExperienceLevel.MID],
    )

    assert NvidiaParams.from_search(search).to_query()["filter_job_type"] == [
        "new college graduate",
        "regular employee",
    ]
    assert AmazonParams.from_search(search).to_query()["normalized_country_code[]"] == ["ISR"]
    assert GoogleParams.from_search(search).to_query()["target_level"] == ["EARLY", "MID"]
    assert AppleParams.from_search(search).to_query()["location"] == ["israel-ISR"]
    assert MetaParams.from_search(search).to_search_input()["offices"] == ["Israel"]
