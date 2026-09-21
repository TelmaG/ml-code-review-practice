# PR: Real-time rolling features

Context: Events arrive 100k/sec with up to 20 minutes of lateness. Features are windowed by event time and must not include future events. State must survive restarts.