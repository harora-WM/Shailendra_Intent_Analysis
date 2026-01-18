# YAML Configuration Guide

## Overview

This guide explains the three YAML configuration files that drive the intent classification system and how they work together to map user queries to data sources.

---

## Table of Contents

1. [Configuration Files Overview](#configuration-files-overview)
2. [intent_categories.yaml](#intent_categoriesyaml)
3. [enrichment_rules.yaml](#enrichment_rulesyaml)
4. [data_sources.yaml](#data_sourcesyaml)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Examples](#examples)
7. [Modification Guide](#modification-guide)

---

## Configuration Files Overview

```
┌─────────────────────────┐
│ intent_categories.yaml  │  → Defines all intents and their initial data sources
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ enrichment_rules.yaml   │  → Maps intents to related intents for enrichment
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   data_sources.yaml     │  → Defines available data sources and capabilities
└─────────────────────────┘
```

### File Relationships

1. **intent_categories.yaml** - The foundation
   - Contains 9 categories (STATE, TREND, PATTERN, CAUSE, IMPACT, ACTION, PREDICT, OPTIMIZE, EVIDENCE)
   - Each category has multiple specific intents
   - Each intent defines required data sources

2. **enrichment_rules.yaml** - The intelligence layer
   - Automatically adds related intents to provide comprehensive answers
   - Creates intent chains for better context

3. **data_sources.yaml** - The execution layer
   - Defines available data sources (Clickhouse, Java Stats API)
   - Maps categories to default data sources
   - Contains connection settings and capabilities

---

## intent_categories.yaml

### Structure

```yaml
CATEGORY_NAME:
  description: "Category description"
  intents:
    INTENT_NAME:
      description: "What this intent does"
      examples:
        - "Example user query 1"
        - "Example user query 2"
      data_sources:
        - data_source_1
        - data_source_2
```

### Categories and Their Purpose

| Category | Purpose | Example Intents | Count |
|----------|---------|-----------------|-------|
| **STATE** | Current status and health | CURRENT_HEALTH, SERVICE_HEALTH, SLO_STATUS | 5 |
| **TREND** | Changes over time | UNDERCURRENTS_TREND, HISTORICAL_COMPARISON | 4 |
| **PATTERN** | Recurring behaviors | SEASONALITY_PATTERN, TIME_WINDOW_ANOMALY | 3 |
| **CAUSE** | Root cause analysis | ROOT_CAUSE_SINGLE, ROOT_CAUSE_MULTI | 4 |
| **IMPACT** | Blast radius & business impact | BLAST_RADIUS, USER_JOURNEY_IMPACT | 4 |
| **ACTION** | Decision support | MITIGATION_STEPS, ROLLBACK_ADVICE | 4 |
| **PREDICT** | Future risk prediction | RISK_PREDICTION, CHANGE_RISK | 3 |
| **OPTIMIZE** | Performance/cost tuning | PERFORMANCE_BOTTLENECK, QUERY_OPTIMIZATION | 3 |
| **EVIDENCE** | Audit and explainability | EVIDENCE_SUMMARY, INCIDENT_TIMELINE | 3 |

### Intent Categories Flowchart

```
                    ┌─────────────────────────────────┐
                    │     User Query                  │
                    │  "Why is payment-api failing?"  │
                    └────────────┬────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────────┐
                    │   AWS Bedrock (Claude 3.5)      │
                    │   Classifies into Intent        │
                    └────────────┬────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
                ▼                                 ▼
    ┌───────────────────────┐       ┌───────────────────────┐
    │   STATE Category      │       │   CAUSE Category      │
    │                       │       │                       │
    │ • CURRENT_HEALTH      │       │ • ROOT_CAUSE_SINGLE ✓ │
    │ • SERVICE_HEALTH      │       │ • ROOT_CAUSE_MULTI    │
    │ • SLO_STATUS          │       │ • ALERT_DEBUG         │
    │ • ALERT_STATUS        │       │ • CONFIG_DRIFT_CAUSE  │
    │ • INCIDENT_STATUS     │       │                       │
    └───────────────────────┘       └───────────┬───────────┘
                                                 │
                                                 ▼
                                    ┌────────────────────────┐
                                    │  ROOT_CAUSE_SINGLE     │
                                    │  Data Sources:         │
                                    │  • java_stats_api      │
                                    │  • clickhouse          │
                                    └────────────────────────┘
```

### Example Intent Definition

```yaml
CAUSE:
  description: "Why it happened - Root cause analysis"
  intents:
    ROOT_CAUSE_SINGLE:
      description: "Root cause for single service failure"
      examples:
        - "Why is payment-api failing?"
        - "What caused the checkout error?"
        - "Root cause of login issues"
      data_sources:
        - java_stats_api
        - clickhouse
```

**Key Points:**
- `description`: Explains what the intent detects
- `examples`: Sample queries that match this intent (used in LLM prompt)
- `data_sources`: Which data sources are needed to answer this type of query

---

## enrichment_rules.yaml

### Structure

```yaml
PRIMARY_INTENT:
  - RELATED_INTENT_1
  - RELATED_INTENT_2
  - RELATED_INTENT_3
```

### Purpose

Enrichment rules automatically expand a primary intent with related intents to provide comprehensive, contextual answers. This prevents users from having to ask multiple follow-up questions.

### Enrichment Flow

```
┌──────────────────────┐
│  Primary Intent      │
│  ROOT_CAUSE_SINGLE   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│         Enrichment Rules Applied                     │
│                                                       │
│  ROOT_CAUSE_SINGLE:                                  │
│    - UNDERCURRENTS_TREND    (What's been changing?)  │
│    - MITIGATION_STEPS       (How to fix it?)         │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  Enriched Intent Set                                 │
│                                                       │
│  1. ROOT_CAUSE_SINGLE      (Primary)                 │
│  2. UNDERCURRENTS_TREND    (Enrichment)              │
│  3. MITIGATION_STEPS       (Enrichment)              │
└──────────┬───────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  Combined Data Sources                               │
│                                                       │
│  • java_stats_api    (from ROOT_CAUSE_SINGLE)        │
│  • clickhouse        (from all three intents)        │
└──────────────────────────────────────────────────────┘
```

### Example Enrichment Rules

```yaml
ROOT_CAUSE_SINGLE:
  - UNDERCURRENTS_TREND
  - MITIGATION_STEPS

SLO_STATUS:
  - SLO_BURN_TREND
  - RISK_PREDICTION

ALERT_DEBUG:
  - ROOT_CAUSE_SINGLE
  - BLAST_RADIUS
  - MITIGATION_STEPS
```

### Common Enrichment Patterns

| Primary Intent | Enriched With | Reasoning |
|----------------|---------------|-----------|
| **ROOT_CAUSE_SINGLE** | UNDERCURRENTS_TREND | Show what's been changing before the failure |
| **ROOT_CAUSE_SINGLE** | MITIGATION_STEPS | Provide fix recommendations |
| **SLO_STATUS** | SLO_BURN_TREND | Show how error budget is being consumed |
| **SLO_STATUS** | RISK_PREDICTION | Predict future SLO breaches |
| **ALERT_DEBUG** | ROOT_CAUSE_SINGLE | Find why the alert fired |
| **ALERT_DEBUG** | BLAST_RADIUS | Show impact of the issue |
| **PERFORMANCE_BOTTLENECK** | QUERY_OPTIMIZATION | Suggest query improvements |

---

## data_sources.yaml

### Structure

```yaml
data_sources:
  data_source_name:
    type: database_type
    description: "What it contains"
    capabilities:
      - capability_1
      - capability_2
    # Additional settings

intent_data_sources:
  CATEGORY:
    - data_source_1
    - data_source_2
```

### Available Data Sources

#### 1. java_stats_api

```yaml
java_stats_api:
  type: rest_api
  description: "Real-time metrics and statistics from Java services"
  capabilities:
    - current_metrics
    - service_health
    - performance_data
    - resource_usage
  timeout: 30
  retry_attempts: 3
```

**Use Cases:**
- Real-time service health checks
- Current performance metrics
- Live resource utilization
- Active service status

---

#### 2. clickhouse

```yaml
clickhouse:
  type: analytical_database
  description: "Historical data, trends, patterns, and AI memory"
  capabilities:
    - trend_analysis
    - pattern_detection
    - historical_comparison
    - ai_insights
    - similarity_search
    - incident_memory
    - slo_definitions
    - alert_history
    - incident_tracking
    - change_log
    - configuration_history
    - log_search
    - trace_analysis
    - error_patterns
    - audit_trail
  pool_size: 5
  compression: true
```

**Use Cases:**
- Historical trend analysis
- Pattern detection and anomaly identification
- SLO definitions and tracking
- Alert and incident history
- Configuration change tracking
- Log and trace analysis
- Audit trails and compliance
- AI-powered insights and memory

---

### Category to Data Source Mapping

```yaml
intent_data_sources:
  STATE:        [java_stats_api, clickhouse]
  TREND:        [java_stats_api, clickhouse]
  PATTERN:      [clickhouse]
  CAUSE:        [java_stats_api, clickhouse]
  IMPACT:       [java_stats_api, clickhouse]
  ACTION:       [clickhouse]
  PREDICT:      [clickhouse, java_stats_api]
  OPTIMIZE:     [java_stats_api, clickhouse]
  EVIDENCE:     [clickhouse]
```

---

## Data Flow Diagrams

### Complete Classification Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                              │
│              "Why is payment-api failing?"                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 STEP 1: INTENT CLASSIFICATION                   │
│                    (intent_categories.yaml)                     │
│                                                                 │
│  AWS Bedrock analyzes query against all 30+ intents            │
│  Returns: ["ROOT_CAUSE_SINGLE"]                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 2: ENRICHMENT                             │
│                  (enrichment_rules.yaml)                        │
│                                                                 │
│  Primary Intent: ROOT_CAUSE_SINGLE                              │
│  ├─ Add: UNDERCURRENTS_TREND                                   │
│  └─ Add: MITIGATION_STEPS                                      │
│                                                                 │
│  Result: [ROOT_CAUSE_SINGLE, UNDERCURRENTS_TREND,              │
│           MITIGATION_STEPS]                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 3: DATA SOURCE MAPPING                       │
│                  (data_sources.yaml)                            │
│                                                                 │
│  ROOT_CAUSE_SINGLE      → [java_stats_api, clickhouse]         │
│  UNDERCURRENTS_TREND    → [java_stats_api, clickhouse]         │
│  MITIGATION_STEPS       → [clickhouse]                         │
│                                                                 │
│  Combined (deduplicated):                                       │
│  └─ [clickhouse, java_stats_api]                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FINAL RESULT                               │
│                                                                 │
│  {                                                              │
│    "query": "Why is payment-api failing?",                     │
│    "primary_intents": ["ROOT_CAUSE_SINGLE"],                   │
│    "enriched_intents": ["MITIGATION_STEPS",                    │
│                         "ROOT_CAUSE_SINGLE",                    │
│                         "UNDERCURRENTS_TREND"],                 │
│    "data_sources": ["clickhouse", "java_stats_api"],           │
│    "enrichment_details": {                                      │
│      "ROOT_CAUSE_SINGLE": ["UNDERCURRENTS_TREND",              │
│                            "MITIGATION_STEPS"]                  │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

### Multi-Intent Classification Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                              │
│     "What alerts are active and what incidents are open?"       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 STEP 1: INTENT CLASSIFICATION                   │
│                                                                 │
│  AWS Bedrock detects MULTIPLE intents:                          │
│  Returns: ["ALERT_STATUS", "INCIDENT_STATUS"]                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 2: ENRICHMENT                             │
│                                                                 │
│  ALERT_STATUS has no enrichment rules                           │
│  INCIDENT_STATUS has no enrichment rules                        │
│                                                                 │
│  Result: [ALERT_STATUS, INCIDENT_STATUS]                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 3: DATA SOURCE MAPPING                       │
│                                                                 │
│  ALERT_STATUS       → [clickhouse]                              │
│  INCIDENT_STATUS    → [clickhouse]                              │
│                                                                 │
│  Combined: [clickhouse]                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

### Enrichment Chain Example

```
                    ┌────────────────────┐
                    │   ALERT_DEBUG      │
                    │   (Primary)        │
                    └─────────┬──────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
    │ROOT_CAUSE_SINGLE│ │BLAST_RADIUS │ │MITIGATION_STEPS  │
    │  (Enrichment)   │ │(Enrichment) │ │  (Enrichment)    │
    └────────┬────────┘ └──────┬──────┘ └────────┬─────────┘
             │                 │                  │
             └─────────┬───────┴──────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │  ROOT_CAUSE_SINGLE has its  │
         │  own enrichment rules too!  │
         └─────────────┬───────────────┘
                       │
         ┌─────────────┴──────────────┐
         │                            │
         ▼                            ▼
┌─────────────────┐          ┌──────────────────┐
│UNDERCURRENTS_   │          │ MITIGATION_STEPS │
│TREND (2nd level)│          │ (already added)  │
└─────────────────┘          └──────────────────┘

FINAL ENRICHED SET:
  1. ALERT_DEBUG          (Primary)
  2. ROOT_CAUSE_SINGLE    (1st level enrichment)
  3. BLAST_RADIUS         (1st level enrichment)
  4. MITIGATION_STEPS     (1st level enrichment - deduplicated)
  5. UNDERCURRENTS_TREND  (2nd level enrichment)
```

---

## Examples

### Example 1: Simple Query

**User Query:** `"Is payment-api healthy?"`

**Classification Process:**

1. **Intent Detection** (intent_categories.yaml)
   - Category: STATE
   - Intent: SERVICE_HEALTH
   - Data Sources: [java_stats_api]

2. **Enrichment** (enrichment_rules.yaml)
   - No enrichment rules for SERVICE_HEALTH
   - Enriched Intents: [SERVICE_HEALTH]

3. **Data Source Collection** (data_sources.yaml)
   - SERVICE_HEALTH → [java_stats_api]
   - Final: [java_stats_api]

**Result:**
```json
{
  "query": "Is payment-api healthy?",
  "primary_intents": ["SERVICE_HEALTH"],
  "enriched_intents": ["SERVICE_HEALTH"],
  "data_sources": ["java_stats_api"],
  "enrichment_details": {}
}
```

---

### Example 2: Query with Enrichment

**User Query:** `"Why is payment-api failing?"`

**Classification Process:**

1. **Intent Detection**
   - Category: CAUSE
   - Intent: ROOT_CAUSE_SINGLE
   - Data Sources: [java_stats_api, clickhouse]

2. **Enrichment**
   ```yaml
   ROOT_CAUSE_SINGLE:
     - UNDERCURRENTS_TREND
     - MITIGATION_STEPS
   ```
   - Enriched Intents: [ROOT_CAUSE_SINGLE, UNDERCURRENTS_TREND, MITIGATION_STEPS]

3. **Data Source Collection**
   - ROOT_CAUSE_SINGLE → [java_stats_api, clickhouse]
   - UNDERCURRENTS_TREND → [java_stats_api, clickhouse]
   - MITIGATION_STEPS → [clickhouse]
   - Final (deduplicated): [clickhouse, java_stats_api]

**Result:**
```json
{
  "query": "Why is payment-api failing?",
  "primary_intents": ["ROOT_CAUSE_SINGLE"],
  "enriched_intents": ["MITIGATION_STEPS", "ROOT_CAUSE_SINGLE", "UNDERCURRENTS_TREND"],
  "data_sources": ["clickhouse", "java_stats_api"],
  "enrichment_details": {
    "ROOT_CAUSE_SINGLE": ["UNDERCURRENTS_TREND", "MITIGATION_STEPS"]
  }
}
```

---

### Example 3: Multi-Intent Query

**User Query:** `"Are we meeting our SLOs and what's the trend?"`

**Classification Process:**

1. **Intent Detection**
   - Category: STATE, TREND
   - Intents: SLO_STATUS, SLO_BURN_TREND
   - Data Sources: [clickhouse] for both

2. **Enrichment**
   ```yaml
   SLO_STATUS:
     - SLO_BURN_TREND    # Already detected!
     - RISK_PREDICTION
   ```
   - Enriched Intents: [SLO_STATUS, SLO_BURN_TREND, RISK_PREDICTION]

3. **Data Source Collection**
   - SLO_STATUS → [clickhouse]
   - SLO_BURN_TREND → [clickhouse]
   - RISK_PREDICTION → [clickhouse, java_stats_api]
   - Final: [clickhouse, java_stats_api]

**Result:**
```json
{
  "query": "Are we meeting our SLOs and what's the trend?",
  "primary_intents": ["SLO_STATUS", "SLO_BURN_TREND"],
  "enriched_intents": ["RISK_PREDICTION", "SLO_BURN_TREND", "SLO_STATUS"],
  "data_sources": ["clickhouse", "java_stats_api"],
  "enrichment_details": {
    "SLO_STATUS": ["SLO_BURN_TREND", "RISK_PREDICTION"]
  }
}
```

---

### Example 4: No Data Sources Available

**User Query:** `"Tell me a joke"` (Not a valid intent)

**Classification Process:**

1. **Intent Detection**
   - AWS Bedrock returns no matching intent or an unknown intent

2. **Enrichment**
   - No enrichment if intent doesn't exist

3. **Data Source Collection**
   - Unknown intent has no data sources
   - Final: "No relevant Data Source available"

**Result:**
```json
{
  "query": "Tell me a joke",
  "primary_intents": ["UNKNOWN"],
  "enriched_intents": ["UNKNOWN"],
  "data_sources": "No relevant Data Source available",
  "enrichment_details": {}
}
```

---

## Modification Guide

### Adding a New Intent

**Step 1: Add to intent_categories.yaml**

```yaml
CATEGORY_NAME:
  intents:
    NEW_INTENT_NAME:
      description: "What this intent does"
      examples:
        - "Example query 1"
        - "Example query 2"
      data_sources:
        - clickhouse
        - java_stats_api
```

**Step 2: (Optional) Add enrichment rules in enrichment_rules.yaml**

```yaml
NEW_INTENT_NAME:
  - RELATED_INTENT_1
  - RELATED_INTENT_2
```

**Step 3: Verify data sources in data_sources.yaml**

Ensure the data sources you specified (clickhouse, java_stats_api) have the necessary capabilities.

---

### Adding a New Enrichment Rule

**File:** enrichment_rules.yaml

```yaml
EXISTING_INTENT:
  - NEW_RELATED_INTENT
  - ANOTHER_RELATED_INTENT
```

**Considerations:**
- Does the enrichment add value to the primary intent?
- Will it help answer follow-up questions proactively?
- Does it create a circular dependency? (Avoid: A enriches B, B enriches A)
- Will it cause too many data sources to be queried? (Performance impact)

---

### Adding a New Data Source

**File:** data_sources.yaml

```yaml
data_sources:
  new_data_source:
    type: database
    description: "What it contains"
    capabilities:
      - capability_1
      - capability_2
    timeout: 30
    pool_size: 10

intent_data_sources:
  CATEGORY:
    - new_data_source
```

Then update relevant intents in **intent_categories.yaml** to use the new data source.

---

## Data Source Decision Matrix

| Query Type | Real-time needed? | Historical analysis? | Data Source |
|------------|-------------------|----------------------|-------------|
| Current health status | ✓ | ✗ | java_stats_api |
| Performance metrics now | ✓ | ✗ | java_stats_api |
| Trend analysis | ✗ | ✓ | clickhouse |
| Pattern detection | ✗ | ✓ | clickhouse |
| Root cause (recent) | ✓ | ✓ | Both |
| SLO status | ✗ | ✓ | clickhouse |
| Alert history | ✗ | ✓ | clickhouse |
| Incident timeline | ✗ | ✓ | clickhouse |
| Audit trail | ✗ | ✓ | clickhouse |
| Mitigation steps | ✗ | ✓ | clickhouse (AI memory) |

---

## Best Practices

### 1. Intent Design
- Keep intents specific and focused
- Provide 2-3 clear examples per intent
- Use descriptive names (e.g., ROOT_CAUSE_SINGLE vs just ROOT_CAUSE)

### 2. Enrichment Rules
- Only enrich when it adds value
- Avoid circular enrichments
- Limit enrichment depth (max 2 levels recommended)
- Consider query performance vs. comprehensiveness

### 3. Data Source Selection
- Use java_stats_api for real-time data
- Use clickhouse for historical, trend, and analytical queries
- Combine both when you need current state + historical context

### 4. Testing
After modifications:
```bash
python intent_classifier.py   # Interactive testing
python test_classifier.py      # Automated test suite
```

---

## Troubleshooting

### Issue: Intent not being detected

**Solution:**
1. Check examples in `intent_categories.yaml` - are they similar to your query?
2. Add more diverse examples
3. Verify the intent description is clear

### Issue: Too many data sources being returned

**Solution:**
1. Review enrichment rules - are they too aggressive?
2. Remove unnecessary enrichments
3. Check if intents are too broad

### Issue: "No relevant Data Source available"

**Solution:**
1. Check if the intent has data_sources defined in `intent_categories.yaml`
2. Verify the data source names match those in `data_sources.yaml`
3. Ensure the intent is properly categorized

---

## Summary

### Quick Reference

| File | Purpose | When to Modify |
|------|---------|----------------|
| **intent_categories.yaml** | Define intents and examples | Adding new intents, updating examples |
| **enrichment_rules.yaml** | Auto-expand intents | Creating intent relationships |
| **data_sources.yaml** | Define data sources | Adding new data sources, updating capabilities |

### Key Concepts

1. **Intent** = What the user wants to know
2. **Enrichment** = Related information to provide comprehensive answers
3. **Data Source** = Where to get the information

### Configuration Flow

```
intent_categories.yaml → enrichment_rules.yaml → data_sources.yaml → Final Result
     (Detection)              (Expansion)            (Execution)
```

---

**For more details, see:**
- `CLAUDE.md` - Development guide for working with this codebase
- `Understanding_Readme.md` - Deep technical implementation details
- `README.md` - Project overview and setup instructions
