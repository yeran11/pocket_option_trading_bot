// Script to create placeholder icons for Electron build
const fs = require('fs');
const path = require('path');

// Create a simple 1x1 PNG as placeholder
const pngBuffer = Buffer.from([
  0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, // PNG signature
  0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52, // IHDR chunk
  0x00, 0x00, 0x01, 0x00, // width: 256
  0x00, 0x00, 0x01, 0x00, // height: 256
  0x08, 0x06, // 8 bits, RGBA
  0x00, 0x00, 0x00, // compression, filter, interlace
  0xD7, 0x98, 0x4F, 0x51, // CRC
  0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82 // IEND
]);

// Write PNG files
fs.writeFileSync(path.join(__dirname, 'electron-ui/assets/icon.png'), pngBuffer);
fs.writeFileSync(path.join(__dirname, 'electron-ui/assets/tray-icon.png'), pngBuffer);

console.log('Created placeholder PNG icons');

// For now, remove the ico requirement by modifying package.json
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
delete packageJson.build.win.icon;
fs.writeFileSync('package.json', JSON.stringify(packageJson, null, 2));

console.log('Updated package.json to skip ICO icon');