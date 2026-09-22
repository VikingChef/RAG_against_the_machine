# Test Backlog

## Models

### Chunk
- Reject negative `first_character_index`.
- Reject negative `last_character_index`.
- Reject `last_character_index` values smaller than `first_character_index`.

### Query
- Reject empty query text.
- Reject whitespace-only query text.
- Reject negative `k`.

### Evaluation Models
- Auto-generate a `question_id` when one is not provided.
- Preserve a provided `question_id`.
- Nest `MinimalSource` correctly inside `MinimalSearchResults`.
- Nest `MinimalAnswer` correctly inside `StudentSearchResultsAndAnswer`.
- Serialize evaluator-facing models into the expected structure.