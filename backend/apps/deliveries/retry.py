from django.utils import timezone


class RetryPolicy:
    def should_retry(self, attempt_count: int, max_retries: int) -> bool:
        return attempt_count <= max_retries

    def calculate_delay_seconds(self, base_seconds: int, attempt_number: int):
        return base_seconds * (2 ** (attempt_number - 1))
        
    def calculate_next_retry_at(self, delay_seconds: int):
        return timezone.now() + timezone.timedelta(seconds=delay_seconds)