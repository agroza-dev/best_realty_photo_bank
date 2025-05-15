import asyncio
import time

from telegram.error import TimedOut

from utils.logger import logger


async def do_with_retry(func, *args, retries=3, delay=2, label='unknown', **kwargs):

    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            processed = time.perf_counter() - start_time
            logger.info(f"[{label}] Processed in {processed:.2f} seconds (attempt {attempt})")
            return result
        except TimedOut as e:
            logger.warning(f"[{label}] Timed out on attempt {attempt} — retrying in {delay} sec...")
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                logger.error(f"[{label}] Failed to resolve after {retries} attempts.")
                raise e
        except Exception as e:
            logger.error(f"[{label}] Неизвестное исключение {e}.")
            last_exception = e
            break

    # Пробрасываем последнее исключение
    if last_exception:
        raise last_exception