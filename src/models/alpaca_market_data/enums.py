
from enum import Enum


class CorporateActionType(Enum):
    DIVIDEND = "Dividend"
    MERGER = "Merger"
    SPINOFF = "Spinoff"
    SPLIT = "Split"

class CorporateActionDateType(Enum):
    DECLARATION_DATE = "declaration_date"
    EX_DATE = "ex_date"
    RECORD_DATE = "record_date"
    PAYABLE_DATE = "payable_date"

class CorporateActions(Enum):
    """
    Enum for different types of corporate actions.
    These can be used to categorize or filter corporate actions when fetching data.

    Types:   
    - REVERSE_SPLIT: Represents a reverse stock split.
    - FORWARD_SPLIT: Represents a forward stock split.
    - UNIT_SPLIT: Represents a unit stock split.
    - CASH_DIVIDEND: Represents a cash dividend.
    - STOCK_DIVIDEND: Represents a stock dividend.
    - SPIN_OFF: Represents a spin-off of a company.
    - CASH_MERGER: Represents a cash merger.
    - STOCK_MERGER: Represents a stock merger.
    - STOCK_CASH_MERGER: Represents a stock and cash merger.
    - REDEMPTION: Represents a redemption of shares.
    - NAME_CHANGE: Represents a name change of a company.
    - WORTHLESS_REMOVAL: Represents the removal of worthless shares.
    - RIGHTS_DISTRIBUTION: Represents a rights distribution.
    """
    
    REVERSE_SPLIT = "reverse_split"
    FORWARD_SPLIT = "forward_split"
    UNIT_SPLIT = "unit_split"
    CASH_DIVIDEND = "cash_dividend"
    STOCK_DIVIDEND = "stock_dividend"
    SPIN_OFF = "spin_off"
    CASH_MERGER = "cash_merger"
    STOCK_MERGER = "stock_merger"
    STOCK_CASH_MERGER = "stock_and_cash_merger"
    REDEMPTION = "redemption"
    NAME_CHANGE = "name_change"
    WORTHLESS_REMOVAL = "worthless_removal"
    RIGHTS_DISTRIBUTION = "rights_distribution"