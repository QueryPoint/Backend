from uuid import uuid4, UUID

from src.core.elasticsearch.client import es_connect

INDEX_NAME = "documents"

ANALYZER_NAME = "ru_analyzer"

MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                ANALYZER_NAME: {
                    "type": "russian"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "chunk_id":    {"type": "keyword"},
            "doc_id":      {"type": "keyword"},
            "user_id":     {"type": "keyword"},
            "file_name":   {"type": "keyword"},
            "page_number": {"type": "integer"},
            "text":        {"type": "text", "analyzer": ANALYZER_NAME},
        }
    }
}

class ElasticService:
    def __init__(self, client=es_connect, index: str = INDEX_NAME):
        self.client = client
        self.index = index

    async def init_index(self) -> None:
        if await self.client.indices.exists(index=self.index):
            mapping = await self.client.indices.get_mapping(index=self.index)
            analyzer = (
                mapping[self.index]["mappings"]
                .get("properties", {})
                .get("text", {})
                .get("analyzer")
            )
            if analyzer == ANALYZER_NAME:
                return
            # старый индекс без русского анализатора — пересоздаём.
            # метаданные документов лежат в PostgreSQL, файлы в S3,
            # так что документы можно переиндексировать заново.
            await self.client.indices.delete(index=self.index)

        await self.client.indices.create(index=self.index, body=MAPPING)

    @staticmethod
    def _chunk_text(text: str, size: int = 1000, overlap: int = 100) -> list[str]:
        chunks: list[str] = []
        start = 0
        while start < len(text):
            chunk = text[start:start + size].strip()
            if chunk:
                chunks.append(chunk)
            start += size - overlap
        return chunks

    async def index_chunks(
        self,
        doc_id: UUID,
        user_id: UUID,
        file_name: str,
        text: str,
        page_number: int = 1,
    ) -> None:
        for chunk in self._chunk_text(text):
            await self.client.index(
                index=self.index,
                document={
                    "chunk_id": str(uuid4()),
                    "doc_id": str(doc_id),
                    "user_id": str(user_id),
                    "file_name": file_name,
                    "page_number": page_number,
                    "text": chunk,
                },
            )
        await self.client.indices.refresh(index=self.index)

    async def search(self, user_id: UUID, query: str) -> list[dict]:
        response = await self.client.search(
            index=self.index,
            body={
                "query": {
                    "bool": {
                        "must": {
                            "multi_match": {"query": query, "fields": ["text"]}
                        },
                        "filter": {
                            "term": {"user_id": str(user_id)}
                        },
                    }
                },
                "highlight": {"fields": {"text": {}}},
            },
        )

        results: list[dict] = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            highlighted = hit.get("highlight", {}).get("text", [source["text"]])[0]
            results.append({
                "file_name": source["file_name"],
                "page_number": source["page_number"],
                "chunk_id": source["chunk_id"],
                "text": highlighted,
                "score": hit["_score"],
            })
        return results

    async def delete_chunks(self, doc_id: UUID) -> None:
        await self.client.delete_by_query(
            index=self.index,
            body={"query": {"term": {"doc_id": str(doc_id)}}},
        )
        await self.client.indices.refresh(index=self.index)

elastic_service = ElasticService()