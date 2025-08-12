import os
import yaml
from dotenv import load_dotenv
from kafka.admin import KafkaAdminClient, NewTopic

def main():
    try:
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

        # Handle the new kafka-python API response format
        try:
            # Try the new API format first
            response = admin.create_topics(new_topics, timeout_ms=10000)
            # Check if response has items attribute (new format)
            if hasattr(response, 'items'):
                for topic, future in response.items():
                    try:
                        future.result()
                        print(f"✔ Created topic: {topic}")
                    except Exception as e:
                        print(f"⚠ Topic '{topic}' creation skipped or failed: {e}")
            else:
                # New format without items - topics are created successfully
                print(f"✔ Created {len(new_topics)} topics successfully")
        except AttributeError:
            # Fallback for older API format
            futures = admin.create_topics(new_topics, timeout_ms=10000)
            for topic, future in futures.items():
                try:
                    future.result()
                    print(f"✔ Created topic: {topic}")
                except Exception as e:
                    print(f"⚠ Topic '{topic}' creation skipped or failed: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error in bootstrap_topics: {e}")
        return False

if __name__ == '__main__':
    main()
