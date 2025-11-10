import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.anyio


async def test_get_jobs(async_client: AsyncClient):
    response = await async_client.get("/jobs/")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert isinstance(payload["items"], list)
    assert "total" in payload
    assert "page" in payload and payload["page"] == 1
    assert "page_size" in payload


async def test_get_job_descriptions(async_client: AsyncClient):
    """Test getting job descriptions for recruiters."""
    response = await async_client.get("/jobs/descriptions")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert isinstance(payload["items"], list)
    assert "total" in payload
    assert "page" in payload and payload["page"] == 1
    assert "page_size" in payload

    # Check that curated jobs are returned
    for job in payload["items"]:
        assert job.get("is_curated") is True
        # Check that required fields are present
        assert "id" in job
        assert "title" in job
        assert "company" in job
        # Description should be present (either original or from jd_content)
        assert "description" in job or job.get("jd_content")


async def test_get_job_descriptions_with_missing_descriptions(async_client: AsyncClient):
    """Test that jobs with jd_content but no description get description populated."""
    # This test ensures the fix for populating description from jd_content works
    from app.services.job_service import list_job_descriptions

    # Mock the database to return a job with jd_content but no description
    mock_job = {
        "_id": "test_id",
        "title": "Test Job",
        "company": "Test Company",
        "jd_content": "This is a long job description content that should be truncated to 500 characters for the description field when no description is present.",
        "is_curated": True,
        "code": "REQ-TEST",
        "uploaded_at": "2025-01-01T00:00:00Z"
    }

    with patch("app.services.job_service.db.jobs.find") as mock_find, \
         patch("app.services.job_service.db.jobs.count_documents", return_value=1) as mock_count:

        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [mock_job]
        mock_find.return_value = mock_cursor

        result = await list_job_descriptions(page=1, page_size=10)

        assert len(result["items"]) == 1
        job = result["items"][0]
        assert "description" in job
        assert job["description"] == mock_job["jd_content"][:500]  # Should be truncated to 500 chars


async def test_job_search_filtering(async_client: AsyncClient):
    """Test job search functionality with various filters."""
    # Test search by title
    response = await async_client.get("/jobs/?search=engineer")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload

    # Test with pagination
    response = await async_client.get("/jobs/?page=1&page_size=5")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) <= 5
    assert payload["page"] == 1
    assert payload["page_size"] == 5


async def test_job_upload_and_retrieval():
    """Test uploading a job and retrieving it via job descriptions endpoint."""
    from app.services.job_service import upload_job_description, list_job_descriptions
    from app.core.database import db
    import io

    # Create test PDF content
    test_content = b"Test job description content"
    test_filename = "test_job.pdf"

    # Mock the file extraction
    with patch("app.services.job_service._extract_text_from_file", return_value="Extracted job description text"):
        job_id = await upload_job_description(
            recruiter_id="test_recruiter",
            title="Test Uploaded Job",
            file_bytes=test_content,
            content_type="application/pdf",
            original_filename=test_filename,
            company="Test Company",
            budget="$100k",
            job_brief="Brief description",
        )

        assert job_id

        # Verify the job was created
        job = await db.jobs.find_one({"_id": job_id})
        assert job
        assert job["title"] == "Test Uploaded Job"
        assert job["company"] == "Test Company"
        assert job["is_curated"] is True
        assert "jd_content" in job
        assert job["jd_content"] == "Extracted job description text"

        # Test that it appears in job descriptions list
        result = await list_job_descriptions(page=1, page_size=50)
        job_ids = [j["id"] for j in result["items"]]
        assert job_id in job_ids

        # Find the job in results and check description is populated
        job_in_list = next(j for j in result["items"] if j["id"] == job_id)
        assert "description" in job_in_list
        assert job_in_list["description"] == "Extracted job description text"

        # Clean up
        await db.jobs.delete_one({"_id": job_id})


async def test_job_description_pagination(async_client: AsyncClient):
    """Test pagination of job descriptions."""
    response = await async_client.get("/jobs/descriptions?page=1&page_size=2")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert len(payload["items"]) <= 2
    assert payload["page"] == 1
    assert payload["page_size"] == 2


async def test_job_with_candidate_matching(async_client: AsyncClient):
    """Test job retrieval with candidate matching scores."""
    # Create a test candidate first
    candidate_response = await async_client.post("/candidates/", json={
        "candidate_id": "test_candidate_jobs",
        "name": "Test Candidate",
        "email": "test@example.com",
        "skills": ["python", "javascript"]
    })
    assert candidate_response.status_code == 201

    # Get jobs with candidate matching
    response = await async_client.get("/jobs/?candidate_id=test_candidate_jobs")
    assert response.status_code == 200
    payload = response.json()

    # Check that jobs have match_score when candidate_id is provided
    for job in payload["items"]:
        if "match_score" in job:
            assert isinstance(job["match_score"], (int, float))
            assert 0 <= job["match_score"] <= 100

    # Clean up
    await async_client.delete(f"/candidates/test_candidate_jobs")


async def test_job_exclude_applied(async_client: AsyncClient):
    """Test excluding already applied jobs."""
    # Create test candidate and job
    candidate_response = await async_client.post("/candidates/", json={
        "candidate_id": "test_exclude_applied",
        "name": "Test Candidate",
        "email": "test@example.com"
    })
    assert candidate_response.status_code == 201

    job_response = await async_client.post("/jobs/", json={
        "title": "Test Job for Exclusion",
        "company": "Test Company",
        "location": "Test Location"
    })
    assert job_response.status_code == 201
    job_data = job_response.json()
    job_id = job_data["job_id"]

    # Apply to the job
    application_response = await async_client.post("/applications/", json={
        "candidate_id": "test_exclude_applied",
        "job_id": job_id
    })
    assert application_response.status_code == 201

    # Get jobs without exclude_applied - should include the job
    response = await async_client.get("/jobs/?candidate_id=test_exclude_applied")
    assert response.status_code == 200
    all_jobs = response.json()["items"]
    job_ids = [job["id"] for job in all_jobs]

    # Get jobs with exclude_applied - should exclude the applied job
    response = await async_client.get("/jobs/?candidate_id=test_exclude_applied&exclude_applied=true")
    assert response.status_code == 200
    filtered_jobs = response.json()["items"]
    filtered_job_ids = [job["id"] for job in filtered_jobs]

    # The applied job should not be in filtered results
    assert job_id not in filtered_job_ids

    # Clean up
    await async_client.delete(f"/applications/candidate/test_exclude_applied/job/{job_id}")
    await async_client.delete(f"/jobs/{job_id}")
    await async_client.delete(f"/candidates/test_exclude_applied")