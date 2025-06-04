# State Management Tutorial

Learn how to design and manage state effectively in Agent Playground workflows. This tutorial covers state design patterns, validation strategies, and best practices for maintaining data integrity throughout complex multi-agent processes.

## Understanding State

State is the data structure that flows through your workflow, carrying information between agents. It's the primary mechanism for:

- **Data Transfer**: Moving data between agents
- **Process Tracking**: Recording execution progress
- **Error Handling**: Capturing and managing errors
- **Result Accumulation**: Collecting outputs from multiple agents

## Basic State Design

### Simple State Classes

Start with basic state classes that extend `BaseState`:

```python
from agent_playground.core import BaseState
from typing import Dict, Any, List, Optional

class DocumentProcessingState(BaseState):
    """State for document processing workflows."""
    
    # Input data
    document_path: str = ""
    document_type: str = ""
    
    # Processing results
    extracted_text: str = ""
    word_count: int = 0
    
    # Status tracking
    processing_complete: bool = False
    processing_time: float = 0.0
```

### Rich State Classes

For complex workflows, design comprehensive state classes:

```python
from pydantic import Field, validator
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

class ProcessingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class CustomerAnalysisState(BaseState):
    """Comprehensive state for customer analysis workflows."""
    
    # Customer information
    customer_id: str = Field(..., description="Unique customer identifier")
    customer_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing configuration
    analysis_types: List[str] = Field(default_factory=list)
    include_recommendations: bool = True
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    
    # Processing status
    status: ProcessingStatus = ProcessingStatus.PENDING
    current_step: str = ""
    steps_completed: List[str] = Field(default_factory=list)
    
    # Analysis results
    demographics: Optional[Dict[str, Any]] = None
    behavior_patterns: Optional[Dict[str, Any]] = None
    sentiment_scores: Optional[Dict[str, float]] = None
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Quality metrics
    data_quality_score: float = 0.0
    analysis_confidence: float = 0.0
    
    # Timestamps
    analysis_started_at: Optional[datetime] = None
    analysis_completed_at: Optional[datetime] = None
    
    @validator('customer_id')
    def validate_customer_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Customer ID must be at least 3 characters')
        return v
    
    @validator('analysis_types')
    def validate_analysis_types(cls, v):
        valid_types = ['demographic', 'behavioral', 'sentiment', 'predictive']
        invalid_types = [t for t in v if t not in valid_types]
        if invalid_types:
            raise ValueError(f'Invalid analysis types: {invalid_types}')
        return v
```

## State Design Patterns

### Modular State Design

Break complex state into logical modules:

```python
from pydantic import BaseModel
from typing import Optional

# Separate models for different aspects
class CustomerProfile(BaseModel):
    """Customer profile information."""
    customer_id: str
    name: str
    email: str
    registration_date: datetime
    tier: str = "standard"

class TransactionHistory(BaseModel):
    """Customer transaction history."""
    total_transactions: int = 0
    total_amount: float = 0.0
    avg_transaction_amount: float = 0.0
    last_transaction_date: Optional[datetime] = None
    transaction_frequency: str = "low"

class EngagementMetrics(BaseModel):
    """Customer engagement metrics."""
    email_open_rate: float = 0.0
    click_through_rate: float = 0.0
    support_tickets: int = 0
    satisfaction_score: float = 0.0

class CustomerInsightsState(BaseState):
    """Modular state using composed models."""
    
    # Core components
    profile: Optional[CustomerProfile] = None
    transactions: Optional[TransactionHistory] = None
    engagement: Optional[EngagementMetrics] = None
    
    # Analysis results
    customer_segment: str = ""
    churn_risk: float = 0.0
    lifetime_value: float = 0.0
    
    # Processing metadata
    analysis_version: str = "1.0"
    data_sources: List[str] = Field(default_factory=list)
```

### Hierarchical State Design

For complex workflows with sub-processes:

```python
class SubProcessState(BaseModel):
    """State for a sub-process within a larger workflow."""
    name: str
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)

class DocumentAnalysisState(BaseState):
    """Hierarchical state for document analysis workflow."""
    
    # Document information
    document_id: str
    document_path: str
    document_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Sub-process states
    text_extraction: SubProcessState = Field(
        default_factory=lambda: SubProcessState(name="text_extraction")
    )
    content_analysis: SubProcessState = Field(
        default_factory=lambda: SubProcessState(name="content_analysis")
    )
    sentiment_analysis: SubProcessState = Field(
        default_factory=lambda: SubProcessState(name="sentiment_analysis")
    )
    classification: SubProcessState = Field(
        default_factory=lambda: SubProcessState(name="classification")
    )
    
    # Final results
    final_report: Optional[Dict[str, Any]] = None
    overall_confidence: float = 0.0
    
    def get_subprocess_by_name(self, name: str) -> Optional[SubProcessState]:
        """Get a sub-process state by name."""
        return getattr(self, name, None)
    
    def mark_subprocess_complete(self, name: str, results: Dict[str, Any]):
        """Mark a sub-process as complete with results."""
        subprocess = self.get_subprocess_by_name(name)
        if subprocess:
            subprocess.status = "completed"
            subprocess.completed_at = datetime.utcnow()
            subprocess.results = results
    
    def get_completed_subprocesses(self) -> List[str]:
        """Get list of completed sub-process names."""
        completed = []
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, SubProcessState):
                if field_value.status == "completed":
                    completed.append(field_name)
        return completed
```

### Dynamic State Design

For workflows that need flexible state structures:

```python
class DynamicWorkflowState(BaseState):
    """State that can adapt its structure based on workflow needs."""
    
    # Core static fields
    workflow_id: str
    workflow_type: str
    
    # Dynamic data storage
    dynamic_data: Dict[str, Any] = Field(default_factory=dict)
    computed_fields: Dict[str, Any] = Field(default_factory=dict)
    
    # Processing metadata
    processing_steps: List[str] = Field(default_factory=list)
    available_computations: List[str] = Field(default_factory=list)
    
    def set_dynamic_field(self, key: str, value: Any, field_type: str = "data"):
        """Set a dynamic field value."""
        if field_type == "data":
            self.dynamic_data[key] = value
        elif field_type == "computed":
            self.computed_fields[key] = value
        else:
            raise ValueError(f"Invalid field type: {field_type}")
    
    def get_dynamic_field(self, key: str, default: Any = None) -> Any:
        """Get a dynamic field value."""
        # Check computed fields first, then data fields
        return self.computed_fields.get(key, self.dynamic_data.get(key, default))
    
    def has_dynamic_field(self, key: str) -> bool:
        """Check if a dynamic field exists."""
        return key in self.dynamic_data or key in self.computed_fields
    
    def add_computation_result(self, computation_name: str, result: Any):
        """Add a computation result to the state."""
        self.computed_fields[computation_name] = result
        if computation_name not in self.available_computations:
            self.available_computations.append(computation_name)
    
    def require_fields(self, *field_names: str) -> bool:
        """Check if all required fields are present."""
        return all(self.has_dynamic_field(field) for field in field_names)
```

## State Validation

### Schema Validation with Pydantic

Use Pydantic validators for robust state validation:

```python
from pydantic import validator, root_validator
from typing import List, Dict
import re

class ValidatedProcessingState(BaseState):
    """State with comprehensive validation."""
    
    # Email validation
    email: str = Field(..., description="Customer email address")
    
    # Numeric constraints
    age: int = Field(..., ge=0, le=150, description="Customer age")
    income: float = Field(..., ge=0, description="Annual income")
    score: float = Field(..., ge=0.0, le=1.0, description="Quality score")
    
    # String constraints
    phone: str = Field(..., min_length=10, max_length=15)
    country_code: str = Field(..., min_length=2, max_length=3)
    
    # List constraints
    tags: List[str] = Field(..., min_items=1, max_items=10)
    
    # Custom validations
    @validator('email')
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('phone')
    def validate_phone(cls, v):
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return digits_only
    
    @validator('tags')
    def validate_tags(cls, v):
        # Ensure tags are unique and lowercase
        unique_tags = list(set(tag.lower().strip() for tag in v))
        if len(unique_tags) != len(v):
            raise ValueError('Duplicate tags are not allowed')
        return unique_tags
    
    @root_validator
    def validate_income_age_relationship(cls, values):
        """Validate logical relationships between fields."""
        age = values.get('age')
        income = values.get('income')
        
        if age and income:
            if age < 18 and income > 50000:
                raise ValueError('Income seems unusually high for age under 18')
        
        return values
```

### Business Logic Validation

Implement domain-specific validation:

```python
class BusinessValidatedState(BaseState):
    """State with business logic validation."""
    
    # Financial data
    account_balance: float = 0.0
    credit_limit: float = 0.0
    monthly_income: float = 0.0
    debt_to_income_ratio: float = 0.0
    
    # Risk assessment
    risk_category: str = ""
    approval_status: str = "pending"
    
    @validator('debt_to_income_ratio', always=True)
    def calculate_debt_to_income(cls, v, values):
        """Auto-calculate debt-to-income ratio."""
        monthly_income = values.get('monthly_income', 0)
        if monthly_income > 0:
            # This would come from actual debt calculation
            estimated_debt = values.get('estimated_monthly_debt', 0)
            return estimated_debt / monthly_income
        return 0.0
    
    @validator('risk_category', always=True)
    def determine_risk_category(cls, v, values):
        """Auto-determine risk category based on financial metrics."""
        debt_ratio = values.get('debt_to_income_ratio', 0)
        account_balance = values.get('account_balance', 0)
        
        if debt_ratio > 0.4 or account_balance < 1000:
            return "high_risk"
        elif debt_ratio > 0.25 or account_balance < 5000:
            return "medium_risk"
        else:
            return "low_risk"
    
    @root_validator
    def validate_business_rules(cls, values):
        """Validate business rules across multiple fields."""
        risk_category = values.get('risk_category')
        credit_limit = values.get('credit_limit', 0)
        monthly_income = values.get('monthly_income', 0)
        
        # Business rule: Credit limit should not exceed 3x monthly income
        if monthly_income > 0 and credit_limit > (monthly_income * 3):
            raise ValueError('Credit limit exceeds 3x monthly income policy')
        
        # Business rule: High-risk customers get lower credit limits
        if risk_category == "high_risk" and credit_limit > 5000:
            raise ValueError('High-risk customers cannot have credit limit > $5000')
        
        return values
```

### Runtime Validation

Implement validation that occurs during workflow execution:

```python
class RuntimeValidatedState(BaseState):
    """State with runtime validation capabilities."""
    
    data_quality_checks: Dict[str, bool] = Field(default_factory=dict)
    validation_results: Dict[str, Any] = Field(default_factory=dict)
    validation_passed: bool = True
    
    def validate_data_quality(self, field_name: str, value: Any) -> bool:
        """Validate data quality for a specific field."""
        validators = {
            'completeness': lambda v: v is not None and str(v).strip() != '',
            'uniqueness': lambda v: self._check_uniqueness(field_name, v),
            'consistency': lambda v: self._check_consistency(field_name, v),
            'accuracy': lambda v: self._check_accuracy(field_name, v)
        }
        
        results = {}
        overall_passed = True
        
        for check_name, validator_func in validators.items():
            try:
                passed = validator_func(value)
                results[check_name] = passed
                if not passed:
                    overall_passed = False
            except Exception as e:
                results[check_name] = False
                results[f'{check_name}_error'] = str(e)
                overall_passed = False
        
        # Store results
        self.data_quality_checks[field_name] = overall_passed
        self.validation_results[field_name] = results
        
        # Update overall validation status
        self.validation_passed = all(self.data_quality_checks.values())
        
        return overall_passed
    
    def _check_uniqueness(self, field_name: str, value: Any) -> bool:
        """Check if value is unique (placeholder for actual implementation)."""
        # In real implementation, this would check against a database or cache
        return True
    
    def _check_consistency(self, field_name: str, value: Any) -> bool:
        """Check if value is consistent with related fields."""
        # Example: Check if city matches state/country
        if field_name == 'city':
            state = getattr(self, 'state', None)
            if state and value:
                # Placeholder for city-state validation logic
                return self._validate_city_state_combination(value, state)
        return True
    
    def _check_accuracy(self, field_name: str, value: Any) -> bool:
        """Check if value appears accurate."""
        # Example: Check if email domain exists
        if field_name == 'email' and value:
            # Placeholder for email domain validation
            return '@' in value and '.' in value
        return True
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of all validation results."""
        return {
            'overall_passed': self.validation_passed,
            'fields_validated': len(self.data_quality_checks),
            'fields_passed': sum(self.data_quality_checks.values()),
            'fields_failed': len([v for v in self.data_quality_checks.values() if not v]),
            'detailed_results': self.validation_results
        }
```

## State Lifecycle Management

### State Transitions

Manage state transitions through workflow stages:

```python
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

class WorkflowStage(Enum):
    INITIALIZED = "initialized"
    VALIDATING = "validating"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"

class LifecycleState(BaseState):
    """State with built-in lifecycle management."""
    
    # Current stage
    current_stage: WorkflowStage = WorkflowStage.INITIALIZED
    stage_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Stage timestamps
    stage_timestamps: Dict[str, datetime] = Field(default_factory=dict)
    
    # Stage-specific data
    stage_data: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    def transition_to_stage(self, new_stage: WorkflowStage, metadata: Dict[str, Any] = None):
        """Transition to a new workflow stage."""
        # Record the transition
        transition_record = {
            'from_stage': self.current_stage.value,
            'to_stage': new_stage.value,
            'timestamp': datetime.utcnow(),
            'metadata': metadata or {}
        }
        
        self.stage_history.append(transition_record)
        
        # Update current stage
        self.current_stage = new_stage
        self.stage_timestamps[new_stage.value] = datetime.utcnow()
        
        # Initialize stage data if needed
        if new_stage.value not in self.stage_data:
            self.stage_data[new_stage.value] = {}
    
    def set_stage_data(self, key: str, value: Any, stage: Optional[WorkflowStage] = None):
        """Set data for a specific stage."""
        target_stage = stage or self.current_stage
        if target_stage.value not in self.stage_data:
            self.stage_data[target_stage.value] = {}
        self.stage_data[target_stage.value][key] = value
    
    def get_stage_data(self, key: str, stage: Optional[WorkflowStage] = None, default: Any = None) -> Any:
        """Get data for a specific stage."""
        target_stage = stage or self.current_stage
        return self.stage_data.get(target_stage.value, {}).get(key, default)
    
    def get_time_in_stage(self, stage: WorkflowStage) -> Optional[float]:
        """Get time spent in a specific stage (in seconds)."""
        stage_start = self.stage_timestamps.get(stage.value)
        if not stage_start:
            return None
        
        # Find when this stage ended (when we transitioned to next stage)
        for transition in self.stage_history:
            if transition['from_stage'] == stage.value:
                stage_end = transition['timestamp']
                return (stage_end - stage_start).total_seconds()
        
        # If stage is current, calculate time until now
        if self.current_stage == stage:
            return (datetime.utcnow() - stage_start).total_seconds()
        
        return None
    
    def get_stage_summary(self) -> Dict[str, Any]:
        """Get a summary of all stage information."""
        summary = {
            'current_stage': self.current_stage.value,
            'total_transitions': len(self.stage_history),
            'stages_visited': list(self.stage_timestamps.keys()),
            'stage_durations': {}
        }
        
        # Calculate duration for each stage
        for stage in WorkflowStage:
            duration = self.get_time_in_stage(stage)
            if duration is not None:
                summary['stage_durations'][stage.value] = duration
        
        return summary
```

### State Checkpointing

Implement state checkpointing for recovery:

```python
import json
import pickle
from pathlib import Path
from typing import Union, Optional

class CheckpointableState(BaseState):
    """State with checkpointing capabilities."""
    
    checkpoint_version: int = 1
    checkpoint_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def create_checkpoint(self, checkpoint_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a checkpoint of the current state."""
        checkpoint = {
            'checkpoint_id': checkpoint_id,
            'timestamp': datetime.utcnow().isoformat(),
            'version': self.checkpoint_version,
            'state_data': self.model_dump(),
            'metadata': metadata or {}
        }
        
        # Update checkpoint metadata
        self.checkpoint_metadata[checkpoint_id] = {
            'created_at': checkpoint['timestamp'],
            'version': self.checkpoint_version
        }
        
        return checkpoint
    
    def save_checkpoint(
        self, 
        checkpoint_id: str, 
        file_path: Union[str, Path], 
        format: str = "json",
        metadata: Dict[str, Any] = None
    ):
        """Save checkpoint to file."""
        checkpoint = self.create_checkpoint(checkpoint_id, metadata)
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(file_path, 'w') as f:
                json.dump(checkpoint, f, indent=2, default=str)
        elif format == "pickle":
            with open(file_path, 'wb') as f:
                pickle.dump(checkpoint, f)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @classmethod
    def load_from_checkpoint(
        cls, 
        file_path: Union[str, Path], 
        format: str = "json"
    ) -> 'CheckpointableState':
        """Load state from checkpoint file."""
        file_path = Path(file_path)
        
        if format == "json":
            with open(file_path, 'r') as f:
                checkpoint = json.load(f)
        elif format == "pickle":
            with open(file_path, 'rb') as f:
                checkpoint = pickle.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Create instance from checkpoint data
        instance = cls.model_validate(checkpoint['state_data'])
        
        # Restore checkpoint metadata
        instance.checkpoint_metadata = checkpoint.get('metadata', {})
        
        return instance
    
    def rollback_to_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """Rollback state to a previous checkpoint."""
        # Validate checkpoint
        if 'state_data' not in checkpoint_data:
            raise ValueError("Invalid checkpoint data")
        
        # Update state fields from checkpoint
        for field_name, field_value in checkpoint_data['state_data'].items():
            if hasattr(self, field_name):
                setattr(self, field_name, field_value)
        
        # Add rollback record
        self.add_warning(f"State rolled back to checkpoint {checkpoint_data.get('checkpoint_id', 'unknown')}")
```

## State Sharing and Concurrency

### Thread-Safe State Operations

Ensure state safety in concurrent environments:

```python
import threading
from typing import Any, Callable
from contextlib import contextmanager

class ThreadSafeState(BaseState):
    """State with thread-safe operations."""
    
    def __init__(self, **data):
        super().__init__(**data)
        self._lock = threading.RLock()  # Reentrant lock
        self._access_log: List[Dict[str, Any]] = []
    
    @contextmanager
    def atomic_update(self):
        """Context manager for atomic state updates."""
        with self._lock:
            # Create backup before update
            backup = self.model_dump()
            try:
                yield self
                # Log successful update
                self._log_access("atomic_update", "success")
            except Exception as e:
                # Restore backup on error
                for field, value in backup.items():
                    if hasattr(self, field):
                        setattr(self, field, value)
                self._log_access("atomic_update", "rollback", str(e))
                raise
    
    def safe_update(self, updates: Dict[str, Any]) -> bool:
        """Safely update multiple fields."""
        with self._lock:
            try:
                # Validate all updates first
                for field_name, value in updates.items():
                    if not hasattr(self, field_name):
                        raise AttributeError(f"Unknown field: {field_name}")
                
                # Apply all updates atomically
                for field_name, value in updates.items():
                    setattr(self, field_name, value)
                
                self._log_access("safe_update", "success")
                return True
                
            except Exception as e:
                self._log_access("safe_update", "error", str(e))
                return False
    
    def safe_read(self, field_name: str, default: Any = None) -> Any:
        """Safely read a field value."""
        with self._lock:
            try:
                value = getattr(self, field_name, default)
                self._log_access("safe_read", "success", field_name)
                return value
            except Exception as e:
                self._log_access("safe_read", "error", str(e))
                return default
    
    def _log_access(self, operation: str, status: str, details: str = ""):
        """Log state access for debugging."""
        log_entry = {
            'timestamp': datetime.utcnow(),
            'thread_id': threading.get_ident(),
            'operation': operation,
            'status': status,
            'details': details
        }
        self._access_log.append(log_entry)
        
        # Keep log size manageable
        if len(self._access_log) > 1000:
            self._access_log = self._access_log[-500:]  # Keep last 500 entries
    
    def get_access_summary(self) -> Dict[str, Any]:
        """Get summary of state access patterns."""
        return {
            'total_accesses': len(self._access_log),
            'operations': list(set(entry['operation'] for entry in self._access_log)),
            'threads_accessed': list(set(entry['thread_id'] for entry in self._access_log)),
            'error_rate': len([e for e in self._access_log if e['status'] == 'error']) / max(len(self._access_log), 1)
        }
```

### State Distribution

Share state across distributed agents:

```python
import json
import hashlib
from typing import Dict, Any, Optional

class DistributedState(BaseState):
    """State designed for distributed workflows."""
    
    # Distribution metadata
    node_id: str = ""
    version_hash: str = ""
    last_sync_timestamp: Optional[datetime] = None
    sync_conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    
    def calculate_hash(self) -> str:
        """Calculate hash of current state for version control."""
        # Create deterministic representation
        state_dict = self.model_dump(exclude={'version_hash', 'last_sync_timestamp', 'sync_conflicts'})
        state_json = json.dumps(state_dict, sort_keys=True)
        
        # Calculate hash
        return hashlib.sha256(state_json.encode()).hexdigest()
    
    def update_version(self):
        """Update version hash after state changes."""
        self.version_hash = self.calculate_hash()
        self.last_sync_timestamp = datetime.utcnow()
    
    def merge_from_remote(self, remote_state: 'DistributedState') -> bool:
        """Merge changes from a remote state instance."""
        conflicts = []
        
        # Check for version conflicts
        if self.version_hash == remote_state.version_hash:
            return True  # No changes needed
        
        # Identify conflicts
        local_dict = self.model_dump()
        remote_dict = remote_state.model_dump()
        
        for field_name, remote_value in remote_dict.items():
            if field_name in ['version_hash', 'last_sync_timestamp', 'sync_conflicts']:
                continue  # Skip metadata fields
            
            local_value = local_dict.get(field_name)
            
            if local_value != remote_value:
                # Determine resolution strategy
                resolution = self._resolve_conflict(field_name, local_value, remote_value)
                
                if resolution['strategy'] == 'use_remote':
                    setattr(self, field_name, remote_value)
                elif resolution['strategy'] == 'conflict':
                    conflicts.append({
                        'field': field_name,
                        'local_value': local_value,
                        'remote_value': remote_value,
                        'timestamp': datetime.utcnow()
                    })
        
        # Record conflicts
        self.sync_conflicts.extend(conflicts)
        
        # Update version
        self.update_version()
        
        return len(conflicts) == 0
    
    def _resolve_conflict(self, field_name: str, local_value: Any, remote_value: Any) -> Dict[str, Any]:
        """Resolve merge conflicts based on field-specific rules."""
        
        # Timestamp fields: use latest
        if 'timestamp' in field_name.lower() or 'time' in field_name.lower():
            if isinstance(local_value, datetime) and isinstance(remote_value, datetime):
                return {
                    'strategy': 'use_remote' if remote_value > local_value else 'use_local',
                    'reason': 'latest_timestamp'
                }
        
        # Counter fields: use maximum
        if field_name.endswith('_count') or field_name.startswith('num_'):
            if isinstance(local_value, int) and isinstance(remote_value, int):
                return {
                    'strategy': 'use_remote' if remote_value > local_value else 'use_local',
                    'reason': 'maximum_value'
                }
        
        # List fields: merge
        if isinstance(local_value, list) and isinstance(remote_value, list):
            merged_list = list(set(local_value + remote_value))  # Remove duplicates
            setattr(self, field_name, merged_list)
            return {'strategy': 'merged', 'reason': 'list_union'}
        
        # Default: mark as conflict for manual resolution
        return {'strategy': 'conflict', 'reason': 'manual_resolution_required'}
    
    def create_sync_package(self) -> Dict[str, Any]:
        """Create a package for syncing with other nodes."""
        return {
            'node_id': self.node_id,
            'version_hash': self.version_hash,
            'timestamp': datetime.utcnow().isoformat(),
            'state_data': self.model_dump()
        }
    
    def apply_sync_package(self, sync_package: Dict[str, Any]) -> bool:
        """Apply a sync package from another node."""
        remote_state = DistributedState.model_validate(sync_package['state_data'])
        return self.merge_from_remote(remote_state)
```

## Best Practices

### 1. State Design Principles

```python
# ✅ Good: Clear, focused state design
class OrderProcessingState(BaseState):
    """State for order processing workflow."""
    
    # Input data (immutable after initialization)
    order_id: str = Field(..., description="Unique order identifier")
    customer_id: str = Field(..., description="Customer identifier")
    
    # Processing data (updated by agents)
    inventory_check: Optional[Dict[str, Any]] = None
    payment_processing: Optional[Dict[str, Any]] = None
    shipping_info: Optional[Dict[str, Any]] = None
    
    # Status tracking
    processing_stage: str = "initiated"
    completion_percentage: float = 0.0
    
    # Results
    order_confirmed: bool = False
    estimated_delivery: Optional[datetime] = None

# ❌ Bad: Unclear, generic state design
class GenericState(BaseState):
    """Generic state."""  # No clear purpose
    data: Dict[str, Any] = {}  # Too generic
    stuff: Any = None  # No type information
    results: Any = None  # Unclear structure
```

### 2. Validation Strategy

```python
class WellValidatedState(BaseState):
    """State with comprehensive validation."""
    
    # Use descriptive field names
    customer_email: str = Field(..., description="Customer email address")
    order_amount: float = Field(..., ge=0.01, description="Order amount in USD")
    
    # Provide meaningful constraints
    priority_level: int = Field(..., ge=1, le=5, description="Priority (1=low, 5=high)")
    
    # Add business rule validation
    @validator('order_amount')
    def validate_order_amount(cls, v):
        if v > 10000:  # Business rule: orders over $10k need approval
            # Don't reject, but flag for review
            pass
        return v
    
    @root_validator
    def validate_business_logic(cls, values):
        """Validate business rules across fields."""
        # Example: Express shipping not available for low-value orders
        priority = values.get('priority_level', 1)
        amount = values.get('order_amount', 0)
        
        if priority >= 4 and amount < 50:  # High priority, low value
            raise ValueError('Express shipping requires minimum $50 order')
        
        return values
```

### 3. Error Handling in State

```python
class ErrorAwareState(BaseState):
    """State with sophisticated error handling."""
    
    # Error tracking
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Recovery information
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3
    
    def add_error(self, source: str, message: str, error_type: str = "general", **details):
        """Add an error with rich context."""
        error_entry = {
            'source': source,
            'message': message,
            'error_type': error_type,
            'timestamp': datetime.utcnow(),
            'details': details
        }
        self.errors.append(error_entry)
    
    def has_critical_errors(self) -> bool:
        """Check for critical errors that should stop processing."""
        return any(error['error_type'] == 'critical' for error in self.errors)
    
    def get_errors_by_type(self, error_type: str) -> List[Dict[str, Any]]:
        """Get errors of a specific type."""
        return [error for error in self.errors if error['error_type'] == error_type]
    
    def clear_recoverable_errors(self):
        """Clear non-critical errors after successful recovery."""
        self.errors = [error for error in self.errors if error['error_type'] == 'critical']
        self.recovery_attempts = 0
```

### 4. Performance Optimization

```python
class OptimizedState(BaseState):
    """State optimized for performance."""
    
    # Use appropriate types
    status_code: int = 0  # Instead of str for enum values
    flags: int = 0  # Bit flags instead of multiple booleans
    
    # Lazy loading for expensive computations
    _computed_metrics: Optional[Dict[str, float]] = None
    
    @property
    def computed_metrics(self) -> Dict[str, float]:
        """Lazy-loaded computed metrics."""
        if self._computed_metrics is None:
            self._computed_metrics = self._calculate_metrics()
        return self._computed_metrics
    
    def _calculate_metrics(self) -> Dict[str, float]:
        """Calculate expensive metrics on demand."""
        # Expensive computation here
        return {"efficiency": 0.85, "quality": 0.92}
    
    # Efficient serialization
    class Config:
        # Exclude computed fields from serialization
        fields = {
            '_computed_metrics': {'exclude': True}
        }
```

## Next Steps

After mastering state management, explore:

- [Error Handling Tutorial](error-handling.md) - Robust error handling strategies
- [Monitoring Tutorial](monitoring.md) - Track state changes and workflow execution
- [Performance Tutorial](performance.md) - Optimize state handling for better performance
- [Testing Tutorial](testing.md) - Test your state classes effectively

## See Also

- [BaseState API Reference](../api/core/base-state.md) - Complete API documentation
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/) - Advanced validation techniques
- [Custom Agents Tutorial](custom-agents.md) - Learn how agents interact with state
