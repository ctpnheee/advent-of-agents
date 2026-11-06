-- Which tools does the model call, and how often?
SELECT tool_name, COUNT(*) AS calls
FROM `advent-agents-0jzupg.agent_logs.messages`
WHERE kind = 'outputs' AND part_type = 'tool_call'
GROUP BY tool_name
ORDER BY calls DESC;
