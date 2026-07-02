from .schemas import SummarizePromptInput, SummarizePromptOutput
from .types import PromptTemplate

SUMMARIZE_V1 = PromptTemplate(
    name="summarize",
    version="v1",
    system_prompt_key="creatoros_writer_v1",
    user_prompt_template=(
        "Summarize this content for audience '{audience}'. "
        "Return JSON with keys: summary (string), key_points (array of strings). "
        "Content:\n{text}"
    ),
    input_schema=SummarizePromptInput,
    output_schema=SummarizePromptOutput,
    temperature=0.2,
)
