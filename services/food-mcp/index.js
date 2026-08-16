const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");
const puppeteer = require("puppeteer");

// Initialize MCP Server
const server = new Server(
  {
    name: "food-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

let browser = null;

async function getBrowser() {
  if (!browser) {
    browser = await puppeteer.launch({ headless: true });
  }
  return browser;
}

// Define the tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "search_swiggy",
        description: "Search for food or restaurants on Swiggy",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "The food or restaurant to search for" },
            latitude: { type: "number", description: "Optional: Latitude of the user" },
            longitude: { type: "number", description: "Optional: Longitude of the user" }
          },
          required: ["query"],
        },
      },
      {
        name: "search_zomato",
        description: "Search for food or restaurants on Zomato",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "The food or restaurant to search for" },
            latitude: { type: "number", description: "Optional: Latitude of the user" },
            longitude: { type: "number", description: "Optional: Longitude of the user" }
          },
          required: ["query"],
        },
      },
      {
        name: "place_order",
        description: "Place a food order on Swiggy or Zomato",
        inputSchema: {
          type: "object",
          properties: {
            platform: { type: "string", enum: ["swiggy", "zomato"] },
            restaurant: { type: "string" },
            item: { type: "string" },
          },
          required: ["platform", "restaurant", "item"],
        },
      }
    ],
  };
});

// Implement the tools
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "search_swiggy") {
    const { query, latitude, longitude } = request.params.arguments || {};
    const locString = (latitude && longitude) ? ` (at coordinates: ${latitude}, ${longitude})` : "";
    return {
      content: [{ type: "text", text: `(Mock) Swiggy Search Results for "${query}"${locString}:\n1. Spicy Biryani House - 4.5 Stars - 30 mins\n2. The Biryani Project - 4.2 Stars - 45 mins` }],
    };
  }
  
  if (request.params.name === "search_zomato") {
    const { query, latitude, longitude } = request.params.arguments || {};
    const locString = (latitude && longitude) ? ` (at coordinates: ${latitude}, ${longitude})` : "";
    return {
      content: [{ type: "text", text: `(Mock) Zomato Search Results for "${query}"${locString}:\n1. Behrouz Biryani - 4.6 Stars - 25 mins\n2. Paradise Biryani - 4.1 Stars - 40 mins` }],
    };
  }

  if (request.params.name === "place_order") {
    const { platform, restaurant, item } = request.params.arguments;
    return {
      content: [{ type: "text", text: `(Mock) Order placed successfully on ${platform} for ${item} from ${restaurant}. Estimated delivery: 35 minutes.` }],
    };
  }

  throw new Error(`Tool not found: ${request.params.name}`);
});

// Start the server
async function run() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Food MCP server running on stdio");
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
