
from unittest.mock import MagicMock
from src.core.s3.s3_service import S3Service

def service_with(client):
    service = S3Service()
    service._client = client
    return service

def test_s3_upload_returns_true_on_success():
    client = MagicMock()
    service = service_with(client)
    assert service.upload_file(b"data", "key") is True
    client.put_object.assert_called_once()

def test_s3_upload_returns_false_on_exception():
    client = MagicMock()
    client.put_object.side_effect = Exception("storage down")
    assert service_with(client).upload_file(b"data", "key") is False

def test_s3_generate_presigned_url_returns_none_on_exception():
    client = MagicMock()
    client.generate_presigned_url.side_effect = Exception("down")
    assert service_with(client).generate_presigned_url("key", 60) is None

def test_s3_delete_and_get_return_expected_values():
    client = MagicMock()
    client.get_object.return_value = {"Body": MagicMock(read=lambda: b"document")}
    service = service_with(client)
    assert service.delete_file("key") is True
    assert service.get_file("key") == b"document"
