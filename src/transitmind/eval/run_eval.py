import structlog
from transitmind.api.main import agent_loop
from transitmind.eval.test_questions import test_questions

logger = structlog.get_logger(__name__)

for tq in test_questions:
    response = agent_loop(tq["question"])
    logger.info("evals_tool_calls", question=tq["question"], tool_calls=response["tools"])
    break

