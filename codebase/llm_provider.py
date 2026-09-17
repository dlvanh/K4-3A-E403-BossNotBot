"""
llm_provider.py — Interface chung cho LLM, để bot và eval không phụ thuộc vào một nhà cung cấp.

Chọn provider bằng biến môi trường (xem .env.example):
    LLM_PROVIDER=openai | nvidia | gemini | anthropic | ollama | fake
    LLM_MODEL=...      (tuỳ chọn, ghi đè model mặc định của preset)
    LLM_BASE_URL=...   (tuỳ chọn, ghi đè endpoint của preset)
    <KEY của provider> (OPENAI_API_KEY, NVIDIA_API_KEY, ... — hoặc LLM_API_KEY dùng chung)

Mọi provider thật ở đây đều đi qua endpoint tương thích OpenAI Chat Completions, nên chỉ cần
một adapter. Provider không tương thích thì viết class mới có hàm `complete()` cùng chữ ký.
Tên model mặc định thay đổi theo thời gian — kiểm tra lại trên trang của provider.
"""
import os
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from openai import AsyncOpenAI


@runtime_checkable
class LLMProvider(Protocol):
    name: str
    model: str

    async def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        """Gửi một prompt, trả về text. Lỗi mạng/API được raise ra ngoài để nơi gọi quyết định."""
        ...


class OpenAICompatibleProvider:
    def __init__(self, name: str, model: str, api_key: str, base_url: str | None = None,
                 token_param: str = "max_tokens", reasoning_effort: str | None = None):
        self.name = name
        self.model = model
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        # OpenAI dòng GPT-5 trở đi và o-series từ chối "max_tokens", bắt buộc "max_completion_tokens"
        self._token_param = token_param
        # Model reasoning tính cả token suy luận vào giới hạn output; "low"/"minimal" để rẻ và không bị cắt
        self._reasoning_effort = reasoning_effort
        # Metadata của lần gọi gần nhất — để eval/log ghi lại, không ảnh hưởng luồng bot
        self.last_usage: dict | None = None
        self.last_finish_reason: str | None = None

    async def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        self.last_usage = self.last_finish_reason = None
        extra = {"reasoning_effort": self._reasoning_effort} if self._reasoning_effort else {}
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **{self._token_param: max_tokens},
            **extra,
        )
        choice = response.choices[0]
        self.last_finish_reason = choice.finish_reason  # "length" = bị cắt vì hết max_tokens
        if response.usage:
            self.last_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        # Model reasoning (vd gpt-oss) có thể trả content rỗng nếu hết token khi đang suy luận
        return choice.message.content or ""


class FakeProvider:
    """Không gọi mạng: chép lại từng dòng dữ liệu thành gạch đầu dòng. Chỉ để thử luồng code/bộ chấm."""

    name = "fake"
    model = "echo"

    async def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        if "=== CÂU HỎI ===" in prompt:
            # Prompt hỏi-đáp: trích tin gần nhất trong lịch sử làm "câu trả lời"
            history = prompt.split("=== LỊCH SỬ TIN NHẮN ===")[1].split("=== CÂU HỎI ===")[0].strip().splitlines()
            return f"(fake) Tin gần nhất: {history[-1][:120]}" if history else "(fake) Mình không tìm thấy thông tin này trong các tin nhắn trước đó."
        # Prompt tóm tắt = hướng dẫn + dòng trống + "Tiêu đề:" + dữ liệu → chỉ chép phần dữ liệu
        _, _, data = prompt.partition("\n\n")
        lines = [l for l in data.splitlines()[1:] if l.strip() and not l.startswith("===")]
        return "\n".join(f"- {l}" for l in lines)


@dataclass(frozen=True)
class Preset:
    base_url: str | None
    model: str
    key_env: str | None  # None = không cần key (vd Ollama chạy local)
    token_param: str = "max_tokens"


PRESETS = {
    "openai": Preset(None, "gpt-4o-mini", "OPENAI_API_KEY", "max_completion_tokens"),
    "nvidia": Preset("https://integrate.api.nvidia.com/v1", "openai/gpt-oss-120b", "NVIDIA_API_KEY"),
    "gemini": Preset("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-3.8-flash", "GEMINI_API_KEY"),
    "anthropic": Preset("https://api.anthropic.com/v1/", "claude-haiku-4-5", "ANTHROPIC_API_KEY"),
    "ollama": Preset("http://localhost:11434/v1", "qwen2.5:7b", None),
}


def create_provider(name: str | None = None) -> LLMProvider:
    """Tạo provider theo tên (hoặc LLM_PROVIDER, mặc định openai). Raise ValueError nếu cấu hình thiếu."""
    name = (name or os.getenv("LLM_PROVIDER") or "openai").strip().lower()
    if name == "fake":
        return FakeProvider()
    if name not in PRESETS:
        raise ValueError(f"LLM_PROVIDER '{name}' không hỗ trợ. Chọn một trong: {', '.join([*PRESETS, 'fake'])}")

    preset = PRESETS[name]
    if preset.key_env is None:
        api_key = os.getenv("LLM_API_KEY") or "not-needed"
    else:
        api_key = os.getenv(preset.key_env) or os.getenv("LLM_API_KEY")
        if not api_key:
            raise ValueError(f"Thiếu {preset.key_env} (hoặc LLM_API_KEY) trong .env cho provider '{name}'")

    return OpenAICompatibleProvider(
        name=name,
        model=os.getenv("LLM_MODEL") or preset.model,
        api_key=api_key,
        base_url=os.getenv("LLM_BASE_URL") or preset.base_url,
        token_param=preset.token_param,
        reasoning_effort=os.getenv("LLM_REASONING_EFFORT") or None,
    )
