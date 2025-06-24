# MeshMind

MeshMind is a knowledge management system that uses LLMs and graph databases to store and retrieve information.
Adding, Searching, Updating, and Deleting memories is supported.
Retrieval of memories using LLMs and graph databases by comparing embeddings and graph database metadata.

## Features

- Adding memories
- Searching memories
- Updating memories
- Deleting memories
- Extracting memories from content
- Expiring memories
- Memory Importance Ranking
- Memory Deduplication
- Memory Consolidation
- Memory Compression

## Retrieval Methods

- Embedding Vector Search
- BM25 Retrieval
- ReRanking with LLM
- Fuzzy Search
- Exact Comparison Search
- Regex Search
- Search Filters
- Hybrid Search Methods

## Components
- OpenAI API
- MemGraphDB (Alternative to Neo4j)
- Embedding Model

# Types of Memory

- Long-Term Memory - Persistent Memory
    - Explicit Memory - Conscious Memory - Active Hotpath Memory (Triggered in Response to Input)
        - Declarative Memory - Conscious Memory
            - Semantic Memory - What is known
            - Eposodic Memory - What has been experienced
            - Procedural Memory - How to perform tasks

    - Implicit Memory - Subconscious Memory - Background Process Memory (Triggered in Intervals)
        - Non-Declarative Memory - Subconscious Memory
            - Semantic Memory - Implicitly acquired
            - Eposodic Memory - Implicitly acquired
            - Procedural Memory - Implicitly acquired

- Short-Term Memory - Transient Memory
    - Working Memory (Processing) [reasoning messages, scratchpad, etc]
    - Sensory Memory (Input) [user input, system input, etc]
    - Log Storage (Output) [assistant responses, tool logs, etc]

# Methods
- Extract Memory
- Add Memory
- Add Triplet
- Search Memory
- Update Memory
- Delete Memory

## Usage

```python
from meshmind import MeshMind
from pydantic import BaseModel, Field

# Pydantic model's name will be used as the node label in the graph database.
# This defines the attributes of the entity.
# Attributes of the entity are stored in entity metadata['attributes']
class Person(BaseModel):
    first_name: str | None = Field(..., description="First name of the person")
    last_name: str | None = Field(None, description="Last name of the person")
    description: str | None = Field(None, description="Description of the person")
    job_title: str | None = Field(None, description="Job title of the person")    

# Initialize MeshMind
mesh_mind = MeshMind()

# Register pydantic model as entity
mesh_mind.register_entity(Person)

# Register allowed relationship predicates labels.
mesh_mind.register_allowed_predicates([
    "employee_of",
    "on_team",
    "on_project",
])

# Add edge - This will create an edge in the graph database. (Alternative to `register_allowed_types`)
mesh_mind.add_predicate("has_skill")

# Extract memories - [High Level API] - This will create nodes and edges based on the content provided. Extracts memories from the content.
extracted_memories = mesh_mind.extract_memories(
    instructions="Extract all memories from the database.",
    namespace="Company Employees",
    entity_types=[Person],
    content=["John Doe, Software Engineer 10 years of experience.", "Jane Doe, Software Engineer 5 years of experience."]
    )

for memory in extracted_memories:
    # Store memory - This will perform deduplication, add uuid, add timestamps, format memory and store the memory in the graph database using `add_triplet`.
    mesh_mind.store_memory(memory)

# Add memory - [Mid Level API] - This will perform all preprocessing steps i.e. deduplication, add uuid, add timestamps, format memory, etc. and store the memory in the graph database using `add_triplet`. ( Skips extraction and automatically adds memory to the graph database ) **Useful for adding custom memories**
mesh_mind.add_memory(
    namespace="Company Employees",
    name="John Doe", 
    entity_label="Person",   
    entity=Person(
        first_name="John",
        last_name="Doe",
        description="John Doe",
        job_title="Software Engineer",
    ),
    metadata={
        "source": "John Doe Employee Record",
        "source_type": "text",        
        }
)

# `add_triplet` - [Low Level API]
#
# Add a [node, edge, node] triplet - This will create a pair of nodes and a connecting edge in the graph database using db driver. 
# This bypasses deduplication and other preprocessing steps and directly adds the data to the graph database.
# This is useful for adding data that is not in the format of a memory.
#
# subject: The subject of the triplet. ( Source Entity Node Label Name )
# predicate: The predicate of the triplet. ( Relationship between the subject and object, registered using `register_allowed_predicates` )
# object: The object of the triplet. ( Target Entity Node Label Name )
# namespace: The namespace of the triplet. ( Group of related nodes and edges )
# entity_label: The label of the entity. ( Type of node, registered using `register_entity` )
# metadata: The metadata of the triplet. ( Additional information about the triplet )
# reference_time: The time at which the triplet was created. ( Optional )
#
# If the subject, predicate, object, namespace, or entity_label does not exist, it will be created.
#
#  Example:
mesh_mind.add_triplet(
    subject="John Doe",
    predicate="on_project",
    object="Project X",
    namespace="Company Employees",
    entity_label="Person",
    metadata={
        "source": "John Doe Project Record",
        "source_type": "text",
        "summary": "John Doe is on project X.",
        "attributes": {
            "first_name": "John",
            "last_name": "Doe",
            "description": "John Doe",
            "job_title": "Software Engineer",
            }
        },    
    reference_time="2025-05-09T23:31:51-04:00"
)

# Search - [High Level API] - This will search the graph database for nodes and edges based on the query.
search_results = mesh_mind.search(
    query="John Doe",
    namespace="Company Employees",
    entity_types=[Person],
    )

for search_result in search_results:
    print(search_result)

# Search - [Mid Level API] - This will search the graph database for nodes and edges based on the query.
search_results = mesh_mind.search_facts(
    query="John Doe",
    namespace="Company Employees",
    entity_types=[Person],
    config=SearchConfig(
            encoder="text-embedding-3-small",
        )
    )

for search_result in search_results:
    print(search_result)

# Search - [Low Level API] - This will search the graph database for nodes and edges based on the query.
search_results = mesh_mind.search_procedures(
    query="John Doe",
    namespace="Company Employees",
    entity_types=[Person],
    config=SearchConfig(
        encoder="text-embedding-3-small",
        )
    )

# Update Memory - Same as `add_memory` but updates an existing memory.
mesh_mind.update_memory(
    uuid="12345678-1234-1234-1234-123456789012",
    namespace="Company Employees",
    name="John Doe", 
    entity_label="Person",   
    entity=Person(
        first_name="John",
        last_name="Doe",
        description="John Doe",
        job_title="Software Engineer",
    ),
    metadata={
        "source": "John Doe Employee Record",
        "source_type": "text",        
        }
)

# Delete Memory
mesh_mind.delete_memory(
    uuid="12345678-1234-1234-1234-123456789012"
)

for search_result in search_results:
    print(search_result)

```

## Command-Line Interface (CLI)

MeshMind includes a `meshmind` CLI tool for ingesting content via the extract → preprocess → store pipeline.

Usage:
```bash
meshmind --help
```
Primary command:
```bash
meshmind ingest \
  -n <namespace> \
  [-e <embedding-model>] \
  [-i "<instructions>"] \
  <path1> [<path2> ...]
```
Example:
```bash
meshmind ingest -n demo --embedding-model text-embedding-3-small ./data/articles
```
This reads text files under `./data/articles`, extracts memories, deduplicates, scores, compresses,
and stores them in your Memgraph database under the `demo` namespace.

