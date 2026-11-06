-- For each user question, what did the model decide to do first (tool call or direct answer)?
SELECT
  i.text AS user_question,
  o.part_type AS decision,
  o.tool_name,
  o.tool_args,
  LEFT(o.text, 80) AS answer_preview
FROM `advent-agents-0jzupg.agent_logs.messages` i
JOIN `advent-agents-0jzupg.agent_logs.messages` o USING (completion_id)
WHERE i.kind = 'inputs' AND i.role = 'user' AND i.part_type = 'text'
  AND o.kind = 'outputs';
