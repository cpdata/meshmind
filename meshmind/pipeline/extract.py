from typing import Any, List, Sequence, Type

from meshmind.core.observability import log_event, telemetry

def extract_memories(
    instructions: str,
    namespace: str,
    entity_types: Sequence[Type[Any]],
    embedding_model: str,
    content: Sequence[str],
    llm_client: Any = None,
) -> List[Any]:
    """
    Extract structured Memory objects from provided content using an LLM.

    :param instructions: Prompt instructions for the LLM extraction.
    :param namespace: Namespace under which memories will be stored.
    :param entity_types: List of registered Pydantic model classes for entity extraction.
    :param embedding_model: Name of the embedding model to use for text encoding.
    :param content: List of text strings to extract memories from.
    :param llm_client: Optional LLM client instance (defaults to OpenAI).
    :return: List of extracted Memory-like dicts or objects.
    """
    import json
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package is required for extraction pipeline")
    from meshmind.core.types import Memory
    from meshmind.core.embeddings import EncoderRegistry
    from meshmind.models.registry import EntityRegistry

    log_event("pipeline.extract.start", segments=len(content))

    # Initialize default LLM client if not provided
    if llm_client is None:
        llm_client = OpenAI()

    # Prepare function schema for Memory items
    mem_schema = Memory.schema()
    function_spec = {
        "name": "extract_memories",
        "description": "Extract structured memories from text segments",
        "parameters": {
            "type": "object",
            "properties": {
                "memories": {"type": "array", "items": mem_schema}
            },
            "required": ["memories"],
        },
    }

    # Build system prompt using a default template and user instructions
    entity_types = list(entity_types) or [Memory]
    for model in entity_types:
        EntityRegistry.register(model)
    allowed_labels = [cls.__name__ for cls in entity_types]
    default_prompt = (
        "You are an agent that extracts structured memories from text segments. "
        "For each provided text, return a structured JSON payload by calling the function 'extract_memories'. "
        "The function takes a single parameter 'memories', which is an array of Memory objects "
        "matching the Memory JSON schema."
    )
    prompt = instructions.strip() if instructions and instructions.strip() else default_prompt
    if allowed_labels:
        prompt += f"\nAllowed entity labels: {', '.join(allowed_labels)}."
    messages = [{"role": "system", "content": prompt}]
    # Add each text segment as a user message
    messages += [{"role": "user", "content": text} for text in list(content)]

    # Call chat completion with function-calling
    with telemetry.track_duration("pipeline.extract.duration"):
        response = llm_client.responses.create(
            model="gpt-4.1-mini",
            messages=messages,
            functions=[function_spec],
            function_call={"name": "extract_memories"},
        )
    msg = response.choices[0].message
    # Parse function call arguments or direct JSON
    if msg.get("function_call"):
        arg_str = msg["function_call"]["arguments"]
        data = json.loads(arg_str)
        items = data.get("memories", [])
    else:
        # fallback: parse content
        try:
            items = json.loads(msg.get("content", "[]"))
        except json.JSONDecodeError:
            raise ValueError("Extraction output is not valid JSON")

    memories = []
    # Instantiate Memory objects, validate entity labels, and compute embeddings
    from pydantic import ValidationError
    encoder = EncoderRegistry.get(embedding_model)
    for entry in items:
        label = entry.get("entity_label")
        if label not in allowed_labels:
            raise ValueError(f"Invalid entity_label '{label}', expected one of {allowed_labels}")
        # ensure namespace is set before validation
        entry['namespace'] = namespace
        try:
            mem = Memory(**entry)
        except ValidationError as e:
            raise ValueError(f"Memory validation failed for entry {entry}: {e}")
        # compute embedding for the name field
        if mem.name:
            emb = encoder.encode([mem.name])[0]
            mem.embedding = emb
        memories.append(mem)

    telemetry.increment("pipeline.extract.segments", len(content))
    telemetry.increment("pipeline.extract.memories", len(memories))
    log_event("pipeline.extract.complete", memories=len(memories))
    return memories
