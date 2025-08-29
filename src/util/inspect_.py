from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import sys


@dataclass
class Parameter:
    """Represents a function parameter"""
    name: str
    default: Any = None
    has_default: bool = False
    kind: str = "POSITIONAL_OR_KEYWORD"  # Simplified - just one kind
    
    # Parameter kinds (simplified)
    POSITIONAL_ONLY = "POSITIONAL_ONLY"
    POSITIONAL_OR_KEYWORD = "POSITIONAL_OR_KEYWORD"
    VAR_POSITIONAL = "VAR_POSITIONAL"  # *args
    KEYWORD_ONLY = "KEYWORD_ONLY"
    VAR_KEYWORD = "VAR_KEYWORD"  # **kwargs

@dataclass
class Signature:
    """Represents a function signature"""
    parameters: Dict[str, Parameter]
    
    def bind(self, *args, **kwargs) -> 'BoundArguments':
        """Bind provided arguments to parameters"""
        bound = BoundArguments(self)
        
        param_names = list(self.parameters.keys())
        
        # Bind positional arguments
        for i, arg in enumerate(args):
            if i < len(param_names):
                param_name = param_names[i]
                param = self.parameters[param_name]
                
                # Skip *args and **kwargs parameters for now
                if param.kind not in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                    bound.arguments[param_name] = arg
        
        # Bind keyword arguments
        for key, value in kwargs.items():
            if key in self.parameters:
                bound.arguments[key] = value
        
        return bound
    
    def apply_defaults(self, bound: 'BoundArguments') -> None:
        """Apply default values to unbound parameters"""
        for param_name, param in self.parameters.items():
            if param_name not in bound.arguments and param.has_default:
                bound.arguments[param_name] = param.default

@dataclass
class BoundArguments:
    """Arguments bound to a signature"""
    signature: Signature
    arguments: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.arguments is None:
            self.arguments = {}
    
    def apply_defaults(self):
        """Apply default parameter values"""
        self.signature.apply_defaults(self)

def signature(func) -> Signature:
    """
    Get the signature of a function (simplified implementation)
    
    Args:
        func: Function to inspect
        
    Returns:
        Signature object containing parameter information
    """
    
    # Get function code object
    if hasattr(func, '__code__'):
        code = func.__code__
    else:
        raise TypeError(f"'{type(func).__name__}' object is not a function")
    
    # Get parameter names from code object
    param_names = code.co_varnames[:code.co_argcount]
    
    # Get default values
    defaults = func.__defaults__ or []
    defaults_dict = {}
    
    # Map defaults to parameter names (defaults apply to last N parameters)
    if defaults:
        default_offset = len(param_names) - len(defaults)
        for i, default_value in enumerate(defaults):
            param_index = default_offset + i
            if param_index < len(param_names):
                defaults_dict[param_names[param_index]] = default_value
    
    # Create Parameter objects
    parameters = {}
    for name in param_names:
        has_default = name in defaults_dict
        default_value = defaults_dict.get(name)
        
        parameters[name] = Parameter(
            name=name,
            default=default_value,
            has_default=has_default,
            kind=Parameter.POSITIONAL_OR_KEYWORD
        )
    
    # Handle *args if present
    if code.co_flags & 0x04:  # CO_VARARGS flag
        varargs_name = code.co_varnames[code.co_argcount]
        parameters[varargs_name] = Parameter(
            name=varargs_name,
            kind=Parameter.VAR_POSITIONAL
        )
    
    # Handle **kwargs if present  
    if code.co_flags & 0x08:  # CO_VARKEYWORDS flag
        kwargs_index = code.co_argcount
        if code.co_flags & 0x04:  # If *args exists, **kwargs is one position later
            kwargs_index += 1
        
        if kwargs_index < len(code.co_varnames):
            kwargs_name = code.co_varnames[kwargs_index]
            parameters[kwargs_name] = Parameter(
                name=kwargs_name,
                kind=Parameter.VAR_KEYWORD
            )

    return Signature(parameters)

# # Test functions for demonstration
# def test_signature():
#     """Test the signature function with various function types"""
    
#     # Test function 1: Simple function with defaults
#     def simple_func(a, b=10, c="hello"):
#         return a + b
    
#     # Test function 2: Function with *args and **kwargs
#     def complex_func(x, y=5, *args, **kwargs):
#         return x * y
    
#     # Test function 3: No parameters
#     def no_params():
#         return "nothing"
    
#     print("="*50)
#     print("TESTING SIMPLIFIED INSPECT.SIGNATURE()")
#     print("="*50)
    
#     # Test simple function
#     print("\n1. Simple function with defaults:")
#     print("def simple_func(a, b=10, c='hello'):")
    
#     sig = signature(simple_func)
#     print(f"Parameters: {list(sig.parameters.keys())}")
    
#     for name, param in sig.parameters.items():
#         default_info = f" (default: {param.default})" if param.has_default else ""
#         print(f"  - {param.name}: {param.kind}{default_info}")
    
#     # Test binding
#     print("\nBinding arguments (1, 20):")
#     bound = sig.bind(1, 20)
#     bound.apply_defaults()
#     print(f"Bound arguments: {bound.arguments}")
    
#     # Test complex function
#     print("\n2. Complex function with *args, **kwargs:")
#     print("def complex_func(x, y=5, *args, **kwargs):")
    
#     sig2 = signature(complex_func)
#     print(f"Parameters: {list(sig2.parameters.keys())}")
    
#     for name, param in sig2.parameters.items():
#         default_info = f" (default: {param.default})" if param.has_default else ""
#         print(f"  - {param.name}: {param.kind}{default_info}")
    
#     # Test no parameters
#     print("\n3. Function with no parameters:")
#     print("def no_params():")
    
#     sig3 = signature(no_params)
#     print(f"Parameters: {list(sig3.parameters.keys())}")
#     if not sig3.parameters:
#         print("  (No parameters)")

# if __name__ == "__main__":
#     test_signature()