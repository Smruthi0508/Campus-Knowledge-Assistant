
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_documents():
    documents = []

    for file_path in DATA_DIR.glob("*.md"):

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for line in lines:
            text = line.strip()

            if text:
                documents.append({
                    "text": text,
                    "source": file_path.name
                })

    return documents


def retrieve_information(question, top_k=2):

    documents = load_documents()

    if not documents:
        return []

    chunks = [doc["text"] for doc in documents]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    document_vectors = vectorizer.fit_transform(chunks)

    question_vector = vectorizer.transform([question])

    scores = cosine_similarity(
        question_vector,
        document_vectors
    ).flatten()

    ranked_indices = scores.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:

        if scores[index] < 0.12:
            continue

        results.append({
            "text": documents[index]["text"],
            "source": documents[index]["source"],
            "score": round(float(scores[index]), 3)
        })

    return results


if __name__ == "__main__":

    question = input("Enter your campus question: ")

    results = retrieve_information(question)

    if results:
        print("\nRetrieved Information:\n")

        for result in results:
            print("Text:", result["text"])
            print("Source:", result["source"])
            print("Similarity:", result["score"])
            print("-" * 40)

    else:
        print("No matching information found.")
