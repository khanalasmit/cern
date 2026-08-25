# System Architecture Image Prompt

Use this prompt with the local ChatGPT image-generation app. The supplied
reference image is a style reference only; do not copy its AWS services,
logos, or wording. The final design direction is monochrome and vertical.

```text
Use case: infographic-diagram
Asset type: professional software system architecture diagram for a technical report
Input image: the supplied reference image is a STYLE REFERENCE ONLY; borrow its clean architecture layout and generous whitespace, but use a monochrome vertical-flow treatment. Do not copy AWS services, logos, decorative emojis, random images, or text.

Primary request: Create a clean, readable 16:9 architecture infographic for the project "OKS MCP Server". Show the path from a developer's coding agent to a natural-language OKS query running on CERN infrastructure and back to filtered results.

Composition: one clean centered vertical flow with black arrows and black text. Stack these stages from top to bottom: "USER", "CODING AGENT / MCP CLIENT", "LOCAL MCP ENDPOINT 127.0.0.1:18001/mcp", "PRIVATE SSH LOCAL PORT FORWARD", then a large outlined section titled "CERN LXPLUS" containing "STREAMABLE HTTP MCP SERVER 127.0.0.1:8001", "OKSQUERYSERVICE", "OKS PIPELINE", "LLM TRANSLATION + VALIDATION", "OKS EXECUTOR", "FILTERED STRUCTURED RESULTS", and "RETURN TO AGENT". Show "OpenAI-compatible LLM API" and "CVMFS TDAQ / OKS data" as small side dependencies connected with black dashed lines.

Add a bottom data block titled "CVMFS TDAQ / OKS Schema + Data" connected to the executor. Add a small external block titled "OpenAI-compatible LLM API" connected to the translation block with a subtle outbound HTTPS dotted arrow. Use arrows to show: User → Coding Agent → SSH Tunnel → MCP → Service → Retrieval → Translation/Validation → Executor → Filtered Results → MCP → Agent.

Style/medium: polished flat vector technical infographic, modern software-architecture presentation style, crisp geometry, thin black outlines, no icons, no emojis, no decorative imagery, no photorealism, no 3D rendering.
Color palette: black, white, and neutral light gray only; optional very light gray section shading. No pastel service colors.
Typography: high-contrast sans-serif, consistent medium-weight labels, large readable section headings, exact spelling, no decorative handwritten text.

Important exact labels: "OKS MCP Server", "Developer Workstation", "Private SSH Tunnel", "CERN LXPLUS", "Coding Agent / MCP Client", "OksQueryService", "Schema + Few-shot Retrieval", "LLM Translation + Validation", "OKS Executor: config / oks_dump", "Filtered Structured Results", "CVMFS TDAQ / OKS Schema + Data".

Constraints: portrait or tall vertical layout, balanced whitespace, no cropped elements, no overlapping arrows, all connectors and dashed lines black, no duplicate blocks, no AWS logos, no vendor logos, no credentials, no domain names, no API keys, no watermark. Keep the architecture semantically correct and do not invent databases, load balancers, containers, or cloud regions.
Avoid: random images, emoji-like symbols, decorative icons, colorful blocks, photorealistic imagery, dark background, dense paragraphs, tiny unreadable text, inaccurate arrows, invented infrastructure, illegible pseudo-text, spelling errors, watermarks.
```
