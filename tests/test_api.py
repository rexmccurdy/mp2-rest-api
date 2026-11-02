def test_upload_csv(client, sample_csv_bytes):
    response = client.post("/upload", files = {"file": ("sample_data.csv", sample_csv_bytes, "text/csv")})
    assert response.status_code == 200
    assert response.json()["rows"] == 6
    assert response.json()["columns"]== 2
    assert response.json()["id"] > 0    


def test_process_and_retrieve(
    client, uploaded_dataset_id, processing_body
):
    response = client.post(f"/datasets/{uploaded_dataset_id}/process", json=processing_body)
    assert response.status_code == 200
    assert response.json()["cleaning_report"]["rows_before"] == 5
    assert response.json()["cleaning_report"]["rows_after"] == 3

    response = client.get(f"/datasets/{uploaded_dataset_id}")
    assert response.status_code == 200
    assert response.json()["total_rows"] == 3
    student_ids = [record["student_id"] for record in response.json()["data"]]
    assert set(student_ids) == {1, 2, 5}
    scores = [record["score"] for record in response.json()["data"]]
    assert set(scores) == {80, 90, 85}



def test_retrieve_missing_dataset(client):
    respone = client.get("/datasets/9999")
    assert respone.status_code == 404