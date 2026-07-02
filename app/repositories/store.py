from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.core.firebase import get_firestore_client


class Store:
    def list(self, collection: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def get(self, collection: str, document_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def set(self, collection: str, document_id: str, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def delete(self, collection: str, document_id: str) -> None:
        raise NotImplementedError


class MemoryStore(Store):
    def __init__(self) -> None:
        self._data: dict[str, dict[str, dict[str, Any]]] = {}

    def list(self, collection: str) -> list[dict[str, Any]]:
        return [deepcopy(value) for value in self._data.get(collection, {}).values()]

    def get(self, collection: str, document_id: str) -> dict[str, Any] | None:
        data = self._data.get(collection, {}).get(document_id)
        return deepcopy(data) if data else None

    def set(self, collection: str, document_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self._data.setdefault(collection, {})[document_id] = deepcopy(data)
        return deepcopy(data)

    def delete(self, collection: str, document_id: str) -> None:
        self._data.get(collection, {}).pop(document_id, None)


class FirestoreStore(Store):
    def __init__(self, client) -> None:
        self.client = client

    def list(self, collection: str) -> list[dict[str, Any]]:
        return [doc.to_dict() for doc in self.client.collection(collection).stream()]

    def get(self, collection: str, document_id: str) -> dict[str, Any] | None:
        snapshot = self.client.collection(collection).document(document_id).get()
        return snapshot.to_dict() if snapshot.exists else None

    def set(self, collection: str, document_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self.client.collection(collection).document(document_id).set(data)
        return data

    def delete(self, collection: str, document_id: str) -> None:
        self.client.collection(collection).document(document_id).delete()


class ResilientStore(Store):
    def __init__(self, primary: Store, fallback: Store) -> None:
        self.primary = primary
        self.fallback = fallback
        self._use_fallback = False

    def _run(self, operation, fallback_operation):
        if self._use_fallback:
            return fallback_operation()
        try:
            return operation()
        except Exception:
            self._use_fallback = True
            return fallback_operation()

    def list(self, collection: str) -> list[dict[str, Any]]:
        return self._run(
            lambda: self.primary.list(collection),
            lambda: self.fallback.list(collection),
        )

    def get(self, collection: str, document_id: str) -> dict[str, Any] | None:
        return self._run(
            lambda: self.primary.get(collection, document_id),
            lambda: self.fallback.get(collection, document_id),
        )

    def set(self, collection: str, document_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self._run(
            lambda: self.primary.set(collection, document_id, data),
            lambda: self.fallback.set(collection, document_id, data),
        )

    def delete(self, collection: str, document_id: str) -> None:
        return self._run(
            lambda: self.primary.delete(collection, document_id),
            lambda: self.fallback.delete(collection, document_id),
        )


_memory_store = MemoryStore()
_firestore_store: Store | None = None


def get_store() -> Store:
    global _firestore_store
    client = get_firestore_client()
    if client is None:
        return _memory_store
    if _firestore_store is None:
        _firestore_store = ResilientStore(FirestoreStore(client), _memory_store)
    return _firestore_store
