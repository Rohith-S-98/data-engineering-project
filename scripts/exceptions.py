class PipelineError(Exception):
    """Base exception for pipeline-related errors."""


class PipelineConfigError(PipelineError):
    """Raised when pipeline configuration is invalid."""


class DataIngestionError(PipelineError):
    """Raised when data ingestion fails."""


class DQValidationError(PipelineError):
    """Raised when data quality validation fails."""


class PipelineExecutionError(PipelineError):
    """Raised when pipeline execution fails."""