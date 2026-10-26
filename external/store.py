"""Open the index named in config. SQLite is the default."""


def open_store(settings: dict):
    if settings.get("store") == "firestore":
        from external.config import FIREBASE_PROJECT_ID
        from shared.store.firestore import FirestoreVectorStore

        return FirestoreVectorStore(
            collection=settings["firestore_collection"],
            project_id=FIREBASE_PROJECT_ID or None,
        )
    from shared.store.sqlite_store import SqliteVectorStore

    return SqliteVectorStore(settings["index_path"])
