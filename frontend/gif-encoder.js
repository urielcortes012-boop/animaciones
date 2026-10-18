/**
 * Lightweight Client-Side Animated GIF Encoder
 * Genera archivos GIF animados directamente en el navegador / Electron sin dependencias externas.
 */
class SimpleGifEncoder {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.frames = [];
  }

  addFrame(ctx, delayMs = 100) {
    const imgData = ctx.getImageData(0, 0, this.width, this.height);
    this.frames.push({
      data: imgData.data,
      delay: Math.round(delayMs / 10) // en centésimas de segundo (1/100s)
    });
  }

  buildBlob() {
    const bytes = [];
    
    // Header GIF89a
    this._writeString(bytes, "GIF89a");
    
    // Logical Screen Descriptor
    this._writeWord(bytes, this.width);
    this._writeWord(bytes, this.height);
    bytes.push(0x70); // Global Color Table Flag: 0, Color Resolution: 7 (8 bits), Sort: 0, Size: 0
    bytes.push(0x00); // Background Color Index
    bytes.push(0x00); // Pixel Aspect Ratio
    
    // Netscape Application Block for Looping
    bytes.push(0x21); // Extension Introducer
    bytes.push(0xff); // Application Extension Label
    bytes.push(0x0b); // Block Size (11 bytes)
    this._writeString(bytes, "NETSCAPE2.0");
    bytes.push(0x03); // Sub-block length
    bytes.push(0x01); // Loop sub-block ID
    this._writeWord(bytes, 0); // Loop count (0 = infinite)
    bytes.push(0x00); // Block Terminator
    
    // Process each frame
    for (let f = 0; f < this.frames.length; f++) {
      const frame = this.frames[f];
      this._writeFrame(bytes, frame);
    }
    
    // Trailer
    bytes.push(0x3b);
    
    return new Blob([new Uint8Array(bytes)], { type: "image/gif" });
  }

  _writeFrame(bytes, frame) {
    // Quantize 24-bit RGB to 64 colors for speed and compact GIF size
    const numPixels = this.width * this.height;
    const pixels = new Uint8Array(numPixels);
    const palette = [];
    const colorMap = new Map();
    
    let colorCount = 0;
    const maxColors = 64;
    
    for (let i = 0; i < numPixels; i++) {
      const pi = i * 4;
      // Reducción a 6 bits (2 bits R, 2 bits G, 2 bits B)
      const r = frame.data[pi] & 0xc0;
      const g = frame.data[pi + 1] & 0xc0;
      const b = frame.data[pi + 2] & 0xc0;
      const key = (r << 16) | (g << 8) | b;
      
      let idx = colorMap.get(key);
      if (idx === undefined) {
        if (colorCount < maxColors) {
          idx = colorCount++;
          colorMap.set(key, idx);
          palette.push(r, g, b);
        } else {
          idx = 0; // fallback
        }
      }
      pixels[i] = idx;
    }
    
    // Pad palette to power of 2 (64 = 2^6)
    const tableSize = 64;
    while (palette.length < tableSize * 3) {
      palette.push(0, 0, 0);
    }

    // Graphic Control Extension
    bytes.push(0x21); // Extension Introducer
    bytes.push(0xf9); // Graphic Control Label
    bytes.push(0x04); // Byte size
    bytes.push(0x00); // Disposal: 0, Transparent: 0
    this._writeWord(bytes, frame.delay); // Delay time
    bytes.push(0x00); // Transparent color index
    bytes.push(0x00); // Block Terminator

    // Image Descriptor
    bytes.push(0x2c); // Image Separator
    this._writeWord(bytes, 0); // Left position
    this._writeWord(bytes, 0); // Top position
    this._writeWord(bytes, this.width);
    this._writeWord(bytes, this.height);
    bytes.push(0x85); // Local Color Table Flag: 1, Interlace: 0, Size: 5 (2^(5+1) = 64)

    // Local Color Table
    for (let i = 0; i < palette.length; i++) {
      bytes.push(palette[i]);
    }

    // LZW Minimum Code Size
    const lzwMinCodeSize = 6;
    bytes.push(lzwMinCodeSize);

    // Simple LZW encoder
    this._writeLZW(bytes, pixels, lzwMinCodeSize);
  }

  _writeLZW(bytes, pixels, minCodeSize) {
    const clearCode = 1 << minCodeSize;
    const endCode = clearCode + 1;
    let codeSize = minCodeSize + 1;
    let maxCode = (1 << codeSize) - 1;

    let dict = new Map();
    let nextCode = endCode + 1;

    let outputBits = 0;
    let bitBuffer = 0;
    const subBlock = [];

    const emitBits = (code, bits) => {
      bitBuffer |= code << outputBits;
      outputBits += bits;
      while (outputBits >= 8) {
        subBlock.push(bitBuffer & 0xff);
        bitBuffer >>= 8;
        outputBits -= 8;
        if (subBlock.length === 254) {
          bytes.push(subBlock.length);
          for (let b of subBlock) bytes.push(b);
          subBlock.length = 0;
        }
      }
    };

    emitBits(clearCode, codeSize);

    let prefix = pixels[0];
    for (let i = 1; i < pixels.length; i++) {
      const c = pixels[i];
      const key = (prefix << 8) | c;
      if (dict.has(key)) {
        prefix = dict.get(key);
      } else {
        emitBits(prefix, codeSize);
        if (nextCode < 4096) {
          dict.set(key, nextCode++);
          if (nextCode > maxCode && codeSize < 12) {
            codeSize++;
            maxCode = (1 << codeSize) - 1;
          }
        } else {
          emitBits(clearCode, codeSize);
          dict.clear();
          codeSize = minCodeSize + 1;
          maxCode = (1 << codeSize) - 1;
          nextCode = endCode + 1;
        }
        prefix = c;
      }
    }
    emitBits(prefix, codeSize);
    emitBits(endCode, codeSize);

    if (outputBits > 0) {
      subBlock.push(bitBuffer & 0xff);
    }
    if (subBlock.length > 0) {
      bytes.push(subBlock.length);
      for (let b of subBlock) bytes.push(b);
    }
    bytes.push(0x00); // Block Terminator
  }

  _writeString(bytes, str) {
    for (let i = 0; i < str.length; i++) {
      bytes.push(str.charCodeAt(i));
    }
  }

  _writeWord(bytes, num) {
    bytes.push(num & 0xff);
    bytes.push((num >> 8) & 0xff);
  }
}

window.SimpleGifEncoder = SimpleGifEncoder;
