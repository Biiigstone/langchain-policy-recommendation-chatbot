
"""
메모리 관리 클래스 및 함수
"""
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from config import MEMORY_K
from pydantic import Field

class WindowedInMemoryHistory(InMemoryChatMessageHistory):
    k: int = 2
    """최근 k개의 상호작용만 저장하는 인메모리 기록 클래스"""

    def __init__(self, k: int = 2):
        super().__init__()
        self.k = MEMORY_K

    def add_messages(self, messages: list) -> None:
        """메시지를 추가하고, 한도를 초과하면 가장 오래된 메시지를 제거합니다."""
        super().add_messages(messages)
        # k개의 상호작용은 2*k개의 메시지입니다 (질문 1 + 답변 1)
        if len(self.messages) > self.k * 2:
            self.messages = self.messages[-(self.k * 2):]


store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """세션 ID에 해당하는 Windowed Memory를 가져오거나 새로 생성합니다."""
    if session_id not in store:
        store[session_id] = WindowedInMemoryHistory(k=MEMORY_K)
    return store[session_id]