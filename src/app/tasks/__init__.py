# from dotenv import load_dotenv
# from taskiq_redis import RedisStreamBroker, RedisAsyncResultBackend
#
# load_dotenv(dotenv_path='../.env', encoding='utf-8')
#
# from app.core.settings import settings
#
# broker = RedisStreamBroker(
#     url=settings.redis_task_url
# ).with_result_backend(
#     RedisAsyncResultBackend(redis_url=settings.redis_task_url)
# )