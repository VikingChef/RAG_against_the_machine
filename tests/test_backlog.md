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

### DatasetLoader cases
- valid dataset file loads successfully
- missing file raises FileMissingError
- malformed JSON raises InvalidJsonError
- structurally invalid dataset raises InvalidDatasetError

### Dataset writer cases
- writes StudentSearchResults successfully
- writes StudentSearchResultsAndAnswer successfully
- output JSON has the expected structure
- write failure raises DatasetWriteError


### CorpusLoader
- Load supported source files from a valid corpus root.
- Discover supported files inside nested directories.
- Skip unsupported file extensions.
- Reject an invalid or non-directory corpus root with `InvalidCorpusRootError`.
- Raise `SourceFileReadError` when an eligible source file cannot be read or decoded.