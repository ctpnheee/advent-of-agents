-- One row per message part, parsed from the raw JSONL lines written by the agent's telemetry.
CREATE OR REPLACE VIEW `advent-agents-0jzupg.agent_logs.messages` AS
SELECT
  REGEXP_EXTRACT(_FILE_NAME, r'completions/(.+)_(?:inputs|outputs|system_instruction|tool\.definitions)\.jsonl$') AS completion_id,
  REGEXP_EXTRACT(_FILE_NAME, r'_(inputs|outputs|system_instruction|tool\.definitions)\.jsonl$') AS kind,
  JSON_VALUE(line, '$.role') AS role,
  JSON_VALUE(line, '$.finish_reason') AS finish_reason,
  JSON_VALUE(part, '$.type') AS part_type,
  JSON_VALUE(part, '$.content') AS text,
  JSON_VALUE(part, '$.name') AS tool_name,
  JSON_QUERY(part, '$.arguments') AS tool_args
FROM `advent-agents-0jzupg.agent_logs.raw_lines`,
  UNNEST(IFNULL(JSON_QUERY_ARRAY(line, '$.parts'), ['{}'])) AS part;  -- lines without parts (instructions) keep one row
