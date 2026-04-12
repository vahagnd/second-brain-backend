# AI Behavior Rules

## Retrieval
- Keyword-based search only (SQL LIKE)
- No embeddings
- No vector search

## Context rule
- Max 5 notes passed into LLM

## LLM usage
- Single wrapper function only
- Always deterministic prompt structure

## Prompt format

Context:
{notes}

Question:
{question}

Answer clearly and concisely.
