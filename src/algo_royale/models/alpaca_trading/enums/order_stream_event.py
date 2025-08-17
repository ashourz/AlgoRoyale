from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class EventDefinition:
    """
    Represents an event definition for the order stream.
    This is used to define the structure of events that will be published
    """

    value: str
    description: str


class OrderStreamEvent(str, Enum):
    """
    Enum for order stream events.
    This is used to identify different types of events in the order stream.

    Attributes:
        NEW: Event when an order is created.
        FILL: Event when an order is completely filled.
        PARTIAL_FILL: Event when an order is partially filled.
        CANCELED: Event when an order is canceled.
        EXPIRED: Event when an order expires.
        DONE_FOR_DAY: Event when an order is done for the day.
        REPLACED: Event when an order is replaced.
        REJECTED: Event when an order is rejected.
        PENDING_NEW: Event when an order is pending new.
        STOPPED: Event when an order is stopped.
        PENDING_CANCEL: Event when an order is pending cancel.
        PENDING_REPLACE: Event when an order is pending replace.
        CALCULATED: Event when an order is calculated.
        SUSPENDED: Event when an order is suspended.
        ORDER_REPLACE_REJECTED: Event when an order replace is rejected.
        ORDER_CANCEL_REJECTED: Event when an order cancel is rejected.
    """

    NEW = EventDefinition(
        "new", "Sent when an order has been routed to exchanges for execution."
    )
    FILL = EventDefinition("fill", "Sent when your order has been completely filled.")
    PARTIAL_FILL = EventDefinition(
        "partial_fill",
        "Sent when a number of shares less than the total remaining quantity on your order has been filled.",
    )
    CANCELED = EventDefinition(
        "canceled", "Sent when your requested cancelation of an order is processed."
    )
    EXPIRED = EventDefinition(
        "expired",
        "Sent when an order has reached the end of its lifespan, as determined by the order’s time in force value.",
    )
    DONE_FOR_DAY = EventDefinition(
        "done_for_day",
        "Sent when the order is done executing for the day, and will not receive further updates until the next trading day.",
    )
    REPLACED = EventDefinition(
        "replaced", "Sent when your requested replacement of an order is processed."
    )
    REJECTED = EventDefinition("rejected", "Sent when your order has been rejected.")
    PENDING_NEW = EventDefinition(
        "pending_new",
        "Sent when the order has been received by Alpaca and routed to the exchanges, but has not yet been accepted for execution.",
    )
    STOPPED = EventDefinition(
        "stopped",
        "Sent when your order has been stopped, and a trade is guaranteed for the order, usually at a stated price or better, but has not yet occurred.",
    )
    PENDING_CANCEL = EventDefinition(
        "pending_cancel",
        "Sent when the order is awaiting cancelation. Most cancelations will occur without the order entering this state.",
    )
    PENDING_REPLACE = EventDefinition(
        "pending_replace", "Sent when the order is awaiting replacement."
    )
    CALCULATED = EventDefinition(
        "calculated",
        "Sent when the order has been completed for the day - it is either “filled” or “done_for_day” - but remaining settlement calculations are still pending.",
    )
    SUSPENDED = EventDefinition(
        "suspended",
        "Sent when the order has been suspended and is not eligible for trading.",
    )
    ORDER_REPLACE_REJECTED = EventDefinition(
        "order_replace_rejected", "Sent when the order replace has been rejected."
    )
    ORDER_CANCEL_REJECTED = EventDefinition(
        "order_cancel_rejected", "Sent when the order cancel has been rejected."
    )

    def __str__(self):
        return self.value.value

    @property
    def description(self):
        return self.value.description

    @property
    def name(self):
        return self.value.value

    @classmethod
    def from_name(cls, name: str) -> "OrderStreamEvent":
        """
        Create an OrderStreamEvent from its name.

        Args:
            name (str): The name of the event.

        Returns:
            OrderStreamEvent: The corresponding OrderStreamEvent instance.
        """
        for event in cls:
            if event.name == name:
                return event
        raise ValueError(f"Unknown OrderStreamEvent: {name}")
