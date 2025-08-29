# """
#     Some base traffic decorators and functions
# """
# from functools import wraps
# import time
# from typing.errors import (
#     RequestError
# )

# def log_request():
#     def decorator(func):
#         import inspect_
#         sig = inspect.signature(func)
#         # db.add_error_log(
#         #     ErrorLog(
#         #       endpoint_name = ""
#         #     )
#         # )
#         pass


# # def rate_limiter(func):
# #     """
# #         Rate limits requests on base api
# #     """
# #     def wrapper(*args, **kwargs):


# def try_with_res_nodes(
#     param_name: str = "nodes",
#     nodes_to_try: List[str],
#     original_node_first: bool = True
# ):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs) -> APIResponse:
#             import inspect
#             sig = inspect.signature(func)
#             param_names = list(sig.parameters.keys())
            
#             # Find the original value for the parameter we want to modify
#             original_node_value = None
#             param_index = None

#             # Check if parameter is in kwargs
#             if param_name in kwargs:
#                 original_node_value = kwargs[param_name]
#             # Check if parameter is in positional args
#             elif param_name in param_names:
#                 param_index = param_names.index(param_name)
#                 if param_index < len(args):
#                     original_node_value = args[param_index]

#             # Build list of values to try
#             if original_node_first and original_node_value is not None:
#                 all_values = [original_node_value] + nodes_to_try
#             else:
#                 all_values = nodes_to_try

#             # Try each value
#             for i, value in enumerate(all_values):
#                 print(f"🔄 Trying {param_name}={value}")
                
#                 # Create modified arguments
#                 new_args = list(args)
#                 new_kwargs = kwargs.copy()

#                 # Update the parameter we're testing
#                 if param_name in kwargs or param_index is None:
#                     # Parameter is in kwargs or we couldn't find it in args
#                     new_kwargs[param_name] = value
#                 else:
#                     # Parameter is in positional args
#                     if param_index < len(new_args):
#                         new_args[param_index] = value
#                     else:
#                         # Parameter position is beyond provided args, add to kwargs
#                         new_kwargs[param_name] = value

#                 # Call function with modified arguments
#                 try:
#                     response = func(*new_args, **new_kwargs)

#                     if rresponse.is_success:
#                         if i > 0 or not original_first:
#                             print(f"✅ Success with {param_name}={value}")
#                         return response.text
#                     else:
#                         print(f"Failed with {param_name}={value}")

#                 except Exception as e:
#                     print(f"Error with {param_name}={value}: {e}")

#             print("All ip attempts failed!")

#             return None
#         return wrapper
#     return decorator


# def smart_exponential_backoff(
#     max_retries: int = 3,
#     base_delay: float = 1.0,
#     max_delay: float = 30.0,
#     retryable_status_codes: Tuple[int, ...] = (429, 500, 502, 503, 504, 408),
#     non_retryable_status_codes: Tuple[int, ...] = (400, 401, 403, 404)
# ):
#     """
#     Smart exponential backoff that considers HTTP status codes
#     """
#     def decorator(func: Callable) -> Callable:
#         @wraps(func)
#         def wrapper(*args, **kwargs) -> APIResponse:
#             last_exception = None
            
#             for attempt in range(max_retries + 1):
#                 try:
#                     # Try the API call
#                     response = func(*args, **kwargs)
                    
#                     # Handle requests.Response objects
#                     if isinstance(response, requests.Response):
#                         if response.status_code in retryable_status_codes:
#                             # Convert to retryable exception
#                             error_msg = f"HTTP {response.status_code}: {response.reason}"
                            
#                             # Special handling for rate limiting
#                             if response.status_code == 429:
#                                 retry_after = response.headers.get('Retry-After')
#                                 if retry_after:
#                                     try:
#                                         retry_delay = int(retry_after)
#                                         error_msg += f" (Retry-After: {retry_delay}s)"
#                                         # Use the server's suggested delay
#                                         time.sleep(retry_delay)
#                                         continue
#                                     except ValueError:
#                                         pass
                            
#                             raise RetryableAPIError(error_msg)
                        
#                         elif response.status_code in non_retryable_status_codes:
#                             # Don't retry these errors
#                             error_msg = f"HTTP {response.status_code}: {response.reason}"
#                             return APIResponse(
#                                 success=False,
#                                 status_code=response.status_code,
#                                 error=error_msg
#                             )
                        
#                         # Success case
#                         try:
#                             data = response.json()
#                             return APIResponse(
#                                 success=True,
#                                 data=data,
#                                 status_code=response.status_code
#                             )
#                         except ValueError:
#                             return APIResponse(
#                                 success=True,
#                                 data={'raw_content': response.text},
#                                 status_code=response.status_code
#                             )
                    
#                     # For non-response objects, return as-is
#                     return response
                    
#                 except (RetryableAPIError, requests.Timeout, requests.ConnectionError) as e:
#                     last_exception = e
                    
#                     if attempt == max_retries:
#                         return APIResponse(
#                             success=False,
#                             error=f"Failed after {max_retries} retries: {str(e)}"
#                         )
                    
#                     # Calculate exponential backoff delay
#                     delay = min(base_delay * (2.0 ** attempt), max_delay)
#                     delay = delay * (0.5 + random.random() * 0.5)  # Add jitter
                    
#                     print(f"⚠️  {func.__name__} attempt {attempt + 1} failed: {e}")
#                     print(f"   Retrying in {delay:.2f} seconds...")
                    
#                     time.sleep(delay)
                
#                 except Exception as e:
#                     # Non-retryable error
#                     return APIResponse(
#                         success=False,
#                         error=f"Non-retryable error: {str(e)}"
#                     )
            
#             return APIResponse(
#                 success=False,
#                 error=f"Max retries exceeded: {str(last_exception)}"
#             )
        
#         return wrapper
#     return decorator