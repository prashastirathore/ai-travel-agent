from app.rag.documents import get_destination_knowledge


def retrieve_context(destination: str):

    knowledge = get_destination_knowledge(
        destination
    )

    return {
        "destination": destination,
        "knowledge": knowledge
    }