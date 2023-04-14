from enum import Enum, unique


# system             1000 ~ 1099
# user               1100 ~ 1199
# data-source        1200 ~ 1299
# catalog            1300 ~ 1399
# template           1400 ~ 1499
# discovery-job      1500 ~ 1599
# query              1600 ~ 1699
@unique
class MessageEnum(Enum):
    # system
    BIZ_UNKNOWN_ERR = {1000: "An application error occurred and has been logged to CloudWatch Logs"}
    BIZ_DEFAULT_OK = {1001: "Operation succeeded"}
    BIZ_DEFAULT_ERR = {1002: "Operation failed"}
    BIZ_INVALID_TOKEN = {1003: "Invalid token"}
    BIZ_TIMEOUT_TOKEN = {1004: "Timeout token"}
    BIZ_ITEM_NOT_EXISTS = {1005: "The item does not exist"}

    # template
    BIZ_TEMPLATE_NOT_EXISTS = {1401: "The classification template does not exist"}
    BIZ_IDENTIFIER_NOT_EXISTS = {1402: "The data identifier does not exist"}
    BIZ_IDENTIFIER_EXISTS = {1403: "A data identifier with the same name already exists"}
    BIZ_IDENTIFIER_USED = {1404: "The data identifier is being used"}

    def get_code(self):
        return list(self.value.keys())[0]

    def get_msg(self):
        return list(self.value.values())[0]


@unique
class JobState(Enum):
    IDLE = "Active (idle)"
    RUNNING = "Active (running)"
    PAUSED = "Paused"
    OD_READY = "Ready"
    OD_RUNNING = "Running"
    OD_COMPLETED = "Completed"


@unique
class RunState(Enum):
    READY = "Ready"
    RUNNING = "Running"
    COMPLETED = "Completed"
    STOPPED = "Stopped"


@unique
class RunDatabaseState(Enum):
    READY = "Ready"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    STOPPED = "Stopped"
    NOT_EXIST = "NotExist"


@unique
class DatabaseType(Enum):
    RDS = "rds"
    S3 = "s3"


@unique
class CatalogState(Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DETECTED = "DETECTED"


@unique
class AthenaQueryState(Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@unique
class GlueCrawlerState(Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@unique
class GlueResourceNameSuffix(Enum):
    DATABASE = "database"
    CRAWLER = "crawler"


@unique
class Privacy(Enum):
    PII = 1
    NON_PII = 0
    NA = -1


@unique
class CatalogDashboardAttribute(Enum):
    REGION = 'region'
    PRIVACY = 'privacy'


@unique
class CatalogModifier(Enum):
    MANUAL = "Manual"
    SYSTEM = "System"


@unique
class ConnectionState(Enum):
    PENDING = "PENDING"
    CRAWLING = "CRAWLING"
    ACTIVE = "ACTIVE"
    UNSUPPORTED = "UNSUPPORTED FILE TYPES"
    ERROR = "ERROR"


@unique
class IdentifierDependency(Enum):
    TEMPLATE = "template"
    S3 = "s3"
