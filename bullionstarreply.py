
from dataclasses import dataclass
from datetime import date, datetime

class BullionStarReply:
    def __init__(self, **kwargs):
        self.status: str = kwargs.get("status", "")
        self.title: str = kwargs.get("title", "")
        self.message: str = kwargs.get("message", "")
        self.spotPrices: list[dict] = kwargs.get("spotPrices", [])
        self.lastUpdateDate: date | None = kwargs.get("lastUpdateDate")
        self.startDate: date = datetime.fromtimestamp(kwargs.get("startDate", 0) / 1000).date()
        self.endDate: date = datetime.fromtimestamp(kwargs.get("endDate", 0) / 1000).date()
        self.fromIndex: str = kwargs.get("fromIndex", "")
        self.toIndex: str = kwargs.get("toIndex", "")
        self.numDecimals: int = kwargs.get("numDecimals", 0)
        self.hasTime: bool = kwargs.get("hasTime", False)
        self.timeToNextUpdate: int = kwargs.get("timeToNextUpdate", 0)
        
        # error flags
        self.error: bool = kwargs.get("error", False)
        self.accessDenied: bool = kwargs.get("accessDenied", False)
        self.authenticationRequired: bool = kwargs.get("authenticationRequired", False)
        self.warning: bool = kwargs.get("warning", False)
        self.success: bool = kwargs.get("success", False)
        
        self.startDateString: str = kwargs.get("startDateString", "")
        self.endDateString: str = kwargs.get("endDateString", "")
        
        self.dataSeries: list[dict] = kwargs.get("dataSeries", [])

        self.assert_error_flags()
        self.assert_start_end_dates()
    # 'dataSeries': [{'d': 0, 'v': 5.1706}, {'d': 6048, 'v': 5.0286}, {'d': 12096, 'v': 5.0734}

    def assert_error_flags(self):
        assert self.error == False, "Error flag is set"
        assert self.accessDenied == False, "Access Denied flag is set"
        assert self.authenticationRequired == False, "Authentication Required flag is set"
        assert self.warning == False, "Warning flag is set"
        assert self.success == True, "Success flag is not set"

    def assert_start_end_dates(self):
        assert isinstance(self.startDate, date), "startDate is not a date"
        assert isinstance(self.endDate, date), "endDate is not a date"
        assert self.startDate.strftime("%d-%m-%Y") == self.startDateString, "startDateString does not match startDate"
        assert self.endDate.strftime("%d-%m-%Y") == self.endDateString, "endDateString does not match endDate"


