import AppKit
import CoreText

let args = CommandLine.arguments
guard args.count == 5, let width = Int(args[3]), let height = Int(args[4]) else {
    fatalError("usage: render_sheet.swift input.svg output.png width height")
}
let directory = URL(fileURLWithPath: args[1]).deletingLastPathComponent()
for name in ["BarlowCondensed-ExtraBoldItalic.ttf", "Barlow-Regular.ttf", "Barlow-SemiBold.ttf"] {
    let url = directory.appendingPathComponent("Fonts/" + name)
    CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
}
guard let source = NSImage(contentsOf: URL(fileURLWithPath: args[1])) else { fatalError("SVG failed to load") }
let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: width, pixelsHigh: height,
                             bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true,
                             isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmap)
source.draw(in: NSRect(x: 0, y: 0, width: width, height: height))
NSGraphicsContext.restoreGraphicsState()
try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: args[2]))
print("Rendered " + args[2])
