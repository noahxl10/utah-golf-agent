# Utah Golf Booking

## Overview

Utah Golf Booking is a web application that aggregates golf course tee times from multiple providers across Utah, solving the problem of fragmented booking systems. The application scrapes tee times from various golf course providers (ChronoGolf, ForeUp, Eaglewood) and presents them in a unified interface, allowing golfers to search and compare available slots across multiple courses without visiting individual websites.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Flask API**: RESTful API built with Flask serving as the primary backend
- **Modular Scraper System**: Organized scraper modules for different golf course providers:
  - ChronoGolf (V1 and V2 APIs) - handles multiple municipal courses
  - ForeUp API - handles Stonebridge Golf Club and others
  - Eaglewood - custom scraper for Eaglewood Golf Course
- **Provider Abstraction**: Each provider has its own API class with standardized TeeTime output format
- **Configuration Management**: Centralized course configuration mapping courses to their respective providers and settings

### Data Models
- **TeeTime Model**: Standardized data structure using Pydantic BaseModel containing:
  - Timing information (start_time, date)
  - Course details (name, holes available)
  - Pricing (green_fee, cart fee, total price)
  - Availability and booking constraints
- **Course Configuration**: Structured mapping of golf courses to their API providers and endpoints

### Authentication System
- **Provider-Specific Auth**: Handles authentication for different providers (notably Stonebridge requiring bearer tokens and session cookies)
- **Token Caching**: Implements token caching system to avoid repeated authentication requests

### Caching Strategy
- **Time-Based Cache**: 45-minute cache expiration for search results
- **Background Refresh**: Potential for background caching to improve response times
- **Trade-off Design**: Balances cost efficiency with occasional slower user responses

### Error Handling
- **Custom Exception Classes**: Structured error hierarchy with BaseError, RequestError, RateLimitError, and CourseNotFoundError
- **Retry Logic**: Distinguishes between retryable and non-retryable API errors

## External Dependencies

### Third-Party APIs
- **ChronoGolf API**: V1 and V2 endpoints for municipal courses (Bonneville, Glendale, Rose Park, Forest Dale, Old Mill)
- **ForeUp Software API**: Golf booking platform API for private courses
- **Eaglewood Golf Course**: Custom API integration

### Authentication Services
- **Stonebridge Golf Club**: Requires OAuth-style authentication with bearer tokens and session management

### Development Tools
- **Flask**: Web framework for API development
- **Pydantic**: Data validation and serialization
- **Requests**: HTTP client for API communications

### Infrastructure Dependencies
- **Environment Variables**: Configuration management for API endpoints, credentials, and tokens
- **File System**: Token caching and configuration file storage

### Potential Future Dependencies
- **Node.js**: Mentioned as potential Flask replacement
- **Payment Processing**: For future checkout integration
- **Database System**: Not currently implemented but likely needed for user management and booking history