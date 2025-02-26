import tools.performance_tracker as tracker

class FeedbackAgent:
    def track_performance(self):
        print("Tracking performance of past recommendations...")
        tracker.analyze_past_trades()
