import django.dispatch


topic_viewed = django.dispatch.Signal(providing_args=["topic", "user", "request", "response", ])
