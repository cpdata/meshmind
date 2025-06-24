"""
Example flow: extract → preprocess → store using Meshmind pipeline.
Requires a running Memgraph instance and a valid OPENAI_API_KEY.
"""
from meshmind.core.types import Memory
from meshmind.client import MeshMind

def main():
    # Initialize MeshMind client (uses OpenAI and default MemgraphDriver)
    mm = MeshMind()
    driver = mm.driver

    # Sample content for extraction
    texts = [
        "The Eiffel Tower is located in Paris and was built in 1889.",
        "Python is a programming language created by Guido van Rossum."
    ]

    # Extract memories via LLM
    memories = mm.extract_memories(
        instructions="Extract key facts as Memory objects.",
        namespace="demo",
        entity_types=[Memory],        
        content=texts,
    )
    print(f"Extracted {len(memories)} memories:")
    for m in memories:
        print(m.json())

    # Preprocess: deduplicate, score importance, compress
    memories = mm.deduplicate(memories, threshold=0.9)
    memories = mm.score_importance(memories)
    memories = mm.compress(memories)

    # Store into graph
    mm.store_memories(memories)
    print("Memories stored to graph.")

if __name__ == "__main__":
    main()