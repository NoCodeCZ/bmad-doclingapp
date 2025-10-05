<!-- Powered by BMAD™ Core -->

# 🧱 BMad Modular Code Structure Guidelines

## Overview

This document outlines the BMad framework's approach to modular code structure for AI agent development. These guidelines ensure consistency, maintainability, and compliance with BMad architectural patterns.

## 🏗️ BMad Architecture Principles

### Core BMad Principles
1. **Framework Exclusivity**: All code must use BMad patterns exclusively
2. **Modular Design**: Clear separation of concerns using BMad abstractions
3. **Consistent Structure**: Standardized organization across all BMad projects
4. **Scalable Architecture**: Built to scale using BMad patterns
5. **Validation-First**: Continuous BMad compliance validation

### BMad Design Patterns
- **Agent Pattern**: Standardized agent structure
- **Tool Pattern**: Consistent tool abstraction
- **Configuration Pattern**: Centralized configuration management
- **Validation Pattern**: Built-in validation mechanisms
- **Monitoring Pattern**: Integrated monitoring and observability

## 📁 BMad Project Structure

### Root Level Structure
```
ai-agent-project/
├── .bmad/                          # BMad framework configuration
│   ├── core-config.yaml           # BMad core configuration
│   ├── validation-rules.yaml      # BMad validation rules
│   └── quality-gates.yaml         # BMad quality gates
├── .kilocode/                     # KiloCode integration
│   ├── rules/                     # BMad-compliant rules
│   └── bmad-integration/          # BMad integration components
├── agent/                         # Main agent code
├── tools/                         # Agent tools
├── prompts/                       # Prompt templates
├── config/                        # Configuration management
├── tests/                         # BMad-compliant tests
├── docs/                          # BMad documentation
├── scripts/                       # BMad utility scripts
├── requirements.txt               # BMad-compatible dependencies
├── PLANNING.md                    # BMad planning document
├── TASK.md                        # BMad task management
├── README.md                      # BMad project documentation
└── .env.example                   # BMad environment template
```

## 🤖 BMad Agent Structure

### Main Agent Module
```python
# agent/agent.py
"""
BMad-compliant main agent implementation.

This module implements the core agent using BMad patterns and conventions.
"""

from bmad.core import BaseAgent, BMadConfig
from bmad.validation import validate_compliance
from bmad.monitoring import monitor_performance
from .tools import ToolManager
from .prompts import PromptManager
from .config import AgentConfig

class BMadAgent(BaseAgent):
    """
    BMad-compliant agent implementation.
    
    Follows BMad agent patterns for consistency and validation.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize agent with BMad configuration."""
        super().__init__(config)
        self.tools = ToolManager(config)
        self.prompts = PromptManager(config)
        self._validate_bmad_compliance()
    
    @validate_compliance
    async def process_request(self, request: dict) -> dict:
        """
        Process incoming request using BMad patterns.
        
        Args:
            request (dict): Incoming request data
            
        Returns:
            dict: Processed response
            
        Raises:
            BMadValidationError: When BMad validation fails
        """
        # BMad pattern implementation
        pass
    
    def _validate_bmad_compliance(self):
        """Validate BMad framework compliance."""
        # BMad validation logic
        pass
```

### Agent Configuration
```python
# agent/config.py
"""
BMad configuration management.

Implements BMad configuration patterns for centralized management.
"""

from bmad.config import BaseConfig, validate_config
from pydantic import BaseModel, Field
from typing import Optional, List

class AgentConfig(BaseConfig):
    """
    BMad-compliant agent configuration.
    
    Follows BMad configuration patterns for validation and management.
    """
    
    # BMad Framework Configuration
    bmad_framework_version: str = Field(
        default="latest",
        description="BMad framework version"
    )
    
    bmad_validation_level: str = Field(
        default="strict",
        description="BMad validation level"
    )
    
    # Agent Configuration
    agent_name: str = Field(..., description="Agent name")
    agent_version: str = Field(..., description="Agent version")
    
    # Tool Configuration
    enabled_tools: List[str] = Field(
        default_factory=list,
        description="List of enabled tools"
    )
    
    # Validation Configuration
    validation_rules: dict = Field(
        default_factory=dict,
        description="BMad validation rules"
    )
    
    @validate_config
    def validate_bmad_compliance(self) -> bool:
        """Validate BMad configuration compliance."""
        # BMad validation implementation
        return True
```

## 🛠️ BMad Tools Structure

### Tool Manager
```python
# tools/tool_manager.py
"""
BMad tool management system.

Implements BMad tool patterns for consistent tool integration.
"""

from bmad.tools import BaseToolManager, validate_tool
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BMadTool(BaseTool):
    """
    Base class for BMad-compliant tools.
    
    All tools must inherit from this class and follow BMad patterns.
    """
    
    def __init__(self, config: dict):
        """Initialize tool with BMad configuration."""
        self.config = config
        self._validate_bmad_compliance()
    
    @validate_tool
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute tool using BMad patterns.
        
        Returns:
            Dict[str, Any]: Tool execution result
        """
        pass
    
    def _validate_bmad_compliance(self):
        """Validate tool BMad compliance."""
        # BMad tool validation
        pass

class ToolManager(BaseToolManager):
    """
    BMad-compliant tool manager.
    
    Manages tool lifecycle and validation using BMad patterns.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize tool manager with BMad configuration."""
        self.config = config
        self.tools: Dict[str, BMadTool] = {}
        self._load_bmad_tools()
    
    def _load_bmad_tools(self):
        """Load tools following BMad patterns."""
        # BMad tool loading logic
        pass
    
    @validate_tool
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute tool with BMad validation."""
        # BMad tool execution
        pass
```

### Example Tool Implementation
```python
# tools/web_search.py
"""
BMad-compliant web search tool.

Implements web search functionality using BMad patterns.
"""

from .tool_manager import BMadTool
from bmad.validation import validate_input, validate_output
from typing import Dict, Any, Optional

class WebSearchTool(BMadTool):
    """
    BMad-compliant web search tool.
    
    Provides web search capabilities following BMad patterns.
    """
    
    def __init__(self, config: dict):
        """Initialize web search tool."""
        super().__init__(config)
        self.search_provider = config.get('search_provider', 'default')
        self._validate_search_config()
    
    @validate_input
    @validate_output
    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Perform web search using BMad patterns.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            Dict[str, Any]: Search results
        """
        # BMad search implementation
        pass
    
    def _validate_search_config(self):
        """Validate search configuration."""
        # BMad configuration validation
        pass
```

## 📝 BMad Prompts Structure

### Prompt Manager
```python
# prompts/prompt_manager.py
"""
BMad prompt management system.

Implements BMad prompt patterns for consistent prompt handling.
"""

from bmad.prompts import BasePromptManager, validate_prompt
from typing import Dict, Any, Optional

class PromptManager(BasePromptManager):
    """
    BMad-compliant prompt manager.
    
    Manages prompts using BMad patterns and validation.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize prompt manager with BMad configuration."""
        self.config = config
        self.prompts: Dict[str, str] = {}
        self._load_bmad_prompts()
    
    def _load_bmad_prompts(self):
        """Load prompts following BMad patterns."""
        # BMad prompt loading logic
        pass
    
    @validate_prompt
    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """Get prompt with BMad validation."""
        # BMad prompt retrieval
        pass
    
    @validate_prompt
    def format_prompt(self, prompt_name: str, **kwargs) -> str:
        """Format prompt using BMad patterns."""
        # BMad prompt formatting
        pass
```

### Prompt Templates
```python
# prompts/templates.py
"""
BMad prompt templates.

Implements BMad prompt template patterns.
"""

from bmad.prompts import BaseTemplate, validate_template

class BMadTemplate(BaseTemplate):
    """
    Base class for BMad prompt templates.
    
    All templates must follow BMad patterns.
    """
    
    def __init__(self, template_name: str, template_content: str):
        """Initialize template with BMad validation."""
        self.name = template_name
        self.content = template_content
        self._validate_template_compliance()
    
    @validate_template
    def render(self, **kwargs) -> str:
        """Render template using BMad patterns."""
        # BMad template rendering
        pass
    
    def _validate_template_compliance(self):
        """Validate template BMad compliance."""
        # BMad template validation
        pass

# Example templates
SYSTEM_PROMPT_TEMPLATE = """
You are a BMad-compliant AI agent designed for {purpose}.

Follow these BMad principles:
- Use BMad framework exclusively
- Apply BMad patterns consistently
- Validate BMad compliance continuously
- Maintain BMad documentation standards

Agent Configuration:
{config}

Instructions:
{instructions}
"""

SEARCH_PROMPT_TEMPLATE = """
Search for information using BMad patterns.

Query: {query}
Max Results: {max_results}
Search Provider: {provider}

BMad Requirements:
- Validate search results
- Format output using BMad standards
- Include BMad compliance metadata
"""
```

## 🧪 BMad Testing Structure

### Test Base Classes
```python
# tests/base.py
"""
BMad testing base classes.

Provides BMad-compliant testing infrastructure.
"""

import pytest
from bmad.testing import BMadTestCase, validate_test
from bmad.validation import BMadValidator

class BMadAgentTestCase(BMadTestCase):
    """
    Base class for BMad agent tests.
    
    Provides BMad-compliant testing utilities.
    """
    
    @pytest.fixture(autouse=True)
    def setup_bmad_validation(self):
        """Setup BMad validation for all tests."""
        self.validator = BMadValidator()
        self.validator.enable_strict_mode()
    
    @validate_test
    def test_bmad_compliance(self):
        """Test BMad framework compliance."""
        compliance_score = self.validator.check_compliance(self.agent)
        assert compliance_score >= 95.0
    
    def test_bmad_patterns(self):
        """Test BMad pattern implementation."""
        patterns = self.agent.get_used_patterns()
        assert all(pattern.is_bmad_compliant() for pattern in patterns)
```

### Test Implementation
```python
# tests/test_agent.py
"""
BMad agent tests.

Tests agent functionality with BMad compliance validation.
"""

from .base import BMadAgentTestCase
from agent.agent import BMadAgent
from agent.config import AgentConfig

class TestBMadAgent(BMadAgentTestCase):
    """Test BMad agent implementation."""
    
    def setup_method(self):
        """Setup test agent."""
        self.config = AgentConfig(
            agent_name="test_agent",
            agent_version="1.0.0",
            bmad_validation_level="strict"
        )
        self.agent = BMadAgent(self.config)
    
    def test_agent_initialization(self):
        """Test agent initialization with BMad compliance."""
        assert self.agent.config.bmad_framework_version is not None
        assert self.agent.config.bmad_validation_level == "strict"
    
    @validate_test
    async def test_process_request(self):
        """Test request processing with BMad validation."""
        request = {"test": "data"}
        response = await self.agent.process_request(request)
        
        # Validate BMad compliance in response
        assert "bmad_compliance" in response
        assert response["bmad_compliance"]["score"] >= 95.0
```

## 📊 BMad Monitoring Structure

### Monitoring Implementation
```python
# monitoring/bmad_monitor.py
"""
BMad monitoring system.

Implements BMad monitoring patterns for observability.
"""

from bmad.monitoring import BaseMonitor, validate_metrics
from typing import Dict, Any, Optional
import time

class BMadMonitor(BaseMonitor):
    """
    BMad-compliant monitoring system.
    
    Provides monitoring using BMad patterns.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize monitor with BMad configuration."""
        self.config = config
        self.metrics: Dict[str, Any] = {}
        self._setup_bmad_monitoring()
    
    def _setup_bmad_monitoring(self):
        """Setup BMad monitoring components."""
        # BMad monitoring setup
        pass
    
    @validate_metrics
    def record_metric(self, metric_name: str, value: Any):
        """Record metric using BMad patterns."""
        # BMad metric recording
        pass
    
    def get_bmad_compliance_metrics(self) -> Dict[str, Any]:
        """Get BMad compliance metrics."""
        return {
            "framework_exclusivity": self._check_framework_exclusivity(),
            "pattern_compliance": self._check_pattern_compliance(),
            "documentation_compliance": self._check_documentation_compliance(),
            "quality_score": self._calculate_quality_score()
        }
```

## 🚀 BMad Deployment Structure

### Deployment Configuration
```yaml
# deployment/bmad-deployment.yaml
# BMad deployment configuration

apiVersion: apps/v1
kind: Deployment
metadata:
  name: bmad-agent
  labels:
    framework: bmad
    compliance: strict
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bmad-agent
  template:
    metadata:
      labels:
        app: bmad-agent
        framework: bmad
    spec:
      containers:
      - name: bmad-agent
        image: bmad-agent:latest
        env:
        - name: BMAD_FRAMEWORK_VERSION
          value: "latest"
        - name: BMAD_VALIDATION_LEVEL
          value: "production"
        - name: BMAD_COMPLIANCE_CHECK
          value: "true"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 📋 BMad Structure Compliance Checklist

### File Organization
- [ ] Root structure follows BMad patterns
- [ ] All modules use BMad naming conventions
- [ ] Configuration files in BMad format
- [ ] Documentation follows BMad standards

### Code Structure
- [ ] All classes inherit from BMad base classes
- [ ] BMad validation decorators applied
- [ ] BMad error handling patterns used
- [ ] BMad logging standards implemented

### Testing Structure
- [ ] Tests inherit from BMad test base classes
- [ ] BMad validation included in tests
- [ ] Test structure mirrors project structure
- [ ] BMad compliance tested explicitly

### Configuration Structure
- [ ] BMad configuration patterns used
- [ ] Environment variables follow BMad standards
- [ ] Validation rules in BMad format
- [ ] Quality gates configured per BMad standards

---

## 🎯 BMad Structure Best Practices

### Development Guidelines
1. **Always inherit from BMad base classes**
2. **Use BMad validation decorators**
3. **Follow BMad naming conventions**
4. **Implement BMad error handling**
5. **Include BMad compliance validation**

### Testing Guidelines
1. **Inherit from BMad test base classes**
2. **Test BMad compliance explicitly**
3. **Use BMad validation in tests**
4. **Mirror project structure in tests**
5. **Validate BMad patterns in tests**

### Documentation Guidelines
1. **Use BMad documentation format**
2. **Include BMad compliance information**
3. **Document BMad pattern usage**
4. **Maintain BMad change logs**
5. **Follow BMad comment standards`

---

*This structure guide ensures consistent, maintainable, and BMad-compliant code organization across all AI agent projects.*