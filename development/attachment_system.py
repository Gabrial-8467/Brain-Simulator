# development/attachment_system.py

class AttachmentSystem:

    def __init__(self):
        self.attachments = {}

    # -----------------------------------------
    # ATTACHMENT UPDATES
    # -----------------------------------------

    def update(self, source: str, reward: float, stress: float) -> None:
        """
        Update the social attachment value based on reward and stress signals.
        
        Formula:
            Attachment <- Attachment + 0.01 * Reward - 0.01 * Stress
        Bounded to [-1.0, 1.0].
        """
        attachment = self.attachments.get(source, 0.0)
        attachment += 0.01 * reward - 0.01 * stress
        self.attachments[source] = max(-1.0, min(1.0, attachment))

    # -----------------------------------------
    # ATTACHMENT RETRIEVAL
    # -----------------------------------------

    def get_attachment(self, source: str) -> float:
        """Get the current attachment bonding level with a given source."""
        return self.attachments.get(source, 0.0)

    # -----------------------------------------
    # HOMEOSTATIC DECAY
    # -----------------------------------------

    def decay(self) -> None:
        """
        Decay social bonding levels slowly toward zero over time.
        
        Formula:
            Attachment <- Attachment * (1.0 - 0.0003) per simulation tick.
        """
        for source in self.attachments:
            self.attachments[source] *= (1.0 - 0.0003)
