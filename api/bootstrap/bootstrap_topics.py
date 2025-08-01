import os
import yaml
from dotenv import load_dotenv
from kafka.admin import KafkaAdminClient, NewTopic

load_dotenv()

bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
config_file = os.getenv('KAFKA_TOPIC_CONFIG_FILE', 'topics.yaml')
default_parts = int(os.getenv('KAFKA_DEFAULT_PARTITIONS', 1))
default_repl = int(os.getenv('KAFKA_DEFAULT_REPLICATION', 1))

with open(config_file, 'r') as f:
    topics_cfg = yaml.safe_load(f).get('topics', [])

admin = KafkaAdminClient(
    bootstrap_servers=bootstrap_servers,
    client_id='topic-bootstrapper'
)

new_topics = []
for t in topics_cfg:
    name = t['name']
    parts = t.get('partitions', default_parts)
    repl = t.get('replication', default_repl)
    new_topics.append(NewTopic(name, num_partitions=parts, replication_factor=repl))

futures = admin.create_topics(new_topics, timeout_ms=10000)
for topic, future in futures.items():
    try:
        future.result()
        print(f"✔ Created topic: {topic}")
    except Exception as e:
        print(f"⚠ Topic '{topic}' creation skipped or failed: {e}")
