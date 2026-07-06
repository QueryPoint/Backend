from elasticsearch import AsyncElasticsearch
from src.config.config import config

es_connect = AsyncElasticsearch(hosts=[config.elasticsearch.URL])