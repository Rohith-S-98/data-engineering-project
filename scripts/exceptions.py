class PipelineError(Exception):
    """Base exception for pipeline-related errors."""


class PipelineConfigError(PipelineError):
    """Raised when pipeline configuration is invalid."""


class DataIngestionError(PipelineError):
    """Raised when ingestion fails."""


class DQValidationError(PipelineError):
    """Raised when data quality validation must stop the pipeline."""


class PipelineExecutionError(PipelineError):
    """Raised when the full pipeline execution fails."""
