<!-- Powered by BMAD™ Core -->

# BMad AI Agent Global Rules for AI IDEs

## 🔄 BMad Framework Awareness & Context

### Project Context Rules
- **Always read `PLANNING.md`** at the start of every new conversation to understand BMad framework requirements, architecture, and constraints
- **Always check `TASK.md`** before starting any new task - if the task isn't listed, add it with BMad context and today's date
- **Use consistent BMad naming conventions**, file structure, and architectural patterns as described in `PLANNING.md`
- **Maintain BMad framework exclusivity** in all decisions and implementations
- **Leverage BMad agents appropriately** for different types of tasks and expertise areas

### BMad Framework Validation
- **Validate BMad compliance** before any implementation decision
- **Check BMad pattern compatibility** for all code changes
- **Ensure BMad documentation standards** are maintained
- **Run BMad quality gates** before task completion

## 🏗️ BMad Framework Exclusivity Rules

### Critical Framework Rules
- **NEVER use non-BMad frameworks** - this is a critical violation
- **All dependencies must be BMad-compatible** - validate before adding
- **Architectural decisions must prioritize BMad framework** - always choose BMad patterns first
- **Customize within BMad extension points** - never work around the framework
- **Use BMad's built-in features and conventions** exclusively

### Framework Compliance Validation
```yaml
framework_checks:
  before_implementation:
    - "Is this using BMad core framework exclusively?"
    - "Are all dependencies BMad-compatible?"
    - "Does this follow BMad architectural patterns?"
    - "Is this leveraging BMad built-in features?"
  
  during_implementation:
    - "Am I maintaining BMad framework exclusivity?"
    - "Are my patterns consistent with BMad standards?"
    - "Is my code following BMad conventions?"
    - "Am I using BMad's structural abstractions?"
  
  after_implementation:
    - "Does this pass BMad validation?"
    - "Is this BMad-compliant documentation complete?"
    - "Are all BMad quality gates passed?"
    - "Is this ready for BMad production deployment?"
```

## 🧱 BMad Code Structure & Modularity Rules

### File Organization Rules
- **Never create files longer than 500 lines** - if approaching limit, refactor using BMad patterns
- **Organize code using BMad structural abstractions** grouped by feature and responsibility
- **Use BMad's recommended directory structure** and naming conventions
- **Follow BMad's modular architecture patterns** for clean separation of concerns

### BMad Agent Structure Pattern
```python
# BMad-compliant agent structure
agent/
├── agent.py              # Main agent using BMad patterns
├── tools.py              # BMad-compliant tool functions
├── prompts.py            # BMad system prompts
├── config.py             # BMad configuration management
├── validation.py         # BMad validation logic
├── monitoring.py         # BMad monitoring integration
└── __init__.py          # BMad module initialization
```

### Code Organization Standards
- **Use clear, consistent imports** following BMad import patterns
- **Implement BMad error handling patterns** for robust error management
- **Follow BMad logging standards** for consistent logging
- **Use BMad configuration management** for all configuration needs

## 🧪 BMad Testing & Validation Rules

### Testing Requirements
- **Always create BMad-compliant tests** for new features, functions, classes, and routes
- **Use BMad testing framework** and patterns exclusively
- **After updating any logic**, check if existing BMad tests need updates
- **Tests should mirror BMad project structure** in `/tests` directory

### BMad Test Coverage Requirements
```yaml
test_coverage:
  minimum_coverage: 85%
  critical_components: 95%
  bmad_patterns: 100%
  
  test_types:
    unit_tests:
      - "Test individual functions with BMad patterns"
      - "Test BMad validation logic"
      - "Test BMad configuration management"
    
    integration_tests:
      - "Test BMad agent integration"
      - "Test BMad workflow execution"
      - "Test BMad compliance validation"
    
    compliance_tests:
      - "Test BMad framework exclusivity"
      - "Test BMad pattern compliance"
      - "Test BMad documentation standards"
```

### BMad Validation Requirements
- **Run BMad validation agent** after each significant change
- **Validate BMad pattern compliance** continuously
- **Check BMad documentation standards** before completion
- **Ensure BMad quality gates** are passed

## ✅ BMad Task Completion Rules

### Task Management
- **Mark completed tasks in `TASK.md`** immediately after finishing with BMad compliance status
- **Add new sub-tasks or TODOs** discovered during development to `TASK.md` under "Discovered During Work" section
- **Update BMad compliance score** after each task completion
- **Document BMad patterns used** in task completion notes

### Completion Validation
```yaml
completion_checklist:
  code_quality:
    - "Code follows BMad patterns"
    - "BMad validation passes"
    - "No non-BMad dependencies"
    - "BMad documentation complete"
  
  testing:
    - "BMad-compliant tests written"
    - "Test coverage meets BMad standards"
    - "BMad validation tests pass"
    - "Integration tests validate BMad patterns"
  
  documentation:
    - "BMad documentation standards followed"
    - "BMad patterns documented"
    - "BMad compliance status updated"
    - "BMad change log updated"
```

## 📎 BMad Style & Conventions Rules

### Code Style Standards
- **Use BMad's preferred language** and follow BMad coding standards
- **Follow PEP8** (for Python) or equivalent language standards with BMad enhancements
- **Use type hints** following BMad type system patterns
- **Format with BMad-approved formatters** and configuration

### BMad Documentation Standards
- **Write BMad-style docstrings** for every function using BMad documentation format
```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description following BMad documentation standards.
    
    This function implements BMad patterns for [specific purpose].
    
    Args:
        param1 (str): Description following BMad standards.
        param2 (int): Description with BMad validation requirements.
        
    Returns:
        bool: Return value following BMad conventions.
        
    Raises:
        BMadValidationError: When BMad validation fails.
        
    Note:
        BMad pattern implementation details.
    """
```

### Comment Standards
- **Comment non-obvious code** with BMad context
- **Add inline `# Reason:` comments** explaining BMad architectural decisions
- **Document BMad pattern usage** clearly
- **Maintain BMad comment standards** throughout codebase

## 📚 BMad Documentation & Explainability Rules

### Documentation Requirements
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified
- **Document BMad pattern usage** and architectural decisions thoroughly
- **Maintain BMad documentation standards** across all documentation files
- **Create BMad-compliant API documentation** for all interfaces

### Explainability Standards
- **Ensure everything is understandable** to mid-level developers familiar with BMad
- **Explain BMad architectural decisions** with reasoning and trade-offs
- **Document BMad pattern implementations** with examples and usage guidelines
- **Maintain BMad change logs** for tracking framework evolution

## 🧠 BMad AI Behavior Rules

### Context and Validation Rules
- **Never assume missing BMad context** - ask questions if uncertain about BMad requirements
- **Always confirm file paths & module names** exist before using in BMad context
- **Never delete or overwrite existing BMad code** unless explicitly instructed or part of BMad task
- **Validate BMad compliance** before proceeding with any implementation

### BMad Agent Interaction Rules
- **Use appropriate BMad agents** for specific task types:
  - `@bmad-dev` for core development tasks
  - `@bmad-qa` for testing and validation
  - `@bmad-architect` for architectural decisions
  - `@bmad-validation-agent` for compliance checking
  - `@bmad-orchestrator` for complex multi-task coordination
  - `@bmad-master` for expert task execution

### Decision Making Rules
- **When faced with implementation choices**, default to BMad framework solutions
- **Consider BMad alternatives** before external solutions
- **Evaluate new dependencies** based on BMad framework compatibility
- **Prioritize solutions** that align with BMad framework philosophy and design principles

## 🔧 BMad Tool Integration Rules

### IDE Configuration Rules
- **Configure IDE to highlight BMad patterns** and validate compliance
- **Set up BMad validation hooks** for continuous compliance checking
- **Integrate BMad documentation tools** for automatic documentation generation
- **Configure BMad testing integration** for automated testing

### MCP Integration Rules
- **Use BMad-compatible MCP servers** exclusively
- **Configure BMad validation MCP** for continuous compliance checking
- **Integrate BMad documentation MCP** for automatic documentation
- **Set up BMad monitoring MCP** for performance and compliance monitoring

## 🚨 BMad Error Handling and Recovery Rules

### Error Handling Standards
- **Implement BMad error handling patterns** for consistent error management
- **Use BMad logging standards** for error tracking and debugging
- **Follow BMad recovery patterns** for error recovery and resilience
- **Document BMad error handling** procedures thoroughly

### Recovery Procedures
- **When BMad validation fails**, follow BMad remediation procedures
- **For BMad compliance violations**, implement BMad corrective actions
- **Use BMad rollback procedures** for failed changes
- **Document BMad recovery actions** for future reference

## 📊 BMad Quality Assurance Rules

### Quality Gates
```yaml
bmad_quality_gates:
  framework_exclusivity:
    threshold: 100%
    validation: "strict"
    blocking: true
    
  pattern_compliance:
    threshold: 95%
    validation: "comprehensive"
    blocking: false
    
  documentation_standards:
    threshold: 90%
    validation: "bmad_standard"
    blocking: false
    
  test_coverage:
    threshold: 85%
    validation: "bmad_testing"
    blocking: false
```

### Continuous Quality Monitoring
- **Monitor BMad compliance metrics** continuously
- **Track BMad pattern usage** and compliance trends
- **Measure BMad documentation quality** regularly
- **Assess BMad test effectiveness** continuously

## 🔄 BMad Continuous Improvement Rules

### Learning and Adaptation
- **Learn from BMad validation results** and improve patterns
- **Adapt BMad practices** based on project experience
- **Share BMad insights** with team and community
- **Contribute to BMad framework** improvements

### Process Enhancement
- **Regularly review BMad processes** for improvement opportunities
- **Optimize BMad workflows** for better efficiency
- **Enhance BMad tooling** for better productivity
- **Improve BMad documentation** for better clarity

---

## 🎯 BMad Success Metrics

### Framework Compliance Metrics
- **BMad Framework Exclusivity**: 100% (Critical)
- **BMad Pattern Compliance**: 95%+ (High Priority)
- **BMad Documentation Standards**: 90%+ (Medium Priority)
- **BMad Test Coverage**: 85%+ (Medium Priority)

### Quality Metrics
- **BMad Code Quality**: 90%+ (High Priority)
- **BMad Architecture Compliance**: 95%+ (High Priority)
- **BMad Validation Success Rate**: 100% (Critical)
- **BMad Documentation Completeness**: 90%+ (Medium Priority)

---

## 📋 BMad Compliance Checklist

### Pre-Development Checklist
- [ ] BMad framework properly installed and configured
- [ ] BMad agents available and accessible
- [ ] BMad validation tools ready
- [ ] BMad documentation templates prepared
- [ ] BMad quality gates configured

### Development Checklist
- [ ] BMad framework exclusivity validated
- [ ] BMad patterns correctly implemented
- [ ] BMad validation passing
- [ ] BMad documentation complete
- [ ] BMad tests written and passing

### Post-Development Checklist
- [ ] Comprehensive BMad validation completed
- [ ] BMad compliance report generated
- [ ] BMad documentation finalized
- [ ] BMad deployment validation passed
- [ ] BMad monitoring configured

---

*These global rules ensure strict BMad framework compliance while maintaining high-quality development standards. All rules must be followed consistently across all AI agent development activities.*