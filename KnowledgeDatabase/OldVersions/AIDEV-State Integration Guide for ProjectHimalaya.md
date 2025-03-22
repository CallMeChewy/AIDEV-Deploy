# AIDEV-State Integration Guide for ProjectHimalaya
**Created: March 17, 2025 7:15 PM**

This guide provides instructions for integrating AIDEV-State with ProjectHimalaya and other components like AIDEV-Validate.

## Overview

AIDEV-State is a specialized component designed to solve state management challenges within the ProjectHimalaya ecosystem. It provides robust mechanisms for:

1. Maintaining continuity between development sessions
2. Safely tracking and transferring state between components
3. Recovering from crashes and unexpected interruptions
4. Automatically documenting the development process

## Integration Steps

### 1. Set Up AIDEV-State

Execute the setup script to create the AIDEV-State project structure:

```bash
chmod +x Setup.sh
./Setup.sh
```

This creates a complete AIDEV-State project with all necessary files and directories.

### 2. Register ProjectHimalaya Components

Each component of ProjectHimalaya should be registered with AIDEV-State:

```python
from AIDEV_State import AIDevState

# Initialize state manager
StateManager = AIDevState()

# Register ProjectHimalaya components
StateManager.RegisterComponent("AIDEV-Validate", "/path/to/AIDEV-Validate")
StateManager.RegisterComponent("OllamaModelEditor", "/path/to/OllamaModelEditor")
# Register other components as needed
```

### 3. Integrate with AIDEV-Validate

The integration with AIDEV-Validate is handled by the example in `Examples/AIDEV_Validate_Integration.py`. This shows how to:

1. Register AIDEV-Validate as a component
2. Track file changes in the AIDEV-Validate codebase
3. Safely run validation operations
4. Generate validation reports
5. Maintain session continuity

### 4. Workflow Integration

Modify your development workflow to incorporate AIDEV-State:

#### Start of Session:
```python
# Initialize state manager
StateManager = AIDevState()

# Check for crash recovery
# (Already handled in initialization)

# Register components (if not already registered)
StateManager.RegisterComponent("AIDEV-Validate", "/path/to/AIDEV-Validate")
```

#### During Development:
```python
# Before performing a significant action
ActionId = StateManager.ActionTracker.RecordActionIntent(
    "CodeGeneration",
    "Generate module for feature X"
)

try:
    # Execute the action
    Result = StateManager.ActionTracker.ExecuteAction(
        ActionId,
        YourFunction,
        {"param1": "value1", "param2": "value2"}
    )
    
    # Action completed successfully
    print(f"Generated: {Result['Artifacts']}")
    
except Exception as Error:
    # Handle error
    print(f"Error: {Error}")
    # Recovery will happen automatically on next session start
```

#### End of Session:
```python
# Generate continuity document
DocumentPath = StateManager.GenerateContinuityDocument()
print(f"Session continuity document: {DocumentPath}")

# End session
StateManager.EndSession("Summary of what was accomplished")
```

### 5. Command Line Usage

You can also use the AIDEV-State command-line interface:

```bash
# Show status
python AIDEV-State.py status

# Register a component
python AIDEV-State.py component register AIDEV-Validate /path/to/AIDEV-Validate

# View component status
python AIDEV-State.py component status AIDEV-Validate

# End session
python AIDEV-State.py end --summary "Session summary"
```

## Crash Recovery

One of the most important features of AIDEV-State is crash recovery:

1. If a session crashes, AIDEV-State will detect this on the next start
2. It will recover any pending actions and mark them as interrupted
3. You can review these actions in the session continuity document
4. ActionSummaries directory will contain details of each interrupted action

## Session Continuity Documents

AIDEV-State automatically generates session continuity documents in the `Session/` directory. These markdown files include:

1. Overview of completed actions
2. Current development focus
3. Component status
4. Next steps for the project

You should review these documents at the start of each session to maintain continuity.

## Best Practices

1. **Always Use ActionTracker**: Wrap important operations with `ExecuteAction` to ensure they're properly tracked and can be recovered after crashes.

2. **Register All Components**: Register every component of ProjectHimalaya with AIDEV-State to track their relationships and dependencies.

3. **End Sessions Properly**: Always end sessions using `EndSession()` to generate proper continuity documents.

4. **Review Continuity Documents**: Start each session by reviewing the continuity document from the previous session.

5. **Maintain Component Separation**: Keep components in separate directories and register them individually with AIDEV-State.

## Troubleshooting

### Recovery After Crash

If a session crashes:

1. Simply restart AIDEV-State
2. It will automatically detect the crash and attempt recovery
3. Check the terminal output for recovery information
4. Review the ActionSummaries directory for details on interrupted actions

### Manual State Reset

If needed, you can manually reset the state:

1. Delete the `Session/CurrentState.json` file
2. Start a new session with `python AIDEV-State.py start`

## Example Integration Script

Save this as `integrate_with_projecthimalaya.py`:

```python
#!/usr/bin/env python3
# File: integrate_with_projecthimalaya.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-17
# Last Modified: 2025-03-17  7:15PM
# Description: Integrates AIDEV-State with ProjectHimalaya components

import os
import sys
from AIDEV_State import AIDevState

def Main():
    """Main integration function."""
    # Initialize AIDEV-State
    StateManager = AIDevState()
    
    # Define component paths
    ComponentPaths = {
        "AIDEV-Validate": os.path.expanduser("~/Desktop/AIDEV-Validate"),
        # Add other components as needed
    }
    
    # Register components
    for ComponentName, ComponentPath in ComponentPaths.items():
        if os.path.exists(ComponentPath):
            ComponentTracker = StateManager.RegisterComponent(ComponentName, ComponentPath)
            print(f"Registered {ComponentName} at {ComponentPath}")
            
            # Check for changes
            Changes = ComponentTracker.CheckChanges()
            print(f"  - Added files: {len(Changes['Added'])}")
            print(f"  - Modified files: {len(Changes['Modified'])}")
            print(f"  - Unchanged files: {len(Changes['Unchanged'])}")
        else:
            print(f"Component directory not found: {ComponentPath}")
    
    # Generate continuity document
    DocumentPath = StateManager.GenerateContinuityDocument()
    print(f"Generated continuity document: {DocumentPath}")
    
    print("\nIntegration complete. AIDEV-State is now tracking ProjectHimalaya components.")

if __name__ == "__main__":
    Main()
```

Run this script to integrate AIDEV-State with your ProjectHimalaya components.

---

*"Code is not merely functional—it is a visual medium that developers interact with for extended periods. The choices made in these standards prioritize the axis of symmetry, character distinction, readability at scale, and visual hierarchy."*

— Herbert J. Bowers
