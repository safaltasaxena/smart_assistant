from google.cloud import firestore

db = firestore.Client()

def save(user_id, key, value):
    db.collection("users").document(user_id).set({key: value}, merge=True)

def load(user_id, key):
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return doc.to_dict().get(key, [])
    return []