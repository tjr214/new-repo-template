This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

## Additional Info

# Directory Structure
```
docs/
tasks/
better-auth-implementation.md
main.py
README.md
```

# Files

## File: better-auth-implementation.md
````markdown
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
````

## File: main.py
````python
from rich import print

from dotenv import load_dotenv
load_dotenv()

print("Hello, new repo!")
````

## File: README.md
````markdown
# New Repository Template with Task Master AI & Context7

A comprehensive project template with pre-configured Task Master AI integration for structured, task-driven development. This template provides a fully set up environment to help you start new projects with an AI-assisted development workflow.

## Features

- **Cursor AI Integration**: Custom Cursor rules for enhanced AI-assisted development
- **Pre-configured for Task Master AI**: Manage your development process with AI-generated tasks and structured workflows
- **MCP Server Setup**: Model Context Protocol server configurations for Task Master and Context7
- **PRD-to-Tasks Workflow**: Convert product requirements documents into structured tasks automatically
- **Task Management**: Comprehensive tools for task creation, expansion, tracking, and dependency management

## Getting Started

1. **Clone this template**:

   ```bash
   git clone https://github.com/tjr214/new-repo-template.git my-project
   cd my-project
   ```

2. **Configure environment variables**:
   Copy the example environment file and add your API keys:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file and add:

   - `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude
   - `PERPLEXITY_API_KEY`: (Optional but recommended) Your Perplexity API key for research-backed features

3. **Install dependencies**:

   Run the following scripts to install and update required packages:

   ```bash
   # Install/update Task Master (MANDATORY)
   ./update_packages.sh taskmaster

   # Install/update npm packages (MANDATORY)
   ./update_packages.sh npm

   # Optional: For Python components (only if your project uses Python)
   ./update_packages.sh python
   ```

4. **Create your PRD**:

   - Use the `prompts/create-new-PRD-file.md` prompt to chat with the AI to create your PRD.
   - Afterwards, edit `scripts/prd.txt` to make any required manual changes.

5. **Generate initial tasks**:

   - Use the `prompts/initial-Task-generation.md` prompt to begin the initial task generation process and create the `tasks.json` file.
   - Next, use the `prompts/generate-individual-Tasks.md` prompt to generate individual task files from `tasks.json`.

6. **Start developing with Cursor AI**:
   - Open the project in Cursor IDE and leverage the custom rules and Task Master integration.

## Using Task Master

### Key Commands (CLI)

- **List tasks**: `npx task-master list`
- **Generate task files**: `npx task-master generate`
- **Parse PRD**: `npx task-master parse-prd scripts/prd.txt`
- **Show next task**: `npx task-master next`
- **Expand a task**: `npx task-master expand --id=<id>`
- **Update task status**: `npx task-master set-status --id=<id> --status=<status>`

### Development Workflow

1. **Start with a PRD**: Create a detailed PRD in `scripts/prd.txt` using the `create-new-PRD-file.md` prompt. If you already have a PRD file, place it in `scripts/prd.txt` and use the `read-PRD-file.md` prompt to process it.
2. **Generate tasks**: Parse the PRD to generate structured tasks using the `initial-Task-generation.md` and `generate-individual-Tasks.md` prompts.
3. **Analyze complexity**: Use task complexity analysis to identify tasks that need to be broken down
   - E.g., "Task 5 seems complex. Can you break it down into subtasks?"
   - "Can you help me expand Task 4?"
   - "Can you analyze the complexity of our Tasks?"
   - "I'd like to implement Task 6. What does it involve?"
   - etc.
4. **Stay on track**:
   - "What tasks are available to work on next?"
   - "What is the status of Task 5?"
   - "Show me all high priority Tasks."
   - "Task 2 is now complete. Please update its status."
   - etc.
5. **Update as you go**: Keep tasks up-to-date as your implementation evolves

## Using Context7 for Library Documentation

Context7 is integrated into the workflow to ensure you're always working with the most current library documentation:

- **Automatic Documentation Lookup**: Whenever you mention a library, package, framework, or module in your conversations with the AI, Context7 automatically fetches up-to-date documentation.
- **How It Works**: The system uses a two-step process:
  1. First, it resolves the library name to a Context7-compatible library ID
  2. Then it retrieves the latest documentation for that library
- **Always Current Information**: This ensures you never work with outdated library knowledge or examples
- **Trigger Patterns**: Context7 activates automatically when you:
  - Ask how to use a specific library
  - Request implementation examples
  - Ask for troubleshooting help with a library
  - Mention any library name in the context of implementation
- **No Manual Activation Required**: You don't need to explicitly request documentation - just mention the library in your question or task

This seamless integration helps maintain code quality and prevents issues caused by outdated implementation patterns or deprecated functions.

## Customization

### Task Master Configuration

Edit `.env` to configure Task Master behavior:

- Model selection (Claude and Perplexity)
- Token limits and temperature
- Default subtask count and priority

### MCP Server Configuration

MCP server configurations are defined in `.cursor/mcp.json`:

- Task Master MCP server for task management integration
- Context7 for library documentation lookup

### Custom Cursor Rules

Custom rules in `.cursor/rules/` enhance the AI's capabilities:

- `dev_workflow.mdc`: Guide for Task Master development workflows
- `taskmaster.mdc`: Comprehensive Task Master tool reference
- `cursor_rules.mdc`: Guidelines for creating and maintaining Cursor rules
- `self_improve.mdc`: Guidance for continuously improving rules
- `global_rules.mdc`: Global rules for all interactions

## Requirements

- Anthropic API key
- [Cursor IDE](https://cursor.sh/) for best experience

## Learn More

- See [README-task-master.md](README-task-master.md) for a complete guide to Task Master
````
