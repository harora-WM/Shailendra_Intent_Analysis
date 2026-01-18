# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an intent classification system for a Conversational SLO Manager. It maps natural language queries to specific intents and determines which data sources should be queried to answer them. The system is configuration-driven using YAML files and uses AWS Bedrock (Claude 3.5) for intelligent intent classification.

## Architecture

### Core Components

**Intent Hierarchy**: Two-level categorization system
- **Categories** (8 top-level): STATE, TREND, PATTERN, CAUSE, IMPACT, ACTION, PREDICT, OPTIMIZE, EVIDENCE
- **Intents** (30+ specific): Each category contains multiple specific intents (e.g., ROOT_CAUSE_SINGLE, BLAST_RADIUS)

**Data Sources** (4 types):
- `java_stats_api`: REST API for real-time metrics, service health, performance data
- `postgres`: Relational database for SLOs, alerts, incidents, change history
- `clickhouse`: Analytical database for trends, patterns, historical analysis, AI memory
- `opensearch`: Search engine for logs, traces, error patterns, audit trails

**Enrichment System**: Automatic intent expansion
- When a primary intent is detected, related intents are automatically included
- Example: `ROOT_CAUSE_SINGLE` automatically enriches with `UNDERCURRENTS_TREND` and `MITIGATION_STEPS`
- This creates comprehensive answers by pulling relevant context

### Configuration Files

**intent_categories.yaml**:
- Defines all intent categories and their specific intents
- Each intent has: description, example queries, and required data sources
- Format: `CATEGORY > intent > {description, examples[], data_sources[]}`

**enrichment_rules.yaml**:
- Maps primary intents to related intents that should be auto-included
- Creates comprehensive query plans by combining related contexts
- Format: `PRIMARY_INTENT: [list of related intents]`

**data_sources.yaml**:
- Defines available data sources and their capabilities
- Includes connection settings (timeouts, pool sizes, retry attempts)
- Maps intent categories to their required data sources

## Key Design Patterns

**Intent Mapping Strategy**:
1. User query → Intent detection (from 30+ specific intents)
2. Enrichment rules apply → Related intents added automatically
3. Data sources determined → Based on all intents in the enriched set
4. Query execution → Multi-source data retrieval

**Data Source Selection Logic**:
- Each intent declares required data sources
- Enrichment can expand the data source list
- Categories also have default data source mappings for fallback

**Examples of Intent Chains**:
- `ALERT_DEBUG` → auto-includes `ROOT_CAUSE_SINGLE`, `BLAST_RADIUS`, `MITIGATION_STEPS`
- `SLO_STATUS` → auto-includes `SLO_BURN_TREND`, `RISK_PREDICTION`
- `PERFORMANCE_BOTTLENECK` → auto-includes `QUERY_OPTIMIZATION`, `RESOURCE_WASTE`

## Modification Guidelines

**Adding a new intent**:
1. Add to appropriate category in `intent_categories.yaml`
2. Include description, example queries, and data sources
3. Add enrichment rules in `enrichment_rules.yaml` if related to other intents
4. Verify data source capabilities match in `data_sources.yaml`

**Modifying enrichment rules**:
- Consider the query context: Does the enrichment add value?
- Avoid circular enrichment chains
- Balance comprehensiveness vs. query performance

**Data source changes**:
- Update capabilities list when data source features change
- Adjust timeouts based on query performance
- Maintain intent_data_sources mapping consistency with individual intent definitions

## Implementation

### Python Intent Classifier (`intent_classifier.py`)

**Main Class**: `IntentClassifier`
- Loads YAML configurations at initialization
- Builds intent-to-data-source mapping from configuration
- Uses AWS Bedrock runtime client for LLM inference
- Temperature set to 0.0 for deterministic classification

**Classification Flow**:
1. `classify(user_query)` → Calls AWS Bedrock with system prompt
2. LLM returns JSON array of primary intent(s)
3. `_get_enrichment_intents()` → Expands with related intents from enrichment rules
4. `_get_data_sources()` → Collects all required data sources from enriched intent set
5. Returns complete classification result with enrichment details

**Key Methods**:
- `_call_bedrock()`: Handles AWS Bedrock API calls, JSON parsing, and error handling
- `_build_system_prompt()`: Generates LLM prompt from intent_categories.yaml
- `print_result()`: Pretty-prints classification results with emoji indicators

### Setup and Testing

**Quick Setup**: Run `./setup.sh` to create venv and install dependencies

**Configuration**: `.env` file (copy from `.env.example`) requires:
- AWS credentials (access key, secret key)
- AWS region (default: us-east-1)
- Bedrock model ID (default: claude-3-5-sonnet-20241022-v2:0)

**Testing**:
- Interactive mode: `python intent_classifier.py`
- Automated tests: `python test_classifier.py` (runs 20+ example queries)

**Dependencies**:
- `boto3`: AWS SDK for Bedrock
- `pyyaml`: YAML configuration parsing
- `python-dotenv`: Environment variable management
