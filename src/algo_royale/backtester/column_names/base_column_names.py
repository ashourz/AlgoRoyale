from algo_royale.backtester.column_names.column_name import ColumnName


class BaseColumnNames:
    """Base class for defining column names used in the algorithmic trading framework."""

    @classmethod
    def _get_all_column_objects(cls) -> list[ColumnName]:
        """
        Returns a list of all ColumnName instances defined in a BaseColumnNames subclass.
        """
        return [
            getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith("__") and isinstance(getattr(cls, attr), ColumnName)
        ]

    @classmethod
    def get_all_column_values(cls) -> list[str]:
        """
        Returns a list of string values from a BaseColumnNames subclass.
        """
        return [str(col) for col in cls._get_all_column_objects()]
