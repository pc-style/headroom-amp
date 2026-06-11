import { describe, expect, it, vi } from "vitest";

import {
  compressTextViaProxy,
  minCompressChars,
  resolveProxyUrl,
  retrieveFromProxy,
  serializeToolOutput,
  tokensSavedFromResponse,
} from "../lib.js";

describe("resolveProxyUrl", () => {
  it("prefers explicit proxy URL", () => {
    expect(
      resolveProxyUrl({
        "headroom.proxyUrl": "http://127.0.0.1:9999/",
      }),
    ).toBe("http://127.0.0.1:9999");
  });

  it("falls back to configured port", () => {
    expect(resolveProxyUrl({ "headroom.proxyPort": 9001 })).toBe(
      "http://127.0.0.1:9001",
    );
  });
});

describe("serializeToolOutput", () => {
  it("stringifies objects for compression", () => {
    expect(serializeToolOutput({ ok: true })).toBe('{"ok":true}');
  });
});

describe("tokensSavedFromResponse", () => {
  it("reads snake_case and camelCase fields", () => {
    expect(tokensSavedFromResponse({ tokens_saved: 12 })).toBe(12);
    expect(tokensSavedFromResponse({ tokensSaved: 8 })).toBe(8);
  });
});

describe("compressTextViaProxy", () => {
  it("returns compressed text when proxy responds", async () => {
    const fetchImpl = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        tokens_saved: 400,
        messages: [{ role: "user", content: "compressed body" }],
      }),
    });

    const result = await compressTextViaProxy(
      "http://127.0.0.1:8787",
      "x".repeat(600),
      "claude-sonnet-4-5",
      fetchImpl,
    );

    expect(result.text).toBe("compressed body");
    expect(result.tokensSaved).toBe(400);
  });
});

describe("retrieveFromProxy", () => {
  it("rejects invalid hashes", async () => {
    const result = await retrieveFromProxy("http://127.0.0.1:8787", "bad");
    expect(result).toContain("Invalid hash format");
  });
});

describe("minCompressChars", () => {
  it("uses workspace override when present", () => {
    expect(minCompressChars({ "headroom.minCompressChars": 1200 })).toBe(1200);
  });
});
