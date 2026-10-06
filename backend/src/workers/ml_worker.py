import threading

from ..ml import MlPipeline
from ..services.ingest import get_pending_documents,save_document_results,mark_document_failed

wake_event = threading.Event()
stop_event = threading.Event()

def worker_loop():
    pipeline = MlPipeline()
    while not stop_event.is_set():
        docs = get_pending_documents()
        if docs is None or len(docs)==0:
            wake_event.wait(timeout=3)
            wake_event.clear()
            continue
        doc = docs[0]
        try:
            result = pipeline.process(doc["path"])
            save_document_results(doc["document_id"],result)
        except Exception:
            mark_document_failed(doc["document_id"])


def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True, name="ml-worker")
    t.start()
    return t
