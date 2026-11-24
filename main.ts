import * as fs from 'node:fs';
import * as path from 'node:path';

function main(): void {
  const entryPath = path.resolve(import.meta.dirname, 'entry.png');
  if (!fs.existsSync(entryPath)) {
    console.error(`entry.png not found at ${entryPath}`);
    process.exit(1);
  }

  const bytes = fs.readFileSync(entryPath);
  const size = bytes.length;
  if (size === 0 || size > 1048576) {
    console.error(`Invalid file size: ${size} bytes (must be > 0 and <= 1,048,576 bytes)`);
    process.exit(1);
  }

  // Verify PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
  // or JPEG magic bytes: FF D8 FF
  const isPng =
    bytes.length >= 8 &&
    bytes[0] === 0x89 &&
    bytes[1] === 0x50 &&
    bytes[2] === 0x4e &&
    bytes[3] === 0x47 &&
    bytes[4] === 0x0d &&
    bytes[5] === 0x0a &&
    bytes[6] === 0x1a &&
    bytes[7] === 0x0a;

  const isJpeg =
    bytes.length >= 3 &&
    bytes[0] === 0xff &&
    bytes[1] === 0xd8 &&
    bytes[2] === 0xff;

  if (!isPng && !isJpeg) {
    console.error('File does not match PNG or JPEG magic bytes');
    process.exit(1);
  }

  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
  fs.mkdirSync(outDir, { recursive: true });
  const destPath = path.join(outDir, 'entry.png');
  fs.writeFileSync(destPath, bytes);
  console.log(`Wrote ${size} bytes to ${destPath}`);
}

main();
