/**
 * Hash Utilities
 *
 * Content hashing functions using Web Crypto API for cache keys.
 */

/**
 * Compute SHA-256 hash of content.
 *
 * Returns the first 16 characters of the hex digest for compact cache keys.
 *
 * @param content - Content to hash
 * @returns Promise resolving to hash string (16 chars)
 *
 * @example
 * ```typescript
 * const hash = await hashContent("# Hello World\n\nContent here.");
 * // => "a3f4b2c1d5e6f7a8"
 * ```
 */
export async function hashContent(content: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(content);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);

  // Convert to hex string
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');

  // Return first 16 chars for compact keys
  return hashHex.slice(0, 16);
}

/**
 * Hash a specific section of content by byte range.
 *
 * Used for incremental parsing to detect which sections changed.
 *
 * @param content - Full document content
 * @param start - Start byte offset (inclusive)
 * @param end - End byte offset (exclusive)
 * @returns Promise resolving to hash string (16 chars)
 *
 * @example
 * ```typescript
 * const sectionHash = await hashSection(content, 0, 150);
 * // => "b7c2d3e4f5a6b7c8"
 * ```
 */
export async function hashSection(
  content: string,
  start: number,
  end: number
): Promise<string> {
  const section = content.slice(start, end);
  return hashContent(section);
}
