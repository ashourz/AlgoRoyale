class ColumnName(str):
    """Type-safe column name with metadata."""

    def __new__(cls, value: str, full_name: str = "", description: str = ""):
        obj = str.__new__(cls, value)
        obj.full_name = full_name or value
        obj.description = description or value
        return obj

    def __repr__(self):
        """Return a string representation of the column name."""
        return f"{str(self)}"

    @property
    def __doc__(self):
        # Show both full name and description for best clarity
        return f"{self.full_name}: {self.description}"
