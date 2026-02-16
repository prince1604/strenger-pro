# 📱 Responsive Design breakpoints

## Screen Sizes Supported

### 🖥️ Desktop (> 1024px)
```
├─ Sidebar: Fixed left (visible)
├─ Map: Full height
├─ Stats: 3-column grid
└─ Messages: 70% chat area
```

### 📱 Tablet (≤ 1024px)
```
├─ Sidebar: Slide-out drawer
├─ Hamburger: Visible ☰
├─ Map: 220px height
├─ Stats: 2-column grid
└─ Touch targets: 48px minimum
```

### 📱 Large Phone (≤ 768px)
```
├─ Sidebar: 300px max-width
├─ Avatar: 36px size
├─ Fonts: Reduced sizes
├─ Toasts: Compact
└─ Input: 48px height
```

### 📱 Small Phone (≤ 480px)
```
├─ Sidebar: 90% width (280px max)
├─ Stats: 1-column (full width)
├─ Map: 200px height
├─ Toasts: Full width
└─ Auth: 95% width
```

### 🔄 Landscape Mode
```
├─ Auth card: Scrollable
├─ Map: 150px height
└─ Optimized for short screens
```

---

## Touch Target Sizes (Accessibility)

| Element | Desktop | Mobile | Standard |
|---------|---------|--------|----------|
| Buttons | Variable | 48px | WCAG AA: 44px ✅ |
| Inputs | Variable | 48px | iOS zoom: 16px ✅ |
| Hamburger | N/A | 48px | Touch friendly ✅ |
| Avatar | 48px | 36px | Readable ✅ |
| Close (✕) | N/A | 44px | Easy tap ✅ |

---

## Responsive Behavior

### Sidebar Animation
```
Desktop:  [Always Visible]
Mobile:   [Hidden] → tap ☰ → [Slides In ←]
Close:    tap ✕ or tap outside → [Slides Out →]
```

### Message Display
```
Desktop:
┌─────────────┬──────────────────────┐
│  Sidebar    │   Chat Messages      │
│  (300px)    │   (Flex grow)        │
└─────────────┴──────────────────────┘

Mobile:
┌──────────────────────────────────┐
│  ☰  Chat Header                  │
├──────────────────────────────────┤
│                                  │
│      Chat Messages (100%)        │
│                                  │
├──────────────────────────────────┤
│  [Input Bar]  [Send Button ]     │
└──────────────────────────────────┘
```

---

## CSS Media Queries Priority

```css
1. Base styles (Desktop): No media query
2. Tablet: @media (max-width: 1024px)
3. Large Phone: @media (max-width: 768px)
4. Small Phone: @media (max-width: 480px)
5. Landscape: @media (max-height: 500px) and (orientation: landscape)
```

---

## Message Types Styling

### User Messages
```
┌──────────────────────┐
│ Hey! How are you?   │ Sent
│        11:30 PM  →  │
└──────────────────────┘
  → Right-aligned
  → Purple gradient background
  → Glow effect
```

### Stranger Messages
```
┌──────────────────────┐
│ ← I'm good, thanks!  │ Received
│   11:31 PM           │
└──────────────────────┘
  → Left-aligned
  → Dark background
  → Subtle border
```

### System Messages
```
┌────────────────────────────┐
│ ⚡ Connected to stranger.  │
│    Start chatting.         │
└────────────────────────────┘
  → Center-aligned
  → Purple accent color
  → Glass morphism effect
  → Fade-in animation
```

---

## Safe Area Insets (Notched Phones)

```css
padding-bottom: max(12px, env(safe-area-inset-bottom));
```

Applied to:
- Input bar
- Auth card
- Bottom navigation elements

Ensures content doesn't go under:
- iPhone notch
- Android gesture bars
- Rounded corners

---

## Font Size Scaling

| Element | Desktop | Tablet | Phone | Reason |
|---------|---------|--------|-------|--------|
| Chat partner name | 1.2rem | 1.2rem | 1.0rem | Readability |
| Messages | 1rem | 0.95rem | 0.95rem | Space efficiency |
| System messages | 0.85rem | 0.8rem | 0.8rem | Less intrusive |
| Stat labels | 0.7rem | 0.7rem | 0.7rem | Compact info |
| Stat values | 0.85rem | 0.75rem | 0.75rem | Critical data |
| Buttons | 0.9rem | 0.9rem | 0.85rem | Touch clarity |

---

## Performance Optimizations

### CSS
- Hardware-accelerated transforms
- `will-change` for animations
- Minimal repaints
- Efficient selectors

### JavaScript
- Event delegation
- Debounced window resize
- Lazy map initialization
- Batch DOM updates

### Network
- WebSocket for real-time
- WebRTC for P2P (when human)
- Minimal API calls
- Efficient polling

---

## Browser Compatibility

### ✅ Fully Supported:
- Chrome 90+ (Desktop & Mobile)
- Safari 14+ (Desktop & Mobile)
- Firefox 88+ (Desktop & Mobile)
- Edge 90+
- Samsung Internet 14+

### ⚠️ Partial Support:
- IE 11: No support (deprecated)
- Old Android (< 5.0): Limited

### Features Used:
- CSS Grid & Flexbox ✅
- CSS Custom Properties ✅
- WebSocket API ✅
- WebRTC API ✅
- Geolocation API ✅
- ES6+ JavaScript ✅

---

## Accessibility (A11y)

### WCAG 2.1 Compliance:

**Level AA:**
- ✅ Touch targets: 44px minimum
- ✅ Color contrast: 4.5:1 minimum
- ✅ Focus indicators: Visible
- ✅ Text scaling: Up to 200%
- ✅ Keyboard navigation: Full support

**Level AAA:**
- ✅ Color contrast: 7:1 (where possible)
- ✅ No time limits on reading
- ✅ Clear focus order

---

## Dark Mode Support

```css
:root {
    --bg: #05060a;           /* Deep black */
    --panel: rgba(20,22,32,0.95); /* Dark glass */
    --accent: #6c5ce7;       /* Purple */
    --text: #ffffff;          /* White */
    --text-dim: #a0a0b0;     /* Gray */
    --danger: #ff5e57;       /* Red */
    --glass: rgba(255,255,255,0.03); /* Subtle */
    --glass-border: rgba(255,255,255,0.1); /* Borders */
}
```

All colors are optimized for:
- OLED displays (true black)
- Eye comfort (low brightness)
- Modern aesthetics
- Accessibility contrast

---

## Testing Matrix

| Device | Screen Size | Orientation | Status |
|--------|-------------|-------------|--------|
| iPhone 14 Pro | 393×852 | Portrait | ✅ Perfect |
| iPhone 14 Pro | 852×393 | Landscape | ✅ Perfect |
| iPhone SE | 375×667 | Portrait | ✅ Perfect |
| iPad Pro | 1024×1366 | Portrait | ✅ Perfect |
| iPad Pro | 1366×1024 | Landscape | ✅ Perfect |
| Galaxy S21 | 360×800 | Portrait | ✅ Perfect |
| Pixel 6 | 412×915 | Portrait | ✅ Perfect |
| Desktop | 1920×1080 | N/A | ✅ Perfect |

---

**All responsive designs tested and verified!** ✅
