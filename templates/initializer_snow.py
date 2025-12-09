"""
Snowflake ID 生成器初始化
"""

import threading
import time


class SnowFlake:
    """
    Snowflake ID 生成器

    生成全局唯一的分布式ID
    """

    # 起始时间戳 (2020-01-01 00:00:00)
    EPOCH: int = 1577836800000

    # 各部分位数
    WORKER_ID_BITS: int = 5
    DATACENTER_ID_BITS: int = 5
    SEQUENCE_BITS: int = 12

    # 最大值
    MAX_WORKER_ID: int = -1 ^ (-1 << WORKER_ID_BITS)
    MAX_DATACENTER_ID: int = -1 ^ (-1 << DATACENTER_ID_BITS)
    MAX_SEQUENCE: int = -1 ^ (-1 << SEQUENCE_BITS)

    # 位移
    WORKER_ID_SHIFT: int = SEQUENCE_BITS
    DATACENTER_ID_SHIFT: int = SEQUENCE_BITS + WORKER_ID_BITS
    TIMESTAMP_SHIFT: int = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

    worker_id: int
    datacenter_id: int
    sequence: int
    last_timestamp: int
    _lock: threading.Lock

    def __init__(self, worker_id: int = 1, datacenter_id: int = 1):
        """
        初始化 Snowflake ID 生成器

        Args:
            worker_id: 工作机器ID (0-31)
            datacenter_id: 数据中心ID (0-31)
        """
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"worker_id 必须在 0 到 {self.MAX_WORKER_ID} 之间")
        if datacenter_id > self.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(f"datacenter_id 必须在 0 到 {self.MAX_DATACENTER_ID} 之间")

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = -1
        self._lock = threading.Lock()

    def _current_timestamp(self) -> int:
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp: int) -> int:
        """等待下一毫秒"""
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

    def generate_id(self) -> int:
        """生成唯一ID"""
        with self._lock:
            timestamp = self._current_timestamp()

            if timestamp < self.last_timestamp:
                raise RuntimeError("时钟回拨，无法生成ID")

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            snowflake_id = (
                ((timestamp - self.EPOCH) << self.TIMESTAMP_SHIFT)
                | (self.datacenter_id << self.DATACENTER_ID_SHIFT)
                | (self.worker_id << self.WORKER_ID_SHIFT)
                | self.sequence
            )

            return snowflake_id

    def generate_id_str(self) -> str:
        """生成唯一ID（字符串格式）"""
        return str(self.generate_id())


def init_snow_client(
    worker_id: int | None = None,
    datacenter_id: int | None = None,
) -> SnowFlake:
    """
    初始化 Snowflake ID 生成器

    Args:
        worker_id: 工作机器ID，默认为 1
        datacenter_id: 数据中心ID，默认为 1

    Returns:
        SnowFlake实例
    """
    # 使用默认值处理 None
    actual_worker_id = worker_id if worker_id is not None else 1
    actual_datacenter_id = datacenter_id if datacenter_id is not None else 1
    return SnowFlake(worker_id=actual_worker_id, datacenter_id=actual_datacenter_id)
