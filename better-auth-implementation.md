# Implementing User Authentication with Better-Auth in a Next.js/FastAPI Architecture

## Architecture Overview

This document outlines the implementation of user authentication in a microservice architecture consisting of:

- **Next.js Frontend**: Exposed to the internet, handles user interface and authentication
- **FastAPI Backend**: Not exposed to the internet, handles business logic and data processing
- **PostgreSQL Database**: Stores both authentication data and application data
- **Docker Network**: Provides network isolation and security

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Next.js        │──────│  FastAPI        │──────│  PostgreSQL     │
│  Frontend       │      │  Backend        │      │  Database       │
│  (Better-Auth)  │      │                 │      │                 │
│                 │      │                 │      │                 │
└────────┬────────┘      └─────────────────┘      └─────────────────┘
         │                      ▲                         ▲
         │                      │                         │
         │                      │                         │
         │                      │                         │
         ▼                      │                         │
┌─────────────────┐             │                         │
│                 │             │                         │
│  Internet       │             │                         │
│  (Users)        │             │                         │
│                 │             │                         │
└─────────────────┘             │                         │
                                │                         │
                      No direct internet access           │
                                                          │
                                           Database connections
```

## Better-Auth Implementation

### 1. Authentication Flow

Better-Auth will be implemented in the Next.js frontend to handle:

- User registration
- User login
- Session management
- Password reset
- Email verification
- Social authentication (optional)

The authentication state will be proxied to the FastAPI backend via internal API calls over the Docker network.

### 2. Session Security Features

Better-Auth provides built-in protections against common session-based attacks:

- **Session Fixation Protection**: Automatically generates new session IDs on login
- **Replay Attack Protection**: Uses signed cookies and includes IP/User-Agent validation
- **Secure Session Storage**: Server-side session storage rather than client-side tokens

### 3. Better-Auth Configuration

```typescript
// auth.ts in Next.js app
import { betterAuth } from "better-auth";
import { Pool } from "pg";

export const auth = betterAuth({
	// Database configuration
	database: new Pool({
		host: process.env.DB_HOST,
		port: parseInt(process.env.DB_PORT || "5432"),
		database: process.env.DB_NAME,
		user: process.env.DB_USER,
		password: process.env.DB_PASSWORD,
	}),

	// Session configuration
	session: {
		expiresIn: 60 * 60 * 24 * 7, // 7 days
		updateAge: 60 * 60 * 24, // 1 day
		freshAge: 60 * 60 * 24, // 1 day
	},

	// Cookie security
	advanced: {
		useSecureCookies: true,
		cookies: {
			session_token: {
				attributes: {
					httpOnly: true,
					sameSite: "lax",
				},
			},
		},
	},

	// Email verification (optional)
	emailVerification: {
		sendVerificationEmail: async ({ user, url }) => {
			// Email sending logic
		},
	},
});
```

## Docker Network Architecture

The application uses a Docker network configuration that provides significant security benefits:

### Security Advantages

1. **Protected Backend**: FastAPI backend isn't exposed to the internet, protecting it from direct attacks
2. **Network-Level Isolation**: Only the Next.js container can communicate with the backend
3. **Simplified Authentication**: Communication happens on a trusted network

## Next.js to FastAPI Communication

Since both services are on the same Docker network, a simplified authentication approach can be used:

### API Route Handler in Next.js

```typescript
// pages/api/proxy/[...path].ts
import type { NextApiRequest, NextApiResponse } from "next";
import { auth } from "@/lib/auth";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
	// Verify user is authenticated with Better-Auth
	const session = await auth.getSession({ headers: req.headers });

	if (!session) {
		return res.status(401).json({ error: "Unauthorized" });
	}

	const path = (req.query.path as string[]).join("/");

	try {
		// Call FastAPI backend with internal API key
		const response = await fetch(`http://fastapi:8000/api/${path}`, {
			method: req.method,
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${process.env.INTERNAL_API_KEY}`,
				"X-User-ID": session.user.id,
			},
			body: req.method !== "GET" ? JSON.stringify(req.body) : undefined,
		});

		const data = await response.json();
		return res.status(response.status).json(data);
	} catch (error) {
		console.error("Error proxying to backend:", error);
		return res.status(500).json({ error: "Internal Server Error" });
	}
}
```

### FastAPI Authentication Middleware

```python
# auth.py in FastAPI app
from fastapi import Request, HTTPException, Depends
from functools import lru_cache
import os

@lru_cache()
def get_api_key():
    return os.environ.get("INTERNAL_API_KEY")

async def verify_internal_api_key(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")

    token = auth_header.replace("Bearer ", "")
    if token != get_api_key():
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Get user ID passed from frontend
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user ID")

    # Return user_id for endpoints to use
    return user_id

# Example use in FastAPI endpoint
@app.get("/api/profile")
async def get_profile(user_id: str = Depends(verify_internal_api_key)):
    # user_id is available here
    return {"user_id": user_id, "data": "User profile data"}
```

## Database Integration

Both services need database access but for different purposes:

### 1. Next.js (Frontend)

- Uses Better-Auth for authentication
- Manages auth-related tables (users, sessions, accounts)
- Connects with a database user that has access to auth tables

### 2. FastAPI (Backend)

- Handles business logic
- Manages application data
- Connects with a database user that has broader access

### Database Schema Approach

```
PostgreSQL Database
├── auth_schema (managed by Better-Auth)
│   ├── users
│   ├── sessions
│   └── accounts
└── app_schema (managed by FastAPI)
    ├── products
    ├── orders
    └── other business tables
```

### Better-Auth Database Setup

After configuring the database connection, run these commands to set up the schema:

```bash
# Generate schema files
npx @better-auth/cli generate

# Apply migrations to database
npx @better-auth/cli migrate
```

## Security Considerations

### Protection Against Session Attacks

Better-Auth provides built-in protection against:

1. **Session Fixation**: Regenerates session IDs after authentication
2. **Session Hijacking**: Uses secure, HttpOnly cookies
3. **CSRF Attacks**: Implements SameSite cookie attributes
4. **Replay Attacks**: Includes IP address and User-Agent validation

### Docker Network Security

The Docker network architecture provides additional security:

1. **No Direct Internet Access** to the backend API
2. **Network Segregation** between frontend and backend
3. **Internal API Key** for service-to-service communication
4. **Simplified Attack Surface** by limiting exposed services

## Conclusion

This architecture provides several benefits:

1. **Separation of Concerns**: Authentication handled by Better-Auth, business logic by FastAPI
2. **Enhanced Security**: Backend not directly exposed to the internet
3. **Simplified Integration**: Communication over internal Docker network
4. **Scalability**: Components can be scaled independently
5. **Maintainability**: Clear boundaries between services

By implementing authentication with Better-Auth in the Next.js frontend and proxying authenticated requests to the FastAPI backend, we achieve a secure, maintainable architecture that leverages the strengths of both frameworks while maintaining strict security boundaries.
