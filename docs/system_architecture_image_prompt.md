# System Architecture Image Prompt

Use this prompt with the local ChatGPT image-generation app. The supplied
reference image is a style reference only; do not copy its AWS services,
logos, or wording.

```text
Use case: infographic-diagram
Asset type: professional software system architecture diagram for a technical report
Input image: the supplied reference image is a STYLE REFERENCE ONLY; borrow its lavender outer background, white rounded canvas, dashed blue region boundaries, pastel flat service blocks, simple icon-like symbols, dotted arrows, and generous whitespace. Do not copy AWS services, logos, or text.

Primary request: Create a clean, readable 16:9 architecture infographic for the project "OKS MCP Server". Show the path from a developer's coding agent to a natural-language OKS query running on CERN infrastructure and back to filtered results.

Composition: Three clearly separated vertical areas with rounded dashed boundaries:
1) left area titled "Developer Workstation" containing "User", "Coding Agent / MCP Client", and "Local MCP Endpoint 127.0.0.1:18001/mcp";
2) center narrow area titled "Private SSH Tunnel" containing "-L 18001:127.0.0.1:8001";
3) right large area titled "CERN LXPLUS" containing stacked blocks "Streamable HTTP MCP 127.0.0.1:8001", "OksQueryService", "Schema + Few-shot Retrieval", "LLM Translation + Validation", "OKS Executor: config / oks_dump", and "Filtered Structured Results".

Add a bottom data block titled "CVMFS TDAQ / OKS Schema + Data" connected to the executor. Add a small external block titled "OpenAI-compatible LLM API" connected to the translation block with a subtle outbound HTTPS dotted arrow. Use arrows to show: User → Coding Agent → SSH Tunnel → MCP → Service → Retrieval → Translation/Validation → Executor → Filtered Results → MCP → Agent.

Style/medium: polished flat vector technical infographic, modern cloud-architecture presentation style, crisp geometry, thin dark-gray outlines, small pastel icons, no photorealism, no 3D rendering.
Color palette: pale lavender background (#E9DDFF), white central canvas, purple client blocks, warm orange tunnel block, light green CERN service blocks, pale blue data/API blocks, dark charcoal text.
Typography: high-contrast sans-serif, consistent medium-weight labels, large readable section headings, exact spelling, no decorative handwritten text.

Important exact labels: "OKS MCP Server", "Developer Workstation", "Private SSH Tunnel", "CERN LXPLUS", "Coding Agent / MCP Client", "OksQueryService", "Schema + Few-shot Retrieval", "LLM Translation + Validation", "OKS Executor: config / oks_dump", "Filtered Structured Results", "CVMFS TDAQ / OKS Schema + Data".

Constraints: landscape 16:9, balanced whitespace, no cropped elements, no overlapping arrows, no duplicate blocks, no AWS logos, no vendor logos, no credentials, no domain names, no API keys, no watermark. Keep the architecture semantically correct and do not invent databases, load balancers, containers, or cloud regions.
Avoid: photorealistic imagery, dark background, dense paragraphs, tiny unreadable text, inaccurate arrows, invented infrastructure, illegible pseudo-text, spelling errors, watermarks.
```
