from rest_framework.throttling import AnonRateThrottle


class BurstRateThrottle(AnonRateThrottle):
    scope = "anon_burst"


class SustainedRateThrottle(AnonRateThrottle):
    scope = "anon_sustained"
