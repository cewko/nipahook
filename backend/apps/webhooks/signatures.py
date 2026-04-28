import hashlib
import hmac
from datetime import timedelta

from django.utils import timezone

from apps.destinations.models import Destination
from .exceptions import SignatureVerificationError


class GenericHMACSHA256Verifier:
    timestamp_header = "X-Webhook-Timestamp"
    signature_header = "X-Webhook-Signature"
    tolerance = timedelta(minutes=5)

    def verify(
        self, 
        *, 
        headers: dict, 
        raw_body: bytes,
        key: str
    ) -> None:
        timestamp = headers.get(self.timestamp_header)
        signature = headers.get(self.signature_header)

        if not timestamp:
            raise SignatureVerificationError("Missing timestamp")

        if not signature:
            raise SignatureVerificationError("Missing signature")

        timestamp_seconds = self._parse_timestamp(timestamp)
        self._validate_timestamp(timestamp_seconds)

        expected_signature = self._build_signature(
            key=key,
            timestamp=timestamp,
            raw_body=raw_body
        )

        if not hmac.compare_digest(signature, expected_signature):
            raise SignatureVerificationError("Invalid signature")

    def _parse_timestamp(self, timestamp: str) -> int:
        try:
            return int(timestamp)
        except ValueError as _e:
            raise SignatureVerificationError("Invalid timestamp")

    def _validate_timestamp(self, timestamp_seconds: int) -> None:
        signed_at = timezone.datetime.fromtimestamp(
            timestamp_seconds,
            tz=timezone.get_current_timezone(),
        )

        now = timezone.now()
        if abs(now - signed_at) > self.tolerance:
            raise SignatureVerificationError("Timestamp is outside tolerance")

    def _build_signature(
        self,
        *,
        key: str,
        timestamp: str,
        raw_body: bytes
    ) -> str:
        digest = hmac.new(
            key=key.encode(),
            msg=timestamp.encode() + b"." + raw_body,
            digestmod=hashlib.sha256
        ).hexdigest()

        return f"sha256={digest}"

def verify_incoming_signature(
    *,
    destination: Destination,
    headers: dict,
    raw_body: bytes
) -> None:
    if destination.signature_verification_mode == Destination.SignatureVerificationMode.NONE:
        return

    if destination.signature_verification_mode == Destination.SignatureVerificationMode.GENERIC_HMAC_SHA256:
        if not destination.incoming_signature_key:
            raise SignatureVerificationError("Incoming signature key isn't provided")
    
        GenericHMACSHA256Verifier().verify(
            headers=headers,
            raw_body=raw_body,
            key=destination.incoming_signature_key
        )

        return

    raise SignatureVerificationError("Unsupported signature verification mode")