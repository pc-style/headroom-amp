import type { PluginAPI } from "./ampcode-plugin.js";

import {
  compressTextViaProxy,
  isCompressionEnabled,
  minCompressChars,
  resolveProxyUrl,
  retrieveFromProxy,
  serializeToolOutput,
  type HeadroomWorkspaceConfig,
} from "./lib.js";

const RETRIEVE_TOOL = "headroom_retrieve";

export default function headroomAmpPlugin(amp: PluginAPI) {
  let totalTokensSaved = 0;
  const statusItem = amp.createStatusItem({ text: "headroom: ready" });

  async function readConfig(): Promise<HeadroomWorkspaceConfig> {
    const config = (await amp.configuration.get()) as HeadroomWorkspaceConfig;
    return config ?? {};
  }

  async function proxyUrl(): Promise<string> {
    return resolveProxyUrl(await readConfig());
  }

  statusItem.update({ text: "headroom: ready" });

  amp.on("tool.result", async (event, ctx) => {
    if (event.status !== "done" || event.tool === RETRIEVE_TOOL) {
      return;
    }

    const config = await readConfig();
    if (!isCompressionEnabled(config)) {
      return;
    }

    const raw = serializeToolOutput(event.output);
    if (!raw || raw.length < minCompressChars(config)) {
      return;
    }

    try {
      const baseUrl = await proxyUrl();
      const { text, tokensSaved } = await compressTextViaProxy(baseUrl, raw);
      if (tokensSaved > 0) {
        totalTokensSaved += tokensSaved;
        statusItem.update({
          text: `headroom: ${totalTokensSaved.toLocaleString()} tokens saved`,
        });
      }

      if (text !== raw) {
        return { status: "done", output: text };
      }
    } catch (error) {
      ctx.logger.log(`[headroom] tool.result compression failed: ${error}`);
    }
  });

  amp.registerTool({
    name: RETRIEVE_TOOL,
    description:
      "Retrieve original uncompressed content from Headroom's compression store. " +
      "Use when compressed tool output mentions a hash and you need full details. " +
      "Pass the 24-character hex hash from the compression marker.",
    inputSchema: {
      type: "object",
      properties: {
        hash: {
          type: "string",
          description: "The 24-character hex hash from the compression marker",
        },
        query: {
          type: "string",
          description: "Optional search query to filter within the original content",
        },
      },
      required: ["hash"],
    },
    async execute(input) {
      const hash = typeof input.hash === "string" ? input.hash : "";
      const query = typeof input.query === "string" ? input.query : undefined;
      const baseUrl = await proxyUrl();
      return retrieveFromProxy(baseUrl, hash, query);
    },
  });

  amp.logger.log("[headroom] Amp plugin loaded");
}
