import { promises as fs } from 'node:fs';
import path from 'node:path';

/** Read JSON, returning `fallback` when the file is missing. Corrupt files are moved aside. */
export async function readJson(file, fallback) {
  let text;
  try {
    text = await fs.readFile(file, 'utf8');
  } catch (err) {
    if (err.code === 'ENOENT') return fallback;
    throw err;
  }
  try {
    return JSON.parse(text);
  } catch {
    const aside = `${file}.corrupt-${Date.now()}`;
    await fs.rename(file, aside).catch(() => {});
    console.warn(`[wallboard] ${path.basename(file)} was not valid JSON; moved to ${aside}`);
    return fallback;
  }
}

/**
 * Serialised, atomic JSON writer. Rapid successive writes are coalesced: only the
 * latest snapshot is written, and never two writes to the same file at once.
 */
export class JsonWriter {
  constructor(file) {
    this.file = file;
    this.pending = null;
    this.running = null;
  }

  write(getData) {
    this.pending = getData;
    if (!this.running) this.running = this.#drain();
    return this.running;
  }

  async #drain() {
    try {
      while (this.pending) {
        const get = this.pending;
        this.pending = null;
        const data = JSON.stringify(typeof get === 'function' ? get() : get);
        const tmp = `${this.file}.${process.pid}.tmp`;
        await fs.mkdir(path.dirname(this.file), { recursive: true });
        await fs.writeFile(tmp, data);
        await fs.rename(tmp, this.file);
      }
    } finally {
      this.running = null;
    }
  }

  async flush() {
    while (this.running) await this.running;
  }
}
