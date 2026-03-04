# PGx Sequence Aligner

Sequence alignment + pharmacogenomic annotation tool (PharmGKB-integrated).

## Repo layout
- align/  alignment algorithms
- api/    service layer
- data/   sample inputs/outputs
- tests/  unit tests

## Example Output

CLI run:

Score: 5
ACCGTATGCA
AC-GTTTGCA


API response:

{
"aligned_seq_a": "ACCGTATGCA",
"aligned_seq_b": "AC-GTTTGCA",
"score": 5
}


