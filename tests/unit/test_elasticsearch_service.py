
from uuid import uuid4
import pytest
from src.core.elasticsearch.es_servise import ElasticService, MAPPING

pytestmark = pytest.mark.unit

@pytest.mark.asyncio
async def test_init_index_creates_mapping_when_absent(fake_es_client):
    fake_es_client.indices.exists.return_value = False
    service = ElasticService(client=fake_es_client)
    await service.init_index()
    fake_es_client.indices.create.assert_awaited_once_with(index="documents", body=MAPPING)

@pytest.mark.asyncio
async def test_index_chunks_writes_each_chunk_and_refreshes(fake_es_client, user_id):
    service = ElasticService(client=fake_es_client)
    await service.index_chunks(uuid4(), user_id, "lecture.pdf", "a"*1100, page_number=3)
    assert fake_es_client.index.await_count == 2
    fake_es_client.indices.refresh.assert_awaited_once_with(index="documents")

@pytest.mark.asyncio
async def test_search_filters_by_current_user_and_uses_highlight(fake_es_client, user_id):
    fake_es_client.search.return_value = {"hits": {"hits": [{
        "_score": 7.2,
        "_source": {"file_name": "lecture.pdf", "page_number": 2, "chunk_id": "chunk", "text": "source"},
        "highlight": {"text": ["<em>source</em>"]},
    }]}}
    result = await ElasticService(client=fake_es_client).search(user_id, "source")
    assert result == [{"file_name":"lecture.pdf","page_number":2,"chunk_id":"chunk","text":"<em>source</em>","score":7.2}]
    body = fake_es_client.search.await_args.kwargs["body"]
    assert body["query"]["bool"]["filter"]["term"]["user_id"] == str(user_id)

@pytest.mark.asyncio
async def test_delete_chunks_deletes_by_document_id_and_refreshes(fake_es_client):
    doc_id = uuid4()
    await ElasticService(client=fake_es_client).delete_chunks(doc_id)
    fake_es_client.delete_by_query.assert_awaited_once()
    assert str(doc_id) in str(fake_es_client.delete_by_query.await_args)
