import asyncio
import os
from redis.asyncio import Redis
from redisvl.index import AsyncSearchIndex
from redisvl.schema.schema import IndexSchema
from dotenv import load_dotenv

load_dotenv()

async def create_ltm_index():
    # Use environment variables
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_url = f"redis://{redis_host}:{redis_port}"
    
    redis_client = Redis.from_url(redis_url)
    
    # Load schema from YAML
    schema_path = os.path.join(os.path.dirname(__file__), "redis_ltm_schema.yaml")
    memory_schema = IndexSchema.from_yaml(schema_path)
    
    try:
        index = AsyncSearchIndex(
            schema=memory_schema,
            redis_client=redis_client,
        )
        
        await index.create(overwrite=True, drop=True)
        print(f"Index '{memory_schema.index.name}' successfully created in Redis.")
        
    except Exception as e:
        print(f"Error creating index: {e}")
    finally:
        await redis_client.aclose()

if __name__ == "__main__":
    asyncio.run(create_ltm_index())
